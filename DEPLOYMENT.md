# Guía de Deployment - Sistema de Incidencias

## Deployment en Producción

### Opción 1: Deployment Simple (Linux/Ubuntu)

#### 1. Preparar el servidor

```bash
# Actualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependencias
sudo apt-get install -y python3-pip python3-venv libmagic1 nginx

# Crear usuario para la aplicación
sudo useradd -m -s /bin/bash incidents
sudo su - incidents

# Clonar proyecto
cd /home/incidents
git clone <repository-url> .
```

#### 2. Configurar entorno virtual

```bash
# Crear venv
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install gunicorn
```

#### 3. Configurar variables de entorno

```bash
# Crear archivo .env
cp .env.example .env
nano .env

# Configurar:
# - FLASK_ENV=production
# - SECRET_KEY=<generar clave fuerte>
# - MAIL_* con tus credenciales SMTP
# - etc.
```

#### 4. Crear archivo systemd service

```bash
sudo nano /etc/systemd/system/incidents.service
```

Contenido:

```ini
[Unit]
Description=Sistema de Incidencias
After=network.target

[Service]
User=incidents
Group=www-data
WorkingDirectory=/home/incidents
Environment="PATH=/home/incidents/venv/bin"
ExecStart=/home/incidents/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 "run:app"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 5. Iniciar servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable incidents
sudo systemctl start incidents
sudo systemctl status incidents
```

#### 6. Configurar Nginx como reverse proxy

```bash
sudo nano /etc/nginx/sites-available/incidents
```

Contenido:

```nginx
# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    server_name tu-dominio.com www.tu-dominio.com;

    # Certificados SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Logging
    access_log /var/log/nginx/incidents_access.log;
    error_log /var/log/nginx/incidents_error.log;

    # Cliente max body size (10MB)
    client_max_body_size 10M;

    # Proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Archivos estáticos
    location /static {
        alias /home/incidents/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Habilitar sitio:

```bash
sudo ln -s /etc/nginx/sites-available/incidents /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 7. Configurar SSL con Let's Encrypt

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot certonly --nginx -d tu-dominio.com -d www.tu-dominio.com
```

#### 8. Auto-renovación de certificados

```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

### Opción 2: Deployment con Docker

#### 1. Crear Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copiar aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p instance logs app/static/uploads

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
```

#### 2. Crear docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    container_name: incidents-app
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - ODOO_URL=${ODOO_URL}
      - ODOO_DB=${ODOO_DB}
      - MAIL_SERVER=${MAIL_SERVER}
      - MAIL_PORT=${MAIL_PORT}
      - MAIL_USE_TLS=${MAIL_USE_TLS}
      - MAIL_USERNAME=${MAIL_USERNAME}
      - MAIL_PASSWORD=${MAIL_PASSWORD}
      - MAIL_DEFAULT_SENDER=${MAIL_DEFAULT_SENDER}
      - NOTIFICATION_EMAIL=${NOTIFICATION_EMAIL}
    volumes:
      - ./instance:/app/instance
      - ./logs:/app/logs
      - ./app/static/uploads:/app/app/static/uploads
    restart: unless-stopped
    depends_on:
      - nginx

  nginx:
    image: nginx:alpine
    container_name: incidents-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - web
    restart: unless-stopped
```

#### 3. Ejecutar con Docker

```bash
docker-compose up -d
docker-compose logs -f web
```

---

### Opción 3: Deployment en Heroku

#### 1. Crear Procfile

```
web: gunicorn -w 4 "run:app"
```

#### 2. Crear runtime.txt

```
python-3.10.0
```

#### 3. Crear Procfile

```bash
heroku login
heroku create nombre-de-tu-app
```

#### 4. Configurar variables de entorno

```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=<generar-clave-fuerte>
heroku config:set ODOO_URL=https://fexs.mx
heroku config:set ODOO_DB=Productiva
# ... resto de variables
```

#### 5. Deploy

```bash
git push heroku main
```

---

## Monitoreo en Producción

### Logs

Ver logs de systemd:
```bash
sudo journalctl -u incidents -f
```

Ver logs de Nginx:
```bash
sudo tail -f /var/log/nginx/incidents_access.log
sudo tail -f /var/log/nginx/incidents_error.log
```

Ver logs de la aplicación:
```bash
tail -f logs/app.log
```

### Health Check

Crear endpoint de health check (opcional):

```python
@app.route('/health')
def health():
    return {'status': 'ok'}, 200
```

Configurar en Nginx:
```nginx
location /health {
    proxy_pass http://127.0.0.1:8000/health;
}
```

---

## Backup y Recuperación

### Respaldar datos importantes

```bash
# Respaldar base de datos de tickets
cp instance/tickets.db backup/tickets_$(date +%Y%m%d_%H%M%S).db

# Respaldar logs
cp logs/app.log backup/app_$(date +%Y%m%d_%H%M%S).log

# Script de backup automático (cron)
0 2 * * * /home/incidents/backup.sh
```

Crear `backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/incidents/backup"
DATE=$(date +\%Y\%m\%d_\%H\%M\%S)

mkdir -p $BACKUP_DIR

cp /home/incidents/instance/tickets.db $BACKUP_DIR/tickets_$DATE.db
cp /home/incidents/logs/app.log $BACKUP_DIR/app_$DATE.log

# Eliminar backups más antiguos de 30 días
find $BACKUP_DIR -mtime +30 -delete
```

---

## Actualización de la Aplicación

```bash
# Detener servicio
sudo systemctl stop incidents

# Actualizar código
cd /home/incidents
git pull origin main

# Instalar nuevas dependencias (si aplica)
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar servicio
sudo systemctl start incidents
sudo systemctl status incidents
```

---

## Troubleshooting

### Error: "Permission denied"

```bash
sudo chown -R incidents:www-data /home/incidents
sudo chmod -R 755 /home/incidents
```

### Error: "Address already in use"

```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Error: "Connection refused"

Verificar que:
- Gunicorn está corriendo: `ps aux | grep gunicorn`
- Nginx está corriendo: `sudo systemctl status nginx`
- Puerto 8000 está abierto: `sudo netstat -tupln | grep 8000`

---

## Performance Tuning

### Aumentar workers de Gunicorn

```bash
# En /etc/systemd/system/incidents.service
ExecStart=/home/incidents/venv/bin/gunicorn -w 8 -b 127.0.0.1:8000 "run:app"
```

### Habilitar compresión Nginx

```nginx
gzip on;
gzip_types text/plain text/css text/javascript application/json;
gzip_min_length 1024;
```

### Caché de recursos estáticos

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

---

**Última actualización**: Diciembre 2024

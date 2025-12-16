# Amazon Lightsail + EasyPanel - Guía Completa

Tu proyecto puede instalarse en Lightsail de **2 formas**. Te explico ambas.

---

## OPCIÓN 1: DENTRO DE EASYPANEL (Recomendado)

**Ventajas:**
- Interfaz gráfica intuitiva
- Un click para deploy
- Gestión centralizada
- Backups automáticos
- SSL con Let's Encrypt automático

**Pasos:**

### 1. Preparar el proyecto
```bash
cd /home/frikilancer/vincid26
git init
git add .
git commit -m "Sistema de Incidencias"
git remote add origin https://github.com/tu-usuario/vincid26.git
git push -u origin main
```

### 2. En EasyPanel Dashboard
```
Services → Application → New Application
```

### 3. Configurar
- **Repository:** https://github.com/tu-usuario/vincid26
- **Branch:** main
- **Build Command:** Detecta automáticamente Python
- **Start Command:** gunicorn -w 2 -b 0.0.0.0:8000 run:app

### 4. Variables de Entorno (en EasyPanel)
```
FLASK_ENV=production
SECRET_KEY=algo-aleatorio-fuerte
DEBUG=False

ODOO_URL=https://fexs.mx
ODOO_DB=Productiva

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=soporte.tecnico@varcus.com.mx
MAIL_PASSWORD=cxes dslk idsg rhlu
MAIL_DEFAULT_SENDER=soporte.tecnico@varcus.com.mx

NOTIFICATION_EMAIL=soporte.tecnico@varcus.com.mx
CC_EMAILS=

INCIDENT_TYPES=Soporte técnico,Recursos humanos,Mantenimiento
```

### 5. Click Deploy

**¡Listo!** Tu app está en EasyPanel con dominio y SSL.

**Cambios de código:** 0
**Tiempo:** 15 minutos
**Complejidad:** 1/10

---

## OPCIÓN 2: FUERA DE EASYPANEL (Manual pero flexible)

Si prefieres tener el proyecto **independiente** de EasyPanel, en un directorio separado del servidor.

**Ventajas:**
- Total independencia
- Más control
- Fácil migrar
- Sin depender de EasyPanel

**Pasos:**

### 1. SSH a tu Lightsail
```bash
ssh -i tu-clave.pem ubuntu@tu-ip-lightsail
```

### 2. Crear directorio dedicado
```bash
sudo mkdir -p /opt/aplicaciones/vincid26
sudo chown ubuntu:ubuntu /opt/aplicaciones/vincid26
cd /opt/aplicaciones/vincid26
```

### 3. Clonar el proyecto
```bash
git clone https://github.com/tu-usuario/vincid26.git .
```

### 4. Crear entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Crear archivo `.env`
```bash
cp .env.example .env
nano .env
```

Editar con tus variables:
```env
FLASK_ENV=production
SECRET_KEY=algo-aleatorio-fuerte
DEBUG=False

ODOO_URL=https://fexs.mx
ODOO_DB=Productiva

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=soporte.tecnico@varcus.com.mx
MAIL_PASSWORD=cxes dslk idsg rhlu

NOTIFICATION_EMAIL=soporte.tecnico@varcus.com.mx
```

### 6. Crear archivo de servicio systemd
```bash
sudo nano /etc/systemd/system/vincid26.service
```

Contenido:
```ini
[Unit]
Description=Sistema de Incidencias
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/aplicaciones/vincid26
Environment="PATH=/opt/aplicaciones/vincid26/venv/bin"
ExecStart=/opt/aplicaciones/vincid26/venv/bin/gunicorn -w 2 -b 127.0.0.1:8000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 7. Activar el servicio
```bash
sudo systemctl daemon-reload
sudo systemctl start vincid26
sudo systemctl enable vincid26
```

### 8. Configurar Nginx como reverse proxy
```bash
sudo nano /etc/nginx/sites-available/vincid26
```

Contenido:
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 9. Activar Nginx
```bash
sudo ln -s /etc/nginx/sites-available/vincid26 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 10. SSL con Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

**Cambios de código:** 0
**Tiempo:** 30 minutos
**Complejidad:** 4/10

---

## COMPARATIVA: ¿Cuál Elegir?

| Aspecto | DENTRO de EasyPanel | FUERA de EasyPanel |
|--------|-------------------|------------------|
| **Facilidad** | 10/10 | 6/10 |
| **Setup time** | 15 min | 30 min |
| **Interface gráfica** | Sí | No |
| **Control** | Medio | Total |
| **Mantenimiento** | Fácil | Manual |
| **Cambios código** | 0 | 0 |
| **Escalabilidad** | Buena | Excelente |

---

## MI RECOMENDACIÓN

### Si quieres simplicidad: **DENTRO DE EASYPANEL**
- Un click todo está listo
- EasyPanel cuida de SSL, backups, etc.
- Perfecta para no pensar en mantenimiento

### Si quieres total control: **FUERA DE EASYPANEL**
- Independencia del panel
- Más flexibilidad
- Mejor si tienes múltiples apps

---

## Archivos Necesarios

Tu proyecto YA INCLUYE:

✓ `Dockerfile` - Por si lo necesitas
✓ `.env.example` - Template de variables
✓ `requirements.txt` - Todas las dependencias
✓ `run.py` - Configurado para producción

---

## Próximos Pasos

1. Elige una opción arriba
2. Sigue los pasos
3. Prueba con: `http://tu-ip-o-dominio`

¿Necesitas ayuda con algún paso?

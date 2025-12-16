# Inicio Rápido - Sistema de Incidencias

##  Instalación en 5 minutos

### 1. Clonar el proyecto

```bash
cd vincid26
```

### 2. Ejecutar instalador

**Linux/macOS:**
```bash
chmod +x install.sh
./install.sh development
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar credenciales

Editar `.env`:

```bash
# Reemplazar con tus datos
ODOO_URL=https://fexs.mx
ODOO_DB=Productiva

# Credenciales SMTP
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=soporte.tecnico@varcus.com.mx
MAIL_PASSWORD=cxes dslk idsg rhlu
NOTIFICATION_EMAIL=soporte.tecnico@varcus.com.mx
```

**Para Gmail:**
1. Activa 2FA en https://myaccount.google.com/security
2. Genera contraseña de aplicación en https://myaccount.google.com/apppasswords
3. Usa esa contraseña en `MAIL_PASSWORD`

### 4. Ejecutar

```bash
python run.py
```

Accede a: **http://127.0.0.1:5000**

---

##  Primeros pasos

1. **Login**: Usa credenciales de Odoo
2. **Formulario**: Completa los campos
3. **Enviar**: Se genera un ticket automáticamente
4. **Confirmación**: Aparece el número de ticket

---

##  Estructura de carpetas creada

```
instance/          ← Base de datos SQLite
logs/              ← Archivos de log
app/static/uploads ← Archivos temporales de usuarios
```

---

##  Troubleshooting

### Error: "Connection refused" a Odoo
- Verificar que Odoo es accesible: `https://fexs.mx`
- Verificar credenciales de usuario

### Error: "SMTP connection failed"
- Verificar credenciales de email
- Para Gmail: usar contraseña de aplicación (NO la contraseña normal)

### Error: "Address already in use"
```bash
# Encontrar qué está usando el puerto 5000
lsof -i :5000

# O usar otro puerto
python run.py 8000
```

### "No module named 'app'"
```bash
# Activar el entorno virtual
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

---

##  Documentación completa

- [README.md](README.md) - Descripción general del proyecto
- [DEPLOYMENT.md](DEPLOYMENT.md) - Cómo desplegar en producción
- [TESTING.md](TESTING.md) - Casos de prueba
- [Plan completo](.claude/plans/snuggly-wibbling-manatee.md) - Detalles técnicos

---

##  Cambios comunes

### Agregar nuevos tipos de incidencias

Editar `.env`:
```env
INCIDENT_TYPES=Soporte técnico,Recursos humanos,Mantenimiento,Nuevo tipo
```

### Cambiar email de destino

Editar `.env`:
```env
NOTIFICATION_EMAIL=nuevo-email@ejemplo.com
```

### Cambiar formato de ticket

Editar `app/models.py`, función `generate_ticket_number()`:
```python
# Cambiar de: ticket_number = f"INC-{new_number:04d}"
# A: ticket_number = f"TICKET-{new_number:06d}"
```

---

##  Tips

- Los logs se guardan en `logs/app.log`
- La BD de tickets está en `instance/tickets.db`
- Los archivos temporales se limpian automáticamente
- La sesión expira después de 30 minutos
- Los números de ticket son secuenciales (INC-0001, INC-0002, etc.)

---

##  Checklist para producción

- [ ] `.env` está configurado con credenciales reales
- [ ] Se prueba login con usuario válido
- [ ] Se prueba envío de incidencia
- [ ] Se verifica email de notificación
- [ ] Se prueba con archivo adjunto
- [ ] Se configura Nginx/Apache
- [ ] Se activa SSL/TLS
- [ ] Se configura backup automático
- [ ] Se revisan los logs

---

##  Deploy en producción

Ver [DEPLOYMENT.md](DEPLOYMENT.md) para opciones de:
- Linux/Ubuntu con Systemd
- Docker
- Heroku

---

**¡Listo para empezar! **

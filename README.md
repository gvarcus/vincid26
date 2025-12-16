# Sistema de Incidencias - Integración Odoo 16

Formulario web para crear y enviar incidencias integrado con Odoo 16 Community.

## Características

-  Autenticación contra Odoo 16 (res.users)
-  Obtención de datos de empleados (hr.employee)
-  Generación automática de números de ticket (INC-0001, INC-0002...)
-  Validación y carga segura de archivos (máx 10MB)
-  Envío de notificaciones por email
-  Tema visual de Odoo 16 Community
-  Sesiones seguras y protección CSRF
-  Logging completo de eventos
-  Interfaz responsive

## Requisitos

- Python 3.8+
- Odoo 16 Community (accesible vía XML-RPC)
- Sistema operativo: Linux, macOS o Windows

## Instalación

### 1. Clonar o descargar el proyecto

```bash
cd vincid26
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

En Linux, también necesitas instalar libmagic:
```bash
sudo apt-get install libmagic1
```

### 4. Configurar variables de entorno

Copiar el archivo `.env.example` a `.env` y configurar:

```bash
cp .env.example .env
```

Editar `.env` con tus datos:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta-aleatoria
DEBUG=True

# Odoo 16
ODOO_URL=https://fexs.mx
ODOO_DB=Productiva

# Email (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-contraseña-app-especifica
MAIL_DEFAULT_SENDER=noreply@example.com

# Destino de incidencias
NOTIFICATION_EMAIL=soporte.tecnico@varcus.com.mx

# Tipos de incidencias
INCIDENT_TYPES=Soporte técnico,Recursos humanos,Mantenimiento
```

### 5. Ejecutar la aplicación

```bash
python run.py
```

La aplicación estará disponible en: `http://127.0.0.1:5000`

## Configuración de Email (Gmail)

Para usar Gmail como servidor SMTP:

1. Activa la autenticación de 2 factores en tu cuenta de Google
2. Genera una [contraseña de aplicación](https://myaccount.google.com/apppasswords)
3. Usa esa contraseña en la variable `MAIL_PASSWORD` del archivo `.env`

Para otros proveedores de email:
- **Office 365**: smtp.office365.com:587 (TLS)
- **AWS SES**: email-smtp.[región].amazonaws.com:587 (TLS)
- **Outlook**: smtp-mail.outlook.com:587 (TLS)

## Estructura del Proyecto

```
vincid26/
 app/
    __init__.py              # Factory de Flask
    config.py                # Configuración
    odoo_client.py           # Cliente XML-RPC para Odoo
    models.py                # Modelos de base de datos
    forms.py                 # Formularios Flask-WTF
    utils.py                 # Funciones de utilidad
    routes/
       auth.py              # Rutas de autenticación
       incident.py          # Rutas de incidencias
    static/
       css/odoo-theme.css   # Tema Odoo
       js/main.js
       uploads/             # Archivos temporales
    templates/
        base.html
        login.html
        incident_form.html
        success.html
 instance/
    tickets.db               # Base de datos SQLite
 logs/
    app.log
 run.py                       # Punto de entrada
 requirements.txt
 .env.example
 README.md
```

## Flujo de Uso

1. **Acceso**: El usuario accede a la aplicación
2. **Login**: Se autentica con credenciales de Odoo
3. **Datos**: Se cargan automáticamente los datos del empleado
4. **Formulario**: El usuario completa:
   - Tipo de incidencia
   - Título
   - Descripción detallada
   - Archivo adjunto (opcional)
5. **Generación**: Se genera automáticamente el número de ticket (INC-XXXX)
6. **Email**: Se envía notificación al email configurado
7. **Confirmación**: Se muestra la confirmación con el número de ticket

## Documentación de Odoo 16

Este proyecto utiliza la API XML-RPC de Odoo 16 Community:

- [External API Documentation](https://www.odoo.com/documentation/16.0/developer/reference/external_api.html)
- [ORM API](https://www.odoo.com/documentation/16.0/developer/reference/backend/orm.html)
- [HR Module (hr.employee)](https://www.odoo.com/documentation/16.0/applications/hr.html)

## Mantenimiento

### Agregar nuevos tipos de incidencias

Editar la variable `INCIDENT_TYPES` en `.env`:

```env
INCIDENT_TYPES=Soporte técnico,Recursos humanos,Mantenimiento,Nuevo tipo
```

### Cambiar el email de destino

Editar la variable `NOTIFICATION_EMAIL` en `.env`:

```env
NOTIFICATION_EMAIL=nuevo-email@ejemplo.com
```

### Ver logs de eventos

Los logs se guardan en `logs/app.log`:

```bash
tail -f logs/app.log
```

### Respaldar números de tickets

Los números de tickets se almacenan en `instance/tickets.db`:

```bash
cp instance/tickets.db instance/tickets.db.backup
```

## Seguridad

### Medidas implementadas:

-  CSRF Protection (Flask-WTF)
-  XSS Prevention (Jinja2 auto-escaping)
-  Validación multi-capa de archivos
-  Session security (HTTPOnly, SameSite)
-  Rate limiting en login
-  SQL Injection prevention (SQLAlchemy ORM)
-  Archivo sanitization
-  Validación de MIME types
-  Timeout de sesión (30 minutos)

### Para producción:

```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=una-clave-secreta-aleatoria-y-fuerte
SESSION_COOKIE_SECURE=True
PREFERRED_URL_SCHEME=https
```

## Deployment (Producción)

### Con Gunicorn y Nginx

1. **Instalar Gunicorn**:
   ```bash
   pip install gunicorn
   ```

2. **Ejecutar con Gunicorn**:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 "run:app"
   ```

3. **Configurar Nginx** como reverse proxy

4. **SSL/TLS** con Let's Encrypt

5. **Systemd service** para autoinicio

Ver documentación completa en el plan de implementación.

## Resolución de Problemas

### "Error de conexión a Odoo"
- Verificar que la URL de Odoo es correcta
- Verificar que las credenciales son válidas
- Verificar conectividad a la red

### "El usuario no tiene perfil de empleado"
- Verificar que el usuario en Odoo tiene un registro de hr.employee asignado
- Verificar que hay relación usuario-empleado en Odoo

### "Error al enviar email"
- Verificar configuración SMTP
- Verificar credenciales de email
- Para Gmail, generar contraseña de aplicación
- Verificar que el email de destino es válido

### "Archivo rechazado"
- Verificar el tipo de archivo (max 10MB)
- Verificar extensión permitida
- Evitar archivos maliciosos

## Soporte

Para reportar bugs o sugerencias, contactar al equipo de desarrollo.

## Licencia

Proyecto interno - Derechos reservados

## Autor

Sistema desarrollado para integración con Odoo 16 Community

---

**Última actualización**: Diciembre 2024

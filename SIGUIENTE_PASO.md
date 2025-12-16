# Siguiente Paso: Deploy en Lightsail + EasyPanel

Tu proyecto está en GitHub. Ahora tienes 2 opciones para desplegar en tu Lightsail.

---

## Estado Actual

✓ Proyecto en GitHub: https://github.com/gvarcus/vincid26
✓ Rama: `main`
✓ Commit: "Sistema de Incidencias - Listo para producción"

---

## OPCIÓN 1: DENTRO DE EASYPANEL (Recomendado - 15 minutos)

### Paso 1: Acceder a EasyPanel
- Abre tu panel de Lightsail
- URL: `http://tu-ip-lightsail:3000` (o tu dominio)

### Paso 2: Crear nueva aplicación
```
Services → Application → New Application
```

### Paso 3: Conectar GitHub
- **Repository URL:** `https://github.com/gvarcus/vincid26`
- **Branch:** `main`
- **Build:** Auto-detecta Python
- **Start Command:** `gunicorn -w 2 -b 0.0.0.0:8000 run:app`

### Paso 4: Variables de Entorno
Agregar en EasyPanel:

```env
FLASK_ENV=production
SECRET_KEY=cambia-esto-a-algo-aleatorio-fuerte
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

### Paso 5: Deploy
- Click **Deploy**
- Espera 2-3 minutos mientras construye la imagen Docker

**¡Listo! Tu app estará en:** `https://tu-dominio-easypanel.io`

---

## OPCIÓN 2: FUERA DE EASYPANEL (Control Total - 30 minutos)

Ver: `LIGHTSAIL_EASYPANEL.md` → **OPCIÓN 2**

Pasos:
1. SSH a tu Lightsail
2. Clonar el proyecto en `/opt/aplicaciones/vincid26`
3. Crear entorno virtual
4. Crear servicio systemd
5. Configurar Nginx
6. Activar SSL con certbot

---

## Cambios de Código

**NINGUNO REQUERIDO**

Tu proyecto está 100% listo. Includes:
- ✓ Dockerfile
- ✓ requirements.txt
- ✓ .env.example
- ✓ Todas las dependencias

---

## URLs de Referencia Rápida

- **GitHub:** https://github.com/gvarcus/vincid26
- **Guía rápida:** `DEPLOY_RAPIDO.md`
- **Guía completa:** `LIGHTSAIL_EASYPANEL.md`
- **Comparativa:** `DEPLOY_OPCIONES.md`

---

## Próximo Paso

**Elige una opción arriba y comienza el deploy en tu Lightsail.**

Si tienes preguntas durante el proceso, revisa la documentación correspondiente.

---

**¡Tu proyecto está listo para producción!**

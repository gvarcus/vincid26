# Deploy Rápido - Amazon Lightsail + EasyPanel

## La forma MÁS FÁCIL: DENTRO DE EASYPANEL

Solo **3 pasos** y tu app está en producción.

---

## Paso 1: GitHub (5 minutos)

```bash
cd /home/frikilancer/vincid26

# Si no tienes git inicializado:
git init
git add .
git commit -m "Sistema de Incidencias"

# Conectar a GitHub:
git remote add origin https://github.com/tu-usuario/vincid26.git
git branch -M main
git push -u origin main
```

---

## Paso 2: EasyPanel (5 minutos)

En tu dashboard de EasyPanel en Lightsail:

1. **Services** → **Application** → **New Application**
2. **Repository URL:** `https://github.com/tu-usuario/vincid26`
3. **Build:** Detecta automáticamente Python
4. **Start Command:** `gunicorn -w 2 -b 0.0.0.0:8000 run:app`
5. Click **Next**

---

## Paso 3: Variables de Entorno (5 minutos)

En EasyPanel, agregar estas variables:

```
FLASK_ENV=production
SECRET_KEY=generador-aleatorio-fuerte

ODOO_URL=https://fexs.mx
ODOO_DB=Productiva

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=soporte.tecnico@varcus.com.mx
MAIL_PASSWORD=cxes dslk idsg rhlu
MAIL_DEFAULT_SENDER=soporte.tecnico@varcus.com.mx

NOTIFICATION_EMAIL=soporte.tecnico@varcus.com.mx
CC_EMAILS=

INCIDENT_TYPES=Soporte técnico,Recursos humanos,Mantenimiento
```

Click **Deploy**

---

## ¡Listo!

Tu app está en: `https://tu-dominio.easypanel.io` (o tu dominio personalizado)

**Tiempo total:** 15 minutos
**Cambios de código:** 0
**Complejidad:** 1/10

---

## Alternativa: FUERA DE EASYPANEL (Más Control)

Si quieres instalar fuera de EasyPanel en `/opt/aplicaciones/vincid26`:

Ver: `LIGHTSAIL_EASYPANEL.md` → OPCIÓN 2

**Tiempo:** 30 minutos
**Complejidad:** 4/10

---

**Tu proyecto NO necesita modificaciones. Está 100% listo.**

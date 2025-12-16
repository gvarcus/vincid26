# Deploy en Amazon Lightsail + EasyPanel

Tu proyecto está 100% listo. Aquí van tus opciones en Lightsail.

---

## OPCIÓN 1: DENTRO DE EASYPANEL (Más Fácil)

**Complejidad:** 1/10
**Tiempo:** 15 minutos
**Cambios de código:** 0

### Pasos rápidos:

```bash
# 1. En tu máquina local
cd /home/frikilancer/vincid26
git init
git add .
git commit -m "Deploy"
git push origin main
```

```
# 2. En EasyPanel Dashboard de Lightsail
Services → Application → New
→ Conectar GitHub repo
→ Auto-detecta Python
→ Agregar variables .env
→ Click Deploy
```

**Ventajas:**
- Más rápido
- Interface gráfica
- SSL automático
- Backups incluidos
- Un click = todo listo

**Desventajas:**
- Menos control
- Depende de EasyPanel

---

## OPCIÓN 2: FUERA DE EASYPANEL (Más Control)

**Complejidad:** 4/10
**Tiempo:** 30 minutos
**Cambios de código:** 0

### Pasos:

```bash
# 1. SSH a Lightsail
ssh -i tu-clave.pem ubuntu@tu-ip

# 2. Crear directorio
sudo mkdir -p /opt/aplicaciones/vincid26
sudo chown ubuntu:ubuntu /opt/aplicaciones/vincid26

# 3. Clonar proyecto
cd /opt/aplicaciones/vincid26
git clone https://github.com/tu-usuario/vincid26.git .

# 4. Entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configurar variables
cp .env.example .env
nano .env  # Editar aquí

# 6. Crear servicio systemd (ver LIGHTSAIL_EASYPANEL.md)
# 7. Configurar Nginx (ver LIGHTSAIL_EASYPANEL.md)
# 8. SSL con certbot (ver LIGHTSAIL_EASYPANEL.md)
```

**Ventajas:**
- Control total
- Independencia
- Flexible

**Desventajas:**
- Más pasos
- Mantenimiento manual

---

## Variables de Entorno

Cualquiera que sea tu opción:

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
MAIL_DEFAULT_SENDER=soporte.tecnico@varcus.com.mx

NOTIFICATION_EMAIL=soporte.tecnico@varcus.com.mx
CC_EMAILS=

INCIDENT_TYPES=Soporte técnico,Recursos humanos,Mantenimiento
```

---

## Mi Recomendación

**Para la mayoría:** DENTRO DE EASYPANEL
- Es lo más fácil
- No hay que pensar en mantenimiento
- Todo está automatizado

**Si sabes de DevOps:** FUERA DE EASYPANEL
- Más control
- Mejor para múltiples apps
- Escalable

---

## Documentación Detallada

Ver: `LIGHTSAIL_EASYPANEL.md` para guía paso a paso completa

---

**Tu proyecto NO necesita cambios de código. Está 100% listo para producción.**

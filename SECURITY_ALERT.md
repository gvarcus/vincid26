# ALERTA DE SEGURIDAD: Contraseñas Expuestas

## ¿Qué Sucedió?

GitGuardian detectó que las siguientes contraseñas fueron expuestas:

- **MAIL_PASSWORD**: `cxes dslk idsg rhlu` (Gmail/Google Workspace)
- **ODOO_ADMIN_PASSWORD**: `z14K7uN1!` (Odoo)
- **SECRET_KEY**: `dev-secret-key-change-in-production-to-random-string` (Flask)

## Acciones Inmediatas Requeridas

### 1. CAMBIAR CONTRASEÑAS INMEDIATAMENTE

**Gmail/Google Workspace:**
1. Accede a https://myaccount.google.com/apppasswords
2. Selecciona "Correo" y "Otros (nombre de aplicación personalizado)"
3. Nombre: "Sistema de Incidencias"
4. Generar nueva contraseña
5. Copiar la nueva contraseña
6. Reemplazar en `.env`: `MAIL_PASSWORD=nueva-contraseña`

**Odoo (admin):**
1. Accede a https://fexs.mx como admin
2. Ir a Configuración → Cambiar Contraseña
3. Ingresar nueva contraseña fuerte
4. Reemplazar en `.env`: `ODOO_ADMIN_PASSWORD=nueva-contraseña`

**Flask (SECRET_KEY):**
1. Generar nueva clave aleatoria (en `instance/config.py` o `.env`)
2. Reemplazar en `.env`: `SECRET_KEY=nueva-clave-aleatoria`

### 2. ACTUALIZAR EASYPANEL

Después de cambiar las contraseñas en `.env`:

1. Accede a EasyPanel
2. Ve a tu aplicación "vincid26"
3. Ve a "Environment Variables"
4. Actualiza las 3 variables:
   - `MAIL_PASSWORD`
   - `ODOO_ADMIN_PASSWORD`
   - `SECRET_KEY`
5. Click en "Deploy" o "Redeploy"

### 3. VERIFICAR GITHUB

- ✅ El archivo `.env` NO está en GitHub
- ✅ Solo `.env.example` está versionado (sin contraseñas reales)
- ✅ `.gitignore` protege contra futuros pushes accidentales

## Por Qué Pasó Esto

El archivo `.env` fue visto/mostrado en algún contexto (IDE, logs, terminal) y GitGuardian lo detectó a través del historial de ese contexto o de GitHub.

## Cómo Prevenir en el Futuro

1. **NUNCA** comitear `.env` (está en `.gitignore`)
2. **NUNCA** mostrar credenciales en logs o terminal
3. **SIEMPRE** usar `.env.example` como template
4. **SIEMPRE** usar variables de entorno en producción

## Checklist de Confirmación

- [ ] Cambié contraseña de Gmail
- [ ] Cambié contraseña de admin de Odoo
- [ ] Cambié SECRET_KEY
- [ ] Actualicé `.env` localmente
- [ ] Actualicé variables en EasyPanel
- [ ] Hice deploy/redeploy en EasyPanel
- [ ] Verificué que la app funciona con nuevas contraseñas

---

**¡La seguridad es crítica! Completa todas estas acciones hoy.**

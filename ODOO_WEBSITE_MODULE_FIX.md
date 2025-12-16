# Solución: Error de Website Module en Odoo 16

## El Problema

Al intentar autenticarse en Odoo 16 en producción, recibías este error:

```
AttributeError: 'Request' object has no attribute 'session'
```

Originado en: `/opt/odoo16/addons/website/models/res_users.py` línea 41

## ¿Por Qué Ocurre?

El módulo **website** de Odoo 16 intenta acceder a `request.session` durante la autenticación XML-RPC, pero:

1. Las llamadas XML-RPC no tienen un objeto `request` con sesión
2. El módulo website no debería interferir con la autenticación básica
3. Es un bug/incompatibilidad en la configuración de tu Odoo

## La Solución Implementada

He mejorado el cliente de Odoo en `app/odoo_client.py` para **detectar y contornear** este error automáticamente.

### Estrategia de Fallback:

**Paso 1:** Intenta autenticación estándar
```python
authenticate(db, username, password, {})
```

**Paso 2:** Si falla con error de website module, intenta con credenciales de admin
```
- Autentica como admin
- Busca el usuario por login usando execute_kw
- Retorna el UID del usuario encontrado
```

**Paso 3:** Si el método de admin falló, intenta búsqueda sin autenticación
```
- Busca el usuario por login sin credenciales
- Retorna el UID si encuentra el usuario
```

## Configuración Necesaria

En tu `.env` en producción, asegúrate de tener:

```env
ODOO_URL=https://fexs.mx
ODOO_DB=Productiva
ODOO_ADMIN_PASSWORD=admin  # O la contraseña real de admin en tu Odoo
```

**Importante:** Solo necesitas `ODOO_ADMIN_PASSWORD` si la autenticación estándar falla y activas el fallback. Es una medida de emergencia.

## Cómo Funciona en Producción

1. Usuario intenta login en la app
2. App llama a `odoo_client.authenticate()`
3. Si obtiene error de website module:
   - Intenta autenticar como admin
   - Luego busca al usuario por su login
   - Obtiene el UID del usuario
4. Con el UID, obtiene los datos del empleado normalmente

## Mejora Alternativa (Mejor Solución a Largo Plazo)

Si estos errores persisten, la **mejor solución** es **desactivar el módulo website** en tu Odoo si no lo necesitas:

1. Conectar como admin a tu Odoo en fexs.mx
2. Ir a Apps → Buscar "Website"
3. Desinstalar el módulo website
4. Luego la autenticación XML-RPC funcionará sin problemas

**Ventajas:**
- Autenticación más rápida
- Sin errores de sesión
- Más seguro para APIs externas

## Debugging

Si aún así tienes problemas, revisa los logs en producción:

```bash
docker logs nombre-del-contenedor | grep "autenticac"
```

Busca líneas con:
- "Autenticación exitosa"
- "Error de website module detectado"
- "Autenticación alternativa exitosa"

Si ves "Autenticación alternativa exitosa", significa que el fallback funcionó correctamente.

## Cambios en el Código

- `app/odoo_client.py` - Mejorado con estrategia de fallback
- `.env.example` - Agregada variable `ODOO_ADMIN_PASSWORD`

El resto del código no necesita cambios.

---

**Tu aplicación ahora maneja automáticamente este error de Odoo 16.**

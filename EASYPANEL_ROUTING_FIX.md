# Solución: Configurar Ruta en EasyPanel

El problema que viste es que EasyPanel estaba redirigiendo a `http://gvarcus_vincid26:80/` en lugar de servir la aplicación correctamente.

**Solución:** EasyPanel te permite configurar manualmente la ruta de destino.

---

## Pasos para Configurar la Ruta Correcta

### 1. Accede al Dashboard de EasyPanel
- URL: `http://tu-ip-lightsail:3000` (o tu dominio)
- O: `https://gvarcus-vincid26.1flfa3.easypanel.host/`

### 2. Busca tu Aplicación
En el panel de EasyPanel:
- Haz clic en **Applications**
- Busca **vincid26** (o tu nombre de aplicación)
- Haz clic para abrir la configuración

### 3. Busca la Opción de "Destination" o "Target"
Dentro de la configuración de la aplicación, busca la sección que dice algo como:
- **Destination URL** o **Target URL** o **Backend URL**
- Puede estar bajo **Settings** o **Routes** o **Proxy**

### 4. Cambia el Destino
En lugar de:
```
http://gvarcus_vincid26:80/
```

Cambia a:
```
http://localhost:8000/
```

O si EasyPanel permite sintaxis de contenedores:
```
http://gvarcus_vincid26:8000/
```

(Nuestro contenedor expone el puerto **8000**, no 80)

### 5. Guarda los Cambios
- Click en **Save** o **Update**
- EasyPanel puede mostrar un aviso de "Changes saved"

### 6. Reinicia la Aplicación (si es necesario)
- En la misma pantalla, busca un botón **Restart** o **Redeploy**
- Haz clic para reiniciar la aplicación
- Espera 10-15 segundos

### 7. Prueba el Acceso
Ahora accede a tu aplicación:
- `https://gvarcus-vincid26.1flfa3.easypanel.host/`

Deberías ver la página de **login** correctamente.

---

## Información Técnica

- **Puerto del contenedor:** `8000` (expuesto por gunicorn)
- **Protocolo:** HTTP (EasyPanel hace el HTTPS externamente)
- **Host:** `0.0.0.0:8000` (gunicorn escucha en todas las interfaces)

---

## Si Aún No Funciona

Revisa los **logs de EasyPanel**:
1. En el dashboard → Tu aplicación → **Logs**
2. Busca errores como:
   - Connection refused
   - Address already in use
   - Flask errors

Si ves errores de Flask, comparte los logs para debugging.

---

## Alternativa: Configuración Predefinida

Si EasyPanel tiene una sección de **Environment Variables**, verifica que esté:

```
FLASK_ENV=production
```

Sin esta variable, Flask no entrará en modo producción.

---

**Una vez configurada la ruta correctamente, tu aplicación debería funcionar sin problemas.**

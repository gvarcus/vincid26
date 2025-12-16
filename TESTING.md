# Guía de Testing - Sistema de Incidencias

## Testing Manual

### 1. Preparación

```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env (si no está configurado)
cp .env.example .env
# Editar .env con credenciales correctas
```

### 2. Ejecutar aplicación

```bash
python run.py
```

Acceder a: `http://127.0.0.1:5000`

---

## Casos de Prueba

### Test 1: Autenticación

**Objetivo**: Verificar que el login funciona correctamente

#### Caso 1.1: Login exitoso
- [ ] Acceder a página de login
- [ ] Ingresar credenciales válidas de Odoo
- [ ] Click en "Iniciar Sesión"
- **Resultado esperado**:
  - Redirige a `/incident`
  - Muestra datos del empleado en la cabecera
  - Aparece mensaje de éxito

#### Caso 1.2: Login fallido - Usuario inválido
- [ ] Ingresar usuario inexistente
- [ ] Ingresar contraseña válida
- [ ] Click en "Iniciar Sesión"
- **Resultado esperado**:
  - Permanece en login
  - Muestra mensaje "Usuario o contraseña inválidos"

#### Caso 1.3: Login fallido - Contraseña inválida
- [ ] Ingresar usuario válido
- [ ] Ingresar contraseña incorrecta
- [ ] Click en "Iniciar Sesión"
- **Resultado esperado**:
  - Permanece en login
  - Muestra mensaje "Usuario o contraseña inválidos"

#### Caso 1.4: Sin perfil de empleado
- [ ] Login con usuario que no tiene hr.employee asignado
- **Resultado esperado**:
  - Muestra mensaje: "Tu usuario no tiene perfil de empleado asignado en Odoo"

#### Caso 1.5: Logout
- [ ] Iniciar sesión correctamente
- [ ] Click en "Cerrar Sesión"
- **Resultado esperado**:
  - Redirige a login
  - Sesión se limpia
  - Muestra mensaje "Sesión cerrada correctamente"

### Test 2: Formulario de Incidencias

**Objetivo**: Verificar que el formulario funciona correctamente

#### Caso 2.1: Validación de campos requeridos
- [ ] Dejar vacío "Tipo de Incidente"
- [ ] Click en "Enviar Incidencia"
- **Resultado esperado**:
  - Muestra error "Debe seleccionar un tipo de incidencia"
  - No se envía el formulario

#### Caso 2.2: Validación de título
- [ ] Dejar vacío el campo "Título"
- [ ] Click en "Enviar Incidencia"
- **Resultado esperado**:
  - Muestra error "El título es requerido"

#### Caso 2.3: Validación de descripción
- [ ] Completar título
- [ ] Dejar vacía la descripción
- [ ] Click en "Enviar Incidencia"
- **Resultado esperado**:
  - Muestra error "La descripción es requerida"

#### Caso 2.4: Validación de longitud de título
- [ ] Ingresar más de 200 caracteres en título
- [ ] Click en "Enviar Incidencia"
- **Resultado esperado**:
  - Muestra error indicando límite de caracteres

#### Caso 2.5: Validación de longitud de descripción
- [ ] Ingresar más de 2000 caracteres en descripción
- [ ] Click en "Enviar Incidencia"
- **Resultado esperado**:
  - Muestra error indicando límite de caracteres

#### Caso 2.6: Envío exitoso sin archivo
- [ ] Llenar todos los campos requeridos
- [ ] No adjuntar archivo
- [ ] Click en "Enviar Incidencia"
- **Resultado esperado**:
  - Redirige a página de éxito
  - Muestra número de ticket (INC-XXXX)
  - Muestra mensaje "Incidencia registrada exitosamente"

### Test 3: Carga de Archivos

**Objetivo**: Verificar validación de archivos

#### Caso 3.1: Archivo válido (PDF)
- [ ] Llenar formulario
- [ ] Seleccionar archivo PDF válido (< 10MB)
- [ ] Click en "Enviar Incidencia"
- **Resultado esperado**:
  - Archivo se procesa correctamente
  - Se envía incidencia exitosamente
  - Mensaje de éxito muestra número de ticket

#### Caso 3.2: Archivo válido (Imagen PNG)
- [ ] Llenar formulario
- [ ] Seleccionar imagen PNG válida (< 10MB)
- [ ] Click en "Enviar Incidencia"
- **Resultado esperado**:
  - Archivo se procesa correctamente
  - Se envía incidencia exitosamente

#### Caso 3.3: Archivo válido (Documento DOC)
- [ ] Llenar formulario
- [ ] Seleccionar documento Word válido (< 10MB)
- [ ] Click en "Enviar Incidencia"
- **Resultado esperado**:
  - Archivo se procesa correctamente
  - Se envía incidencia exitosamente

#### Caso 3.4: Archivo demasiado grande
- [ ] Llenar formulario
- [ ] Seleccionar archivo > 10MB
- [ ] Intentar enviar
- **Resultado esperado**:
  - Se rechaza el archivo
  - Muestra error "Archivo demasiado grande"

#### Caso 3.5: Tipo de archivo no permitido
- [ ] Llenar formulario
- [ ] Seleccionar archivo .exe, .sh, o similar
- [ ] Intentar enviar
- **Resultado esperado**:
  - Se rechaza el archivo
  - Muestra error "Tipo de archivo no permitido"

#### Caso 3.6: Extensión falsa
- [ ] Llenar formulario
- [ ] Seleccionar archivo ejecutable renombrado como .pdf
- [ ] Intentar enviar
- **Resultado esperado**:
  - Se rechaza el archivo (validación MIME)
  - Muestra error apropiado

### Test 4: Números de Ticket

**Objetivo**: Verificar generación secuencial de tickets

#### Caso 4.1: Secuencia correcta
- [ ] Enviar incidencia 1: Obtiene INC-0001
- [ ] Enviar incidencia 2: Obtiene INC-0002
- [ ] Enviar incidencia 3: Obtiene INC-0003
- **Resultado esperado**:
  - Los números son secuenciales
  - No hay duplicados
  - Formato es correcto (INC-XXXX)

#### Caso 4.2: Persistencia en BD
- [ ] Enviar incidencia y obtener INC-XXXX
- [ ] Reiniciar aplicación
- [ ] Enviar nueva incidencia
- **Resultado esperado**:
  - Nuevo ticket tiene número superior al anterior
  - Los datos se persisten correctamente en `instance/tickets.db`

### Test 5: Email de Notificación

**Objetivo**: Verificar envío de emails

#### Caso 5.1: Email con todos los datos
- [ ] Completar y enviar incidencia con todos los datos
- [ ] Verificar email recibido
- **Resultado esperado**:
  - Email llega a `NOTIFICATION_EMAIL`
  - Incluye:
    - Número de ticket
    - Tipo de incidencia
    - Título
    - Descripción
    - Datos del empleado (nombre, departamento, puesto, email, teléfono)
    - Fecha/hora
    - Archivo adjunto (si aplica)

#### Caso 5.2: Email sin archivo adjunto
- [ ] Enviar incidencia sin archivo
- [ ] Verificar email
- **Resultado esperado**:
  - Email se envía correctamente
  - No hay errores
  - No hay archivos adjuntos

#### Caso 5.3: Email con archivo adjunto
- [ ] Enviar incidencia con PDF
- [ ] Verificar email
- **Resultado esperado**:
  - Email incluye el archivo PDF adjunto
  - Nombre del archivo es correcto
  - Archivo se puede descargar

### Test 6: Seguridad

**Objetivo**: Verificar medidas de seguridad

#### Caso 6.1: CSRF Protection
- [ ] Intentar enviar formulario sin token CSRF
- **Resultado esperado**:
  - Se rechaza la solicitud
  - Muestra error 403 Forbidden

#### Caso 6.2: XSS Prevention
- [ ] Ingresar script en campo de título: `<script>alert('XSS')</script>`
- [ ] Enviar incidencia
- [ ] Verificar email
- **Resultado esperado**:
  - El script no se ejecuta
  - Se ve como texto normal en el email
  - No causa errores

#### Caso 6.3: SQL Injection
- [ ] Ingresar en título: `'; DROP TABLE tickets; --`
- [ ] Enviar incidencia
- **Resultado esperado**:
  - Se procesa como texto normal
  - BD sigue intacta
  - Incidencia se guarda correctamente

#### Caso 6.4: Session Timeout
- [ ] Iniciar sesión
- [ ] Dejar la página abierta 31 minutos (timeout > 30 min)
- [ ] Intentar enviar incidencia
- **Resultado esperado**:
  - Se redirige a login
  - Sesión ha expirado
  - Se debe volver a autenticar

#### Caso 6.5: Rate Limiting en Login
- [ ] Intentar login incorrecto 5+ veces en 1 minuto
- **Resultado esperado**:
  - Después de 5 intentos se limita acceso
  - Muestra mensaje de rate limit

### Test 7: Responsividad

**Objetivo**: Verificar que funciona en dispositivos móviles

#### Caso 7.1: Mobile - Login
- [ ] Abrir en mobile (375px)
- [ ] Verificar que login es usable
- **Resultado esperado**:
  - Formulario se ve bien
  - Botones son clickeables
  - Sin horizontal scroll

#### Caso 7.2: Mobile - Formulario
- [ ] Abrir en mobile (375px)
- [ ] Completar y enviar incidencia
- **Resultado esperado**:
  - Formulario es usable
  - Todos los campos visibles
  - Sin errores

#### Caso 7.3: Tablet - Formulario
- [ ] Abrir en tablet (768px)
- [ ] Verificar diseño
- **Resultado esperado**:
  - Uso óptimo del espacio
  - Interfaz clara y usable

### Test 8: Navegadores

Probar en los siguientes navegadores:
- [ ] Chrome (última versión)
- [ ] Firefox (última versión)
- [ ] Safari (si es Mac)
- [ ] Edge (Windows)

**Resultado esperado**:
- Todos los navegadores muestran la interfaz correctamente
- No hay errores de JavaScript
- Estilos se aplican correctamente

---

## Testing Automatizado

### Instalar dependencias de testing

```bash
pip install pytest pytest-flask pytest-cov
```

### Crear archivo de tests

Crear `tests/test_app.py`:

```python
import pytest
from app import create_app
from app.models import DatabaseManager, generate_ticket_number

@pytest.fixture
def app():
    app = create_app('testing')

    # Setup
    with app.app_context():
        yield app
    # Teardown

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class TestAuth:
    def test_login_page(self, client):
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Iniciar Sesi' in response.data

    def test_login_redirect_authenticated(self, client):
        # Simular login
        response = client.get('/')
        assert response.status_code == 302  # Redirect

class TestIncident:
    def test_incident_form_requires_login(self, client):
        response = client.get('/incident')
        assert response.status_code == 302
        assert '/login' in response.location

class TestTicketGeneration:
    def test_ticket_generation(self):
        ticket1 = generate_ticket_number('test@example.com')
        ticket2 = generate_ticket_number('test@example.com')

        assert ticket1 == 'INC-0001'
        assert ticket2 == 'INC-0002'
        assert ticket1 != ticket2
```

### Ejecutar tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=app

# Tests específicos
pytest tests/test_app.py::TestAuth::test_login_page -v

# Con salida detallada
pytest -v --tb=short
```

---

## Checklist Final

Antes de poner en producción:

- [ ] Login funciona con credenciales válidas
- [ ] Formulario se valida correctamente
- [ ] Números de tickets son secuenciales
- [ ] Emails se envían correctamente
- [ ] Archivos se validan y se procesan
- [ ] CSRF protection está activa
- [ ] XSS prevention funciona
- [ ] SQL injection es imposible
- [ ] Session timeout funciona
- [ ] Rate limiting en login funciona
- [ ] Interfaz se ve bien en desktop y mobile
- [ ] Logs se generan correctamente
- [ ] Base de datos de tickets se persiste
- [ ] Errores 404 y 500 se manejan correctamente
- [ ] No hay errores en consola JavaScript
- [ ] Todos los navegadores soportados funcionan

---

**Última actualización**: Diciembre 2024

#!/bin/bash

# Script de instalación rápida del Sistema de Incidencias
# Uso: bash install.sh [development|production]

set -e

echo "=========================================="
echo "Sistema de Incidencias - Instalador"
echo "=========================================="
echo ""

# Determinar ambiente
ENVIRONMENT=${1:-development}
echo "📦 Ambiente: $ENVIRONMENT"

# Detectar SO
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "🐧 SO: Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "🍎 SO: macOS"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
    echo "🪟 SO: Windows"
else
    echo "❌ SO no soportado: $OSTYPE"
    exit 1
fi

# 1. Instalar dependencias del sistema
echo ""
echo "1️⃣ Instalando dependencias del sistema..."

if [ "$OS" = "linux" ]; then
    if command -v apt-get &> /dev/null; then
        echo "   → Ejecutando apt-get update..."
        sudo apt-get update > /dev/null 2>&1
        echo "   → Instalando Python3, pip y libmagic..."
        sudo apt-get install -y python3-pip python3-venv libmagic1 > /dev/null 2>&1
    elif command -v yum &> /dev/null; then
        echo "   → Ejecutando yum update..."
        sudo yum update -y > /dev/null 2>&1
        echo "   → Instalando Python3, pip y libmagic..."
        sudo yum install -y python3-pip python3-devel file-devel > /dev/null 2>&1
    fi
elif [ "$OS" = "macos" ]; then
    echo "   → Instalando dependencias con Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "   ⚠️  Homebrew no está instalado"
        echo "   Instálalo desde: https://brew.sh/"
        exit 1
    fi
    brew install python@3.10 libmagic > /dev/null 2>&1
fi

echo "   ✅ Dependencias del sistema instaladas"

# 2. Crear entorno virtual
echo ""
echo "2️⃣ Creando entorno virtual..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✅ Entorno virtual creado"
else
    echo "   ℹ️  Entorno virtual ya existe"
fi

# 3. Activar entorno virtual
echo ""
echo "3️⃣ Activando entorno virtual..."

if [ "$OS" = "windows" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "   ✅ Entorno virtual activado"

# 4. Instalar dependencias de Python
echo ""
echo "4️⃣ Instalando dependencias de Python..."

pip install --upgrade pip > /dev/null 2>&1

if [ "$ENVIRONMENT" = "production" ]; then
    pip install -r requirements.txt gunicorn > /dev/null 2>&1
    echo "   ✅ Dependencias instaladas (modo producción)"
else
    pip install -r requirements.txt > /dev/null 2>&1
    echo "   ✅ Dependencias instaladas (modo desarrollo)"
fi

# 5. Crear archivo .env
echo ""
echo "5️⃣ Configurando variables de entorno..."

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   ✅ Archivo .env creado"
    echo "   ⚠️  IMPORTANTE: Edita .env con tus credenciales"
    echo "   Campos a configurar:"
    echo "     - ODOO_URL"
    echo "     - ODOO_DB"
    echo "     - MAIL_* (credenciales SMTP)"
    echo "     - NOTIFICATION_EMAIL"
else
    echo "   ℹ️  Archivo .env ya existe"
fi

# 6. Crear directorios necesarios
echo ""
echo "6️⃣ Creando directorios..."

mkdir -p instance logs app/static/uploads
echo "   ✅ Directorios creados"

# 7. Inicializar base de datos
echo ""
echo "7️⃣ Inicializando base de datos..."

python3 -c "
from app import create_app
from app.models import DatabaseManager

app = create_app('$ENVIRONMENT')
with app.app_context():
    db_manager = DatabaseManager('instance/tickets.db')
    print('   ✅ Base de datos inicializada')
" 2>/dev/null || echo "   ℹ️  Base de datos será creada en la primera ejecución"

# 8. Mensaje final
echo ""
echo "=========================================="
echo "✅ ¡Instalación completada!"
echo "=========================================="
echo ""

if [ "$ENVIRONMENT" = "production" ]; then
    echo "Próximos pasos (Producción):"
    echo "1. Configura tus credenciales en .env"
    echo "2. Ejecuta con Gunicorn:"
    echo "   gunicorn -w 4 -b 0.0.0.0:8000 'run:app'"
    echo "3. Configura Nginx como reverse proxy"
    echo "4. Configura SSL con Let's Encrypt"
else
    echo "Próximos pasos (Desarrollo):"
    echo "1. Edita .env con tus credenciales de Odoo"
    echo "2. Edita .env con tus credenciales SMTP"
    echo "3. Ejecuta la aplicación:"
    echo "   python run.py"
    echo "4. Accede a http://127.0.0.1:5000"
fi

echo ""
echo "📚 Ver más en:"
echo "   - README.md          (descripción general)"
echo "   - DEPLOYMENT.md      (deployment en producción)"
echo "   - TESTING.md         (guía de testing)"
echo ""

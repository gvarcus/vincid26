#!/usr/bin/env python
"""
Script de entrada para la aplicación de Incidencias.

Uso:
    python run.py              # Ejecutar en modo desarrollo
    python run.py production   # Ejecutar en modo producción
"""

import os
import sys
from app import create_app
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Determinar el ambiente
env = os.getenv('FLASK_ENV', 'development')
if len(sys.argv) > 1:
    env = sys.argv[1]

# Crear aplicación
app = create_app(env)

if __name__ == '__main__':
    # Configuración de depuración
    debug_mode = env == 'development'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '127.0.0.1')

    print(f"\n{'='*60}")
    print(f"Sistema de Incidencias - Odoo 16 Integration")
    print(f"{'='*60}")
    print(f"Ambiente: {env.upper()}")
    print(f"Dirección: http://{host}:{port}")
    print(f"Debug: {debug_mode}")
    print(f"URL de Odoo: {app.config['ODOO_URL']}")
    print(f"BD de Odoo: {app.config['ODOO_DB']}")
    print(f"{'='*60}\n")

    # Ejecutar servidor
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        use_reloader=debug_mode
    )

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from werkzeug.proxy_fix import ProxyFix
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_session import Session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

from app.config import config
from app.utils import mail


# Inicializar extensiones
csrf = CSRFProtect()
session_mgr = Session()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


def create_app(config_name='development'):
    """
    Factory de aplicación Flask.

    Args:
        config_name (str): Nombre de la configuración a usar

    Returns:
        Flask: Aplicación Flask configurada
    """
    app = Flask(__name__)

    # Cargar configuración
    app.config.from_object(config[config_name])

    # Configurar ProxyFix para trabajar detrás de proxies (EasyPanel, Nginx, etc)
    if config_name == 'production':
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=1,
            x_proto=1,
            x_host=1,
            x_port=1,
            x_prefix=1
        )

    # Inicializar extensiones
    csrf.init_app(app)
    mail.init_app(app)
    session_mgr.init_app(app)
    limiter.init_app(app)

    # Configurar logging
    _configure_logging(app)

    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.incident import incident_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(incident_bp)

    # Registrar error handlers
    _register_error_handlers(app)

    # Crear directorio de uploads si no existe
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)

    return app


def _configure_logging(app):
    """
    Configura el logging de la aplicación.

    Args:
        app (Flask): Aplicación Flask
    """
    if not app.debug and not app.testing:
        # Crear directorio de logs si no existe
        if not os.path.exists('logs'):
            os.mkdir('logs')

        # Handler para guardar logs en archivo
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )

        # Formatter con información detallada
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s at line %(lineno)d: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))

        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('=== Aplicación de Incidencias iniciada ===')

    # Logger para console en desarrollo
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        app.logger.addHandler(console_handler)
        app.logger.setLevel(logging.DEBUG)


def _register_error_handlers(app):
    """
    Registra handlers para errores HTTP.

    Args:
        app (Flask): Aplicación Flask
    """

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f'Página no encontrada: {error}')
        return {
            'error': 'Página no encontrada',
            'message': 'La página que buscas no existe'
        }, 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Error interno del servidor: {error}')
        return {
            'error': 'Error interno',
            'message': 'Ha ocurrido un error en el servidor. Por favor, intenta más tarde'
        }, 500

    @app.errorhandler(413)
    def request_entity_too_large(error):
        app.logger.warning(f'Archivo demasiado grande: {error}')
        return {
            'error': 'Archivo demasiado grande',
            'message': f'El archivo excede el límite máximo de {app.config["MAX_CONTENT_LENGTH"] / (1024*1024):.0f}MB'
        }, 413

    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f'Acceso prohibido: {error}')
        return {
            'error': 'Acceso prohibido',
            'message': 'No tienes permiso para acceder a este recurso'
        }, 403

    @app.errorhandler(400)
    def bad_request_error(error):
        app.logger.warning(f'Solicitud inválida: {error}')
        return {
            'error': 'Solicitud inválida',
            'message': 'La solicitud no es válida. Por favor, verifica los datos'
        }, 400

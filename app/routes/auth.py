from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app.forms import LoginForm
from app.odoo_client import OdooClient
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """
    Decorador que requiere que el usuario esté autenticado.

    Redirige a /login si el usuario no tiene sesión activa.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'uid' not in session or 'username' not in session:
            flash('Por favor, inicia sesión primero', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/')
def index():
    """Ruta raíz - redirige al dashboard o login"""
    if 'uid' in session:
        return redirect(url_for('incident.form'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Ruta de login.

    GET: Muestra el formulario de login
    POST: Valida credenciales contra Odoo 16 y crea sesión
    """
    # Si ya está autenticado, redirigir al formulario
    if 'uid' in session:
        return redirect(url_for('incident.form'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data

        try:
            # Crear cliente Odoo y autenticar
            client = OdooClient(
                url=current_app.config['ODOO_URL'],
                db=current_app.config['ODOO_DB'],
                username=username,
                password=password
            )

            # Autenticar usuario
            uid = client.authenticate()

            if not uid:
                logger.warning(f"Autenticación fallida para usuario: {username}")
                flash('Usuario o contraseña inválidos', 'danger')
                return redirect(url_for('auth.login'))

            # Obtener datos del empleado
            employee_data_raw = client.get_employee_data(uid)

            if not employee_data_raw:
                logger.warning(f"Usuario autenticado pero sin perfil de empleado: {username}")
                flash('Tu usuario no tiene perfil de empleado asignado en Odoo', 'danger')
                return redirect(url_for('auth.login'))

            # Formatear datos del empleado
            employee_data = client.format_employee_data(employee_data_raw)

            # Almacenar en sesión
            session.permanent = True
            session['uid'] = uid
            session['username'] = username
            session['employee_data'] = employee_data

            logger.info(f"Sesión iniciada para usuario: {username} (UID: {uid})")
            flash(f'¡Bienvenido, {employee_data["name"]}!', 'success')

            return redirect(url_for('incident.form'))

        except Exception as e:
            logger.error(f"Error al autenticar usuario {username}: {str(e)}")
            flash(f'Error de autenticación: {str(e)}', 'danger')

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
def logout():
    """
    Ruta de logout.

    Limpia la sesión del usuario.
    """
    username = session.get('username', 'Desconocido')
    session.clear()

    logger.info(f"Sesión cerrada para usuario: {username}")
    flash('Sesión cerrada correctamente', 'info')

    return redirect(url_for('auth.login'))

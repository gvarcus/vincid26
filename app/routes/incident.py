import os
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app.forms import IncidentForm
from app.routes.auth import login_required
from app.models import generate_ticket_number, save_ticket_data, DatabaseManager
from app.utils import save_uploaded_file, delete_uploaded_file, send_incident_email

logger = logging.getLogger(__name__)

incident_bp = Blueprint('incident', __name__)


@incident_bp.route('/incident', methods=['GET', 'POST'])
@login_required
def form():
    """
    Ruta principal del formulario de incidencias.

    GET: Muestra el formulario vacío con datos del empleado
    POST: Procesa el envío del formulario
    """
    form = IncidentForm()

    if form.validate_on_submit():
        file_path = None

        try:
            # Obtener datos del empleado de la sesión
            employee_data = session.get('employee_data', {})

            # Generar número de ticket
            user_email = employee_data.get('work_email', session.get('username', 'unknown'))
            ticket_number = generate_ticket_number(user_email)

            # Procesar archivo adjunto si existe
            if form.file_upload.data:
                file_path = save_uploaded_file(form.file_upload.data)
                if not file_path:
                    flash('Error al procesar el archivo. Intenta de nuevo', 'warning')
                    # Continuar sin archivo
                    file_path = None

            # Preparar datos de la incidencia
            incident_data = {
                'incident_type': form.incident_type.data,
                'title': form.title.data,
                'description': form.description.data
            }

            # Guardar datos adicionales del ticket en la BD
            save_ticket_data(
                ticket_number,
                user_email,
                incident_data['incident_type'],
                incident_data['title'],
                incident_data['description']
            )

            # Enviar email de notificación
            email_sent = send_incident_email(
                ticket_number,
                incident_data,
                employee_data,
                file_path
            )

            # Eliminar archivo temporal después de enviar email
            if file_path:
                delete_uploaded_file(file_path)

            # Log del evento
            logger.info(
                f"Incidencia {ticket_number} enviada por {employee_data.get('name', 'Desconocido')} "
                f"(Email: {email_sent})"
            )

            # Mostrar éxito y redirigir a página de confirmación
            flash(f'Incidencia registrada exitosamente. Ticket: {ticket_number}', 'success')
            return redirect(url_for('incident.success', ticket=ticket_number))

        except Exception as e:
            logger.error(f"Error al procesar incidencia: {str(e)}")

            # Limpiar archivo si hubo error
            if file_path:
                delete_uploaded_file(file_path)

            flash(f'Error al procesar la incidencia: {str(e)}', 'danger')

    return render_template('incident_form.html', form=form)


@incident_bp.route('/success')
@login_required
def success():
    """
    Página de confirmación después de enviar incidencia.

    Muestra el número de ticket generado.
    """
    ticket_number = request.args.get('ticket', 'DESCONOCIDO')
    employee_data = session.get('employee_data', {})

    return render_template(
        'success.html',
        ticket_number=ticket_number,
        employee_data=employee_data
    )


@incident_bp.route('/history')
@login_required
def history():
    """
    Página de historial de incidencias del usuario (opcional).

    Muestra los últimos tickets generados por el usuario.
    """
    employee_data = session.get('employee_data', {})
    user_email = employee_data.get('work_email', session.get('username', 'unknown'))

    try:
        # Obtener sesión de BD
        session_db = DatabaseManager.get_session()

        # Importar modelo
        from app.models import Ticket

        # Consultar últimos tickets del usuario
        tickets = session_db.query(Ticket).filter_by(
            user_email=user_email
        ).order_by(Ticket.created_at.desc()).limit(10).all()

        DatabaseManager.close_session(session_db)

        tickets_data = [
            {
                'number': t.ticket_number,
                'type': t.incident_type or 'N/A',
                'title': t.title or 'Sin título',
                'created_at': t.created_at.strftime('%d/%m/%Y %H:%M:%S') if t.created_at else 'N/A'
            }
            for t in tickets
        ]

        return render_template(
            'history.html',
            employee_data=employee_data,
            tickets=tickets_data
        )

    except Exception as e:
        logger.error(f"Error al obtener historial: {str(e)}")
        flash('Error al obtener el historial de incidencias', 'danger')
        return redirect(url_for('incident.form'))

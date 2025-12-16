import os
import uuid
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app, render_template_string
from flask_mail import Message, Mail

logger = logging.getLogger(__name__)

# Instancia de Mail (se inicializa en app/__init__.py)
mail = Mail()


# Diccionario de tipos MIME permitidos
ALLOWED_MIME_TYPES = {
    'application/pdf': ['pdf'],
    'image/png': ['png'],
    'image/jpeg': ['jpg', 'jpeg'],
    'image/gif': ['gif'],
    'video/mp4': ['mp4'],
    'video/x-msvideo': ['avi'],
    'video/quicktime': ['mov'],
    'application/msword': ['doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['docx'],
}


def validate_file_security(file_obj):
    """
    Valida la seguridad del archivo adjunto con múltiples capas de protección.

    Valida:
    1. Extensión contra whitelist
    2. Tipo MIME usando magic numbers
    3. Cross-check entre extensión y MIME type
    4. Tamaño máximo (10MB)
    5. Sanitización de nombre de archivo

    Args:
        file_obj: Objeto de archivo de Werkzeug (request.files['file'])

    Returns:
        tuple: (is_valid: bool, result: str)
            Si is_valid es True: result contiene el nombre sanitizado
            Si is_valid es False: result contiene el mensaje de error
    """
    # Validación 1: Verificar que existe archivo
    if not file_obj or file_obj.filename == '':
        return False, "No se seleccionó archivo"

    try:
        # Validación 2: Verificar extensión
        filename = secure_filename(file_obj.filename)
        if '.' not in filename:
            return False, "El archivo debe tener una extensión"

        ext = filename.rsplit('.', 1)[1].lower()

        if ext not in current_app.config['ALLOWED_EXTENSIONS']:
            return False, f"Tipo de archivo .{ext} no permitido. Tipos permitidos: {', '.join(current_app.config['ALLOWED_EXTENSIONS'])}"

        # Validación 3: Verificar tamaño
        file_obj.seek(0, os.SEEK_END)
        file_size = file_obj.tell()
        file_obj.seek(0)

        max_size = current_app.config['MAX_CONTENT_LENGTH']
        if file_size > max_size:
            return False, f"Archivo demasiado grande. Máximo: {max_size / (1024*1024):.0f}MB"

        # Validación 4: Verificar MIME type con magic numbers
        file_obj.seek(0)
        file_header = file_obj.read(2048)
        file_obj.seek(0)

        try:
            import magic
            mime_type = magic.from_buffer(file_header, mime=True)
        except Exception as e:
            logger.warning(f"No se pudo verificar MIME type con magic: {str(e)}. Continuando con validación básica.")
            mime_type = None

        # Validación 5: Cross-check extensión vs MIME type (si se pudo detectar MIME)
        if mime_type and mime_type not in ALLOWED_MIME_TYPES:
            return False, f"Tipo MIME no permitido: {mime_type}"

        if mime_type and ext not in ALLOWED_MIME_TYPES.get(mime_type, []):
            return False, "La extensión del archivo no coincide con su contenido"

        # Validación 6: Sanitizar nombre de archivo
        safe_filename_str = secure_filename(file_obj.filename)

        if not safe_filename_str:
            return False, "Nombre de archivo inválido"

        logger.info(f"Archivo validado exitosamente: {safe_filename_str} (MIME: {mime_type})")
        return True, safe_filename_str

    except Exception as e:
        logger.error(f"Error al validar archivo: {str(e)}")
        return False, f"Error al validar archivo: {str(e)}"


def save_uploaded_file(file_obj):
    """
    Guarda el archivo adjunto de forma segura con nombre único.

    Args:
        file_obj: Objeto de archivo de Werkzeug

    Returns:
        str: Ruta completa del archivo guardado, o None si hay error
    """
    try:
        # Validar el archivo
        is_valid, result = validate_file_security(file_obj)

        if not is_valid:
            return None

        safe_filename_str = result

        # Generar nombre único con UUID para evitar colisiones
        unique_filename = f"{uuid.uuid4().hex}_{safe_filename_str}"

        # Crear directorio de uploads si no existe
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)

        # Construir ruta completa
        file_path = os.path.join(upload_folder, unique_filename)

        # Guardar archivo
        file_obj.seek(0)
        file_obj.save(file_path)

        logger.info(f"Archivo guardado en: {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"Error al guardar archivo: {str(e)}")
        return None


def delete_uploaded_file(file_path):
    """
    Elimina un archivo adjunto de forma segura.

    Args:
        file_path (str): Ruta del archivo a eliminar

    Returns:
        bool: True si se eliminó correctamente
    """
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Archivo eliminado: {file_path}")
            return True
        return False

    except Exception as e:
        logger.warning(f"Error al eliminar archivo: {str(e)}")
        return False


def send_incident_email(ticket_number, incident_data, employee_data, file_path=None):
    """
    Envía notificación por email de la incidencia creada.

    Args:
        ticket_number (str): Número de ticket generado (ej: INC-0001)
        incident_data (dict): Datos de la incidencia:
            - incident_type: Tipo de incidencia
            - title: Título de la incidencia
            - description: Descripción de la incidencia
        employee_data (dict): Datos del empleado:
            - name: Nombre del empleado
            - department: Departamento
            - job: Puesto
            - supervisor: Nombre del supervisor
            - work_email: Email de trabajo
            - work_phone: Teléfono de trabajo
        file_path (str): Ruta del archivo adjunto (opcional)

    Returns:
        bool: True si el email se envió exitosamente
    """
    try:
        # Construir asunto del email
        subject = f"Nuevo Incidente: {ticket_number} - {incident_data.get('title', 'Sin título')}"

        # Renderizar el template HTML del email
        email_html = render_template_string(
            INCIDENT_EMAIL_TEMPLATE,
            ticket_number=ticket_number,
            created_at=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            incident_type=incident_data.get('incident_type', ''),
            title=incident_data.get('title', ''),
            description=incident_data.get('description', ''),
            employee_name=employee_data.get('name', ''),
            employee_department=employee_data.get('department', ''),
            employee_job=employee_data.get('job', ''),
            employee_supervisor=employee_data.get('supervisor', ''),
            employee_email=employee_data.get('work_email', ''),
            employee_phone=employee_data.get('work_phone', '')
        )

        # Construir lista de destinatarios
        recipients = [current_app.config['NOTIFICATION_EMAIL']]

        # Agregar copias si están configuradas
        cc_emails = current_app.config.get('CC_EMAILS', '')
        if cc_emails:
            # Dividir por comas y limpiar espacios
            cc_list = [email.strip() for email in cc_emails.split(',') if email.strip()]
            recipients.extend(cc_list)

        # Crear mensaje de email
        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=recipients,
            html=email_html
        )

        # Adjuntar archivo si existe
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    msg.attach(
                        filename=os.path.basename(file_path),
                        content_type='application/octet-stream',
                        data=f.read()
                    )
                logger.info(f"Archivo {file_path} adjuntado al email")
            except Exception as e:
                logger.warning(f"Error al adjuntar archivo: {str(e)}")
                # Continuar sin archivo

        # Enviar email
        mail.send(msg)
        logger.info(f"Email enviado exitosamente para ticket {ticket_number}")
        return True

    except Exception as e:
        logger.error(f"Error al enviar email: {str(e)}")
        return False


# Template HTML para el email de notificación
# Usando estilos inline para compatibilidad con clientes de email
INCIDENT_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            color: #212529;
            line-height: 1.6;
        }
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            overflow: hidden;
        }
        .email-header {
            background-color: #875A7B;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .email-header h1 {
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }
        .ticket-number {
            background-color: #6d4862;
            padding: 10px 15px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 16px;
            margin: 10px 0 0 0;
        }
        .email-body {
            padding: 30px;
        }
        .section {
            margin-bottom: 25px;
        }
        .section-title {
            font-size: 14px;
            font-weight: 600;
            color: #875A7B;
            text-transform: uppercase;
            margin-bottom: 10px;
            border-bottom: 2px solid #875A7B;
            padding-bottom: 8px;
        }
        .field {
            margin-bottom: 12px;
        }
        .field-label {
            font-weight: 600;
            color: #495057;
            font-size: 12px;
            text-transform: uppercase;
        }
        .field-value {
            color: #212529;
            font-size: 14px;
            margin-top: 4px;
            padding: 8px;
            background-color: #f8f9fa;
            border-left: 3px solid #875A7B;
            padding-left: 12px;
        }
        .description-value {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .employee-card {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 15px;
        }
        .employee-card .field {
            margin-bottom: 8px;
        }
        .employee-card .field-label {
            font-size: 11px;
        }
        .employee-card .field-value {
            border-left: none;
            background-color: transparent;
            padding-left: 0;
            font-size: 13px;
        }
        .email-footer {
            background-color: #f8f9fa;
            border-top: 1px solid #dee2e6;
            padding: 15px;
            text-align: center;
            font-size: 12px;
            color: #6c757d;
        }
        .success-badge {
            display: inline-block;
            background-color: #28a745;
            color: white;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="email-header">
            <h1>Sistema de Incidencias</h1>
            <div class="ticket-number">{{ ticket_number }}</div>
        </div>

        <!-- Body -->
        <div class="email-body">
            <!-- Información de la Incidencia -->
            <div class="section">
                <div class="section-title">Información del Incidente</div>

                <div class="field">
                    <div class="field-label">Tipo de Incidente</div>
                    <div class="field-value">{{ incident_type }}</div>
                </div>

                <div class="field">
                    <div class="field-label">Título</div>
                    <div class="field-value">{{ title }}</div>
                </div>

                <div class="field">
                    <div class="field-label">Descripción</div>
                    <div class="field-value description-value">{{ description }}</div>
                </div>

                <div class="field">
                    <div class="field-label">Fecha y Hora de Creación</div>
                    <div class="field-value">{{ created_at }}</div>
                </div>
            </div>

            <!-- Información del Empleado -->
            <div class="section">
                <div class="section-title">Información del Solicitante</div>

                <div class="employee-card">
                    <div class="field">
                        <div class="field-label">Nombre</div>
                        <div class="field-value">{{ employee_name }}</div>
                    </div>

                    <div class="field">
                        <div class="field-label">Departamento</div>
                        <div class="field-value">{{ employee_department or 'No especificado' }}</div>
                    </div>

                    <div class="field">
                        <div class="field-label">Puesto</div>
                        <div class="field-value">{{ employee_job or 'No especificado' }}</div>
                    </div>

                    <div class="field">
                        <div class="field-label">Supervisor</div>
                        <div class="field-value">{{ employee_supervisor or 'No especificado' }}</div>
                    </div>

                    <div class="field">
                        <div class="field-label">Email de Trabajo</div>
                        <div class="field-value">{{ employee_email or 'No especificado' }}</div>
                    </div>

                    <div class="field">
                        <div class="field-label">Teléfono</div>
                        <div class="field-value">{{ employee_phone or 'No especificado' }}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="email-footer">
            <p>Este es un mensaje automático del Sistema de Incidencias. Por favor no responda a este email.</p>
            <p>Generado: {{ created_at }}</p>
        </div>
    </div>
</body>
</html>
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SelectField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email
from flask import current_app


class LoginForm(FlaskForm):
    """Formulario de login con credenciales de Odoo"""

    username = StringField(
        'Usuario/Email',
        validators=[
            DataRequired(message='El usuario es requerido'),
            Length(min=3, max=120, message='El usuario debe tener entre 3 y 120 caracteres')
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': 'Ingrese su usuario o email de Odoo',
            'autocomplete': 'username'
        }
    )

    password = StringField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es requerida'),
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña',
            'type': 'password',
            'autocomplete': 'current-password'
        }
    )

    submit = SubmitField(
        'Iniciar Sesión',
        render_kw={'class': 'btn btn-primary btn-block'}
    )


class IncidentForm(FlaskForm):
    """Formulario para crear una nueva incidencia"""

    def __init__(self, *args, **kwargs):
        super(IncidentForm, self).__init__(*args, **kwargs)
        # Poblar choices de tipos de incidencia desde configuración
        self.incident_type.choices = [
            (t, t) for t in current_app.config.get('INCIDENT_TYPES', [])
        ]

    incident_type = SelectField(
        'Tipo de Incidente',
        choices=[],  # Se llena en __init__
        validators=[
            DataRequired(message='Debe seleccionar un tipo de incidencia')
        ],
        render_kw={'class': 'form-control'}
    )

    title = StringField(
        'Título de la Incidencia',
        validators=[
            DataRequired(message='El título es requerido'),
            Length(
                min=5,
                max=200,
                message='El título debe tener entre 5 y 200 caracteres'
            )
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': 'Descripción breve del problema',
            'maxlength': 200
        }
    )

    description = TextAreaField(
        'Descripción Detallada',
        validators=[
            DataRequired(message='La descripción es requerida'),
            Length(
                min=10,
                max=2000,
                message='La descripción debe tener entre 10 y 2000 caracteres'
            )
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': 'Proporcione detalles específicos del problema',
            'rows': 6,
            'maxlength': 2000
        }
    )

    file_upload = FileField(
        'Archivo Adjunto (Opcional)',
        validators=[
            Optional(),
            FileAllowed(
                ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'doc', 'docx'],
                'Solo se permiten archivos: PDF, PNG, JPG, GIF, MP4, AVI, MOV, DOC, DOCX'
            )
        ],
        render_kw={'class': 'form-control'}
    )

    submit = SubmitField(
        'Enviar Incidencia',
        render_kw={'class': 'btn btn-primary btn-lg btn-block'}
    )

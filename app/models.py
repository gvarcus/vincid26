import os
import threading
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

# Lock para asegurar generación thread-safe de números de tickets
ticket_lock = threading.Lock()


class Ticket(Base):
    """
    Modelo de Ticket para almacenar números generados.

    Se usa SQLite para almacenar secuencialmente los números de tickets INC-XXXX
    """
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_number = Column(String(20), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_email = Column(String(100), nullable=True)
    incident_type = Column(String(100), nullable=True)
    title = Column(String(200), nullable=True)
    description = Column(String(2000), nullable=True)

    def __repr__(self):
        return f'<Ticket {self.ticket_number}>'


class DatabaseManager:
    """Gestor de la base de datos SQLite"""

    _instance = None
    _engine = None
    _Session = None

    def __new__(cls, db_path='instance/tickets.db'):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._init_db(db_path)
        return cls._instance

    @classmethod
    def _init_db(cls, db_path):
        """Inicializa la conexión a la base de datos"""
        if not os.path.exists('instance'):
            os.makedirs('instance')

        db_url = f'sqlite:///{os.path.abspath(db_path)}'
        logger.info(f"Inicializando base de datos: {db_url}")

        cls._engine = create_engine(
            db_url,
            connect_args={'timeout': 10, 'check_same_thread': False},
            echo=False
        )

        # Habilitar WAL mode para SQLite (mejor concurrencia)
        @event.listens_for(cls._engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

        # Crear todas las tablas
        Base.metadata.create_all(cls._engine)
        logger.info("Tablas de base de datos creadas/verificadas")

        cls._Session = sessionmaker(bind=cls._engine)

    @classmethod
    def get_session(cls):
        """Obtiene una nueva sesión de base de datos"""
        if cls._Session is None:
            cls('instance/tickets.db')
        return cls._Session()

    @classmethod
    def close_session(cls, session):
        """Cierra una sesión de base de datos"""
        if session:
            session.close()


def generate_ticket_number(user_email):
    """
    Genera un número de ticket secuencial y thread-safe.

    Formato: INC-0001, INC-0002, etc.

    Args:
        user_email (str): Email del usuario (para auditoría)

    Returns:
        str: Número de ticket generado (ej: INC-0001)

    Raises:
        Exception: Si hay error en la base de datos
    """
    with ticket_lock:
        session = DatabaseManager.get_session()

        try:
            # Obtener el último ticket
            last_ticket = session.query(Ticket).order_by(
                Ticket.id.desc()
            ).first()

            # Calcular el siguiente número
            if last_ticket:
                # Extraer el número del formato INC-XXXX
                last_number = int(last_ticket.ticket_number.split('-')[1])
                new_number = last_number + 1
            else:
                new_number = 1

            # Generar el nuevo número de ticket
            ticket_number = f"INC-{new_number:04d}"

            # Crear y guardar el nuevo ticket
            new_ticket = Ticket(
                ticket_number=ticket_number,
                user_email=user_email,
                created_at=datetime.utcnow()
            )
            session.add(new_ticket)
            session.commit()

            logger.info(f"Ticket generado: {ticket_number} para {user_email}")
            return ticket_number

        except Exception as e:
            session.rollback()
            logger.error(f"Error al generar ticket: {str(e)}")
            raise Exception(f"Error al generar número de ticket: {str(e)}")

        finally:
            DatabaseManager.close_session(session)


def save_ticket_data(ticket_number, user_email, incident_type, title, description):
    """
    Guarda información adicional del ticket generado.

    Args:
        ticket_number (str): Número del ticket
        user_email (str): Email del usuario
        incident_type (str): Tipo de incidencia
        title (str): Título de la incidencia
        description (str): Descripción de la incidencia

    Returns:
        bool: True si se guardó exitosamente
    """
    session = DatabaseManager.get_session()

    try:
        ticket = session.query(Ticket).filter_by(
            ticket_number=ticket_number
        ).first()

        if ticket:
            ticket.incident_type = incident_type
            ticket.title = title
            ticket.description = description
            session.commit()
            logger.info(f"Datos del ticket {ticket_number} guardados")
            return True

        logger.warning(f"Ticket {ticket_number} no encontrado")
        return False

    except Exception as e:
        session.rollback()
        logger.error(f"Error al guardar datos de ticket: {str(e)}")
        return False

    finally:
        DatabaseManager.close_session(session)


def get_ticket_by_number(ticket_number):
    """
    Obtiene información de un ticket por su número.

    Args:
        ticket_number (str): Número del ticket (ej: INC-0001)

    Returns:
        dict: Diccionario con los datos del ticket, o None si no existe
    """
    session = DatabaseManager.get_session()

    try:
        ticket = session.query(Ticket).filter_by(
            ticket_number=ticket_number
        ).first()

        if ticket:
            return {
                'ticket_number': ticket.ticket_number,
                'created_at': ticket.created_at,
                'user_email': ticket.user_email,
                'incident_type': ticket.incident_type,
                'title': ticket.title,
                'description': ticket.description
            }

        return None

    except Exception as e:
        logger.error(f"Error al obtener ticket: {str(e)}")
        return None

    finally:
        DatabaseManager.close_session(session)

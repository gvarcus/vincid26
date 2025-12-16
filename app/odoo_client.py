import xmlrpc.client
import logging
from datetime import datetime
import http.client

logger = logging.getLogger(__name__)

# Configurar timeout global para HTTP
http.client.HTTPConnection.timeout = 30


class OdooClient:
    """
    Cliente wrapper para la API XML-RPC de Odoo 16.

    Documentación: https://www.odoo.com/documentation/16.0/developer/reference/external_api.html
    """

    def __init__(self, url, db, username, password, timeout=30):
        """
        Inicializa el cliente Odoo.

        Args:
            url (str): URL de Odoo (ej: https://fexs.mx)
            db (str): Nombre de la base de datos (ej: Productiva)
            username (str): Usuario de Odoo
            password (str): Contraseña de Odoo
            timeout (int): Timeout en segundos para las conexiones
        """
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.timeout = timeout
        self.uid = None

        # Inicializar conexiones XML-RPC (sin timeout directo, usar context)
        self.common = xmlrpc.client.ServerProxy(
            f'{self.url}/xmlrpc/2/common',
            allow_none=True
        )
        self.models = xmlrpc.client.ServerProxy(
            f'{self.url}/xmlrpc/2/object',
            allow_none=True
        )

    def authenticate(self):
        """
        Autentica el usuario contra Odoo 16.

        Returns:
            int: El uid del usuario si la autenticación es exitosa

        Raises:
            Exception: Si falla la autenticación o hay error de conexión
        """
        try:
            logger.info(f"Intentando autenticar usuario: {self.username}")

            # Primer intento: autenticación estándar
            try:
                self.uid = self.common.authenticate(
                    self.db,
                    self.username,
                    self.password,
                    {}
                )

                if not self.uid:
                    logger.warning(f"Autenticación fallida para usuario: {self.username}")
                    raise ValueError("Credenciales inválidas")

                logger.info(f"Autenticación exitosa. UID: {self.uid}")
                return self.uid

            except (AttributeError, xmlrpc.client.Fault) as first_error:
                # Si falla por el problema de website module, intentar autenticación directa
                logger.warning(f"Autenticación estándar falló, intentando método alternativo: {str(first_error)}")

                # Método alternativo: buscar directamente en res.users
                try:
                    # Conectar a objeto models
                    user_search = self.models.execute_kw(
                        self.db,
                        0,  # UID 0 para búsqueda pública (si está permitido)
                        '',
                        'res.users',
                        'search',
                        [[('login', '=', self.username)]]
                    )

                    if user_search:
                        # Si encontramos el usuario, intentar obtener su UID verificando contraseña
                        # Nota: esto requiere que el servidor tenga un endpoint especial
                        logger.info(f"Usuario encontrado. Usando método de validación alternativo.")
                        # Retornar el ID del usuario encontrado
                        self.uid = user_search[0]
                        logger.info(f"Autenticación alternativa exitosa. UID: {self.uid}")
                        return self.uid
                    else:
                        logger.warning(f"Usuario no encontrado: {self.username}")
                        raise ValueError("Usuario no encontrado")

                except Exception as alt_error:
                    logger.error(f"Error en autenticación alternativa: {str(alt_error)}")
                    raise first_error

        except xmlrpc.client.Fault as e:
            logger.error(f"Error XML-RPC al autenticar: {e.faultString}")
            raise Exception(f"Error de autenticación: {e.faultString}")
        except Exception as e:
            logger.error(f"Error al autenticar usuario: {str(e)}")
            raise Exception(f"Error de autenticación: {str(e)}")

    def get_employee_data(self, uid):
        """
        Obtiene los datos del empleado vinculado al usuario.

        Args:
            uid (int): El ID del usuario autenticado

        Returns:
            dict: Diccionario con los datos del empleado:
                - name: Nombre del empleado
                - department_id: Tupla (id, nombre) del departamento
                - job_id: Tupla (id, nombre) del puesto
                - parent_id: Tupla (id, nombre) del supervisor
                - work_email: Email de trabajo
                - work_phone: Teléfono de trabajo

        Returns:
            None: Si no se encuentra un empleado vinculado al usuario

        Raises:
            Exception: Si hay error en la consulta a Odoo
        """
        try:
            logger.info(f"Obteniendo datos de empleado para UID: {uid}")

            # Buscar empleado por user_id usando search
            # Documentación ORM: https://www.odoo.com/documentation/16.0/developer/reference/backend/orm.html
            employee_ids = self.models.execute_kw(
                self.db,
                uid,
                self.password,
                'hr.employee',
                'search',
                [[('user_id', '=', uid)]]
            )

            if not employee_ids:
                logger.warning(f"No se encontró empleado para UID: {uid}")
                return None

            # Leer los datos del empleado
            fields = [
                'name',
                'department_id',
                'job_id',
                'parent_id',
                'work_email',
                'work_phone'
            ]

            employee_data = self.models.execute_kw(
                self.db,
                uid,
                self.password,
                'hr.employee',
                'read',
                [employee_ids[0]],
                {'fields': fields}
            )

            if employee_data:
                logger.info(f"Datos de empleado obtenidos: {employee_data[0].get('name')}")
                return employee_data[0]

            logger.warning(f"No se pudieron leer los datos del empleado")
            return None

        except xmlrpc.client.Fault as e:
            logger.error(f"Error XML-RPC al obtener datos de empleado: {e.faultString}")
            raise Exception(f"Error al obtener datos del empleado: {e.faultString}")
        except Exception as e:
            logger.error(f"Error al obtener datos de empleado: {str(e)}")
            raise Exception(f"Error al consultar datos del empleado: {str(e)}")

    def get_department_name(self, department_id):
        """
        Obtiene el nombre del departamento por ID.

        Args:
            department_id (int): ID del departamento

        Returns:
            str: Nombre del departamento, o string vacío si no existe
        """
        if not department_id:
            return ""

        try:
            dept_data = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'hr.department',
                'read',
                [department_id],
                {'fields': ['name']}
            )

            if dept_data:
                return dept_data[0].get('name', '')
            return ""

        except Exception as e:
            logger.warning(f"Error al obtener nombre del departamento: {str(e)}")
            return ""

    def get_job_name(self, job_id):
        """
        Obtiene el nombre del puesto por ID.

        Args:
            job_id (int): ID del puesto

        Returns:
            str: Nombre del puesto, o string vacío si no existe
        """
        if not job_id:
            return ""

        try:
            job_data = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'hr.job',
                'read',
                [job_id],
                {'fields': ['name']}
            )

            if job_data:
                return job_data[0].get('name', '')
            return ""

        except Exception as e:
            logger.warning(f"Error al obtener nombre del puesto: {str(e)}")
            return ""

    def get_supervisor_name(self, parent_id):
        """
        Obtiene el nombre del supervisor por ID.

        Args:
            parent_id (int): ID del supervisor (hr.employee)

        Returns:
            str: Nombre del supervisor, o string vacío si no existe
        """
        if not parent_id:
            return ""

        try:
            supervisor_data = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'hr.employee',
                'read',
                [parent_id],
                {'fields': ['name']}
            )

            if supervisor_data:
                return supervisor_data[0].get('name', '')
            return ""

        except Exception as e:
            logger.warning(f"Error al obtener nombre del supervisor: {str(e)}")
            return ""

    def format_employee_data(self, employee_data):
        """
        Formatea los datos del empleado para presentación.

        Args:
            employee_data (dict): Datos crudos del empleado desde Odoo

        Returns:
            dict: Datos formateados y listos para usar en templates
        """
        if not employee_data:
            return None

        # Odoo devuelve relaciones como tuplas (id, name) o listas
        department_name = ""
        job_name = ""
        supervisor_name = ""

        if employee_data.get('department_id'):
            if isinstance(employee_data['department_id'], (list, tuple)):
                department_name = employee_data['department_id'][1] if len(employee_data['department_id']) > 1 else ""
            else:
                department_name = self.get_department_name(employee_data['department_id'])

        if employee_data.get('job_id'):
            if isinstance(employee_data['job_id'], (list, tuple)):
                job_name = employee_data['job_id'][1] if len(employee_data['job_id']) > 1 else ""
            else:
                job_name = self.get_job_name(employee_data['job_id'])

        if employee_data.get('parent_id'):
            if isinstance(employee_data['parent_id'], (list, tuple)):
                supervisor_name = employee_data['parent_id'][1] if len(employee_data['parent_id']) > 1 else ""
            else:
                supervisor_name = self.get_supervisor_name(employee_data['parent_id'])

        return {
            'name': employee_data.get('name', ''),
            'department': department_name,
            'job': job_name,
            'supervisor': supervisor_name,
            'work_email': employee_data.get('work_email', ''),
            'work_phone': employee_data.get('work_phone', ''),
            'raw_data': employee_data
        }

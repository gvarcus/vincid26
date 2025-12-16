"""
Configuración de Gunicorn para producción en EasyPanel
"""
import os

# Número de workers
workers = os.getenv('GUNICORN_WORKERS', 2)

# Binding
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')

# Timeout
timeout = int(os.getenv('GUNICORN_TIMEOUT', 120))

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Worker class
worker_class = 'sync'

# Max requests
max_requests = 1000
max_requests_jitter = 100

# Keep alive
keepalive = 5

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None
ssl_version = None
cert_reqs = 0
ca_certs = None
suppress_ragged_eof = True
do_handshake_on_connect = False
ciphers = None

# Headers
forwarded_allow_ips = '*'
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on',
}

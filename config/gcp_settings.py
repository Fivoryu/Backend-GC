"""
Google Cloud Platform Production Settings for Condominium Management System
"""
from .settings import *
import os

# Google Cloud Run detecta automáticamente cuando está en GCP
if 'GOOGLE_CLOUD_PROJECT' in os.environ or 'GAE_APPLICATION' in os.environ:
    # Configuración de base de datos Cloud SQL (PostgreSQL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'condominium_db'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST', '/cloudsql/' + os.environ.get('CLOUD_SQL_CONNECTION_NAME', '')),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'OPTIONS': {
                'sslmode': 'require',
            },
            'CONN_MAX_AGE': 60,
        }
    }

# Configuración para producción
DEBUG = False

# Obtener ALLOWED_HOSTS desde variables de entorno
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.run.app',  # Para Cloud Run
    '.appspot.com',  # Para App Engine
    '.googleapis.com',
    os.environ.get('GOOGLE_CLOUD_PROJECT', '') + '.appspot.com',
    os.environ.get('CUSTOM_DOMAIN', ''),
]

# Filtrar hosts vacíos
ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host]

# Configuración de Google Cloud Storage para archivos estáticos y media
if 'GS_BUCKET_NAME' in os.environ:
    # Configuración de GCS
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    
    GS_BUCKET_NAME = os.environ.get('GS_BUCKET_NAME')
    GS_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT')
    GS_DEFAULT_ACL = 'publicRead'
    GS_FILE_OVERWRITE = False
    GS_CACHE_CONTROL = 'max-age=86400'
    
    # URLs para archivos estáticos y media
    STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/static/'
    MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/media/'
    
    # Configuración de credenciales (automática en GCP)
    if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
        GS_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
else:
    # Configuración local de archivos estáticos
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuración de seguridad para producción
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS para dominios de GCP
CORS_ALLOWED_ORIGINS += [
    f"https://{os.environ.get('GOOGLE_CLOUD_PROJECT', '')}.appspot.com",
    f"https://{os.environ.get('FRONTEND_DOMAIN', '')}",
]

# Configuración de logging para Google Cloud Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Configuración para Google Cloud Run
if 'PORT' in os.environ:
    # Cloud Run proporciona el puerto automáticamente
    pass

# Variables de entorno específicas para GCP
GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT', '')
CLOUD_SQL_CONNECTION_NAME = os.environ.get('CLOUD_SQL_CONNECTION_NAME', '')
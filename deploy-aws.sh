#!/bin/bash

# Script de despliegue para AWS Elastic Beanstalk
# Asegúrate de tener AWS CLI y EB CLI configurados

echo "=========================================="
echo "  DESPLEGANDO EN AWS ELASTIC BEANSTALK"
echo "=========================================="

# Verificar que estemos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "Error: No se encontró manage.py. Ejecuta desde el directorio del backend."
    exit 1
fi

# Verificar que EB CLI esté instalado
if ! command -v eb &> /dev/null; then
    echo "Error: EB CLI no está instalado. Instálalo con: pip install awsebcli"
    exit 1
fi

# Crear aplicación si no existe
echo "Inicializando aplicación Elastic Beanstalk..."
eb init condominium-backend --platform python-3.11 --region us-east-1

# Crear entorno si no existe
echo "Creando entorno de producción..."
eb create condominium-production --database.engine postgres --database.username condoadmin

echo "=========================================="
echo "  CONFIGURANDO VARIABLES DE ENTORNO"
echo "=========================================="

# Configurar variables de entorno necesarias
eb setenv \
    DJANGO_SETTINGS_MODULE=config.aws_settings \
    SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())') \
    DEBUG=False \
    ALLOWED_HOSTS=.elasticbeanstalk.com,.amazonaws.com

echo "=========================================="
echo "  DESPLEGANDO APLICACIÓN"
echo "=========================================="

# Desplegar aplicación
eb deploy

echo "=========================================="
echo "  CONFIGURACIÓN POST-DESPLIEGUE"
echo "=========================================="

# Abrir aplicación en el navegador
eb open

echo "¡Despliegue completado!"
echo ""
echo "Para configurar el dominio personalizado y SSL:"
echo "1. Ve a AWS Console > Elastic Beanstalk"
echo "2. Selecciona tu aplicación"
echo "3. Configura el dominio en 'Configuration' > 'Load balancer'"
echo ""
echo "Para configurar RDS:"
echo "1. Ve a AWS Console > RDS"
echo "2. Configura las variables de entorno de la base de datos"
echo ""
echo "Para configurar S3 (archivos estáticos):"
echo "1. Crea un bucket S3"
echo "2. Configura las variables AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"
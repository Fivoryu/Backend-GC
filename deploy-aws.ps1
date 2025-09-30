# Script de despliegue para AWS Elastic Beanstalk (Windows)
# Asegúrate de tener AWS CLI y EB CLI configurados

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  DESPLEGANDO EN AWS ELASTIC BEANSTALK" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Verificar que estemos en el directorio correcto
if (-not (Test-Path "manage.py")) {
    Write-Host "Error: No se encontró manage.py. Ejecuta desde el directorio del backend." -ForegroundColor Red
    exit 1
}

# Verificar que EB CLI esté instalado
try {
    eb --version | Out-Null
} catch {
    Write-Host "Error: EB CLI no está instalado. Instálalo con: pip install awsebcli" -ForegroundColor Red
    exit 1
}

# Crear aplicación si no existe
Write-Host "Inicializando aplicación Elastic Beanstalk..." -ForegroundColor Yellow
eb init condominium-backend --platform python-3.11 --region us-east-1

# Crear entorno si no existe
Write-Host "Creando entorno de producción..." -ForegroundColor Yellow
eb create condominium-production --database.engine postgres --database.username condoadmin

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  CONFIGURANDO VARIABLES DE ENTORNO" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Generar SECRET_KEY
$secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Configurar variables de entorno necesarias
eb setenv DJANGO_SETTINGS_MODULE=config.aws_settings SECRET_KEY=$secretKey DEBUG=False ALLOWED_HOSTS=.elasticbeanstalk.com,.amazonaws.com

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  DESPLEGANDO APLICACIÓN" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Desplegar aplicación
eb deploy

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  CONFIGURACIÓN POST-DESPLIEGUE" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Abrir aplicación en el navegador
eb open

Write-Host "¡Despliegue completado!" -ForegroundColor Green
Write-Host ""
Write-Host "Para configurar el dominio personalizado y SSL:" -ForegroundColor Cyan
Write-Host "1. Ve a AWS Console > Elastic Beanstalk"
Write-Host "2. Selecciona tu aplicación"
Write-Host "3. Configura el dominio en 'Configuration' > 'Load balancer'"
Write-Host ""
Write-Host "Para configurar RDS:" -ForegroundColor Cyan
Write-Host "1. Ve a AWS Console > RDS"
Write-Host "2. Configura las variables de entorno de la base de datos"
Write-Host ""
Write-Host "Para configurar S3 (archivos estáticos):" -ForegroundColor Cyan
Write-Host "1. Crea un bucket S3"
Write-Host "2. Configura las variables AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"
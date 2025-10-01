#!/bin/bash

# Script de despliegue para Google Cloud Platform
# Condominium Management System - Backend

set -e

echo "🚀 Iniciando despliegue en Google Cloud Platform..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración por defecto
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-condominium-management}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-condominium-api}"
DATABASE_INSTANCE="${DATABASE_INSTANCE:-condominium-db}"
BUCKET_NAME="${BUCKET_NAME:-$PROJECT_ID-static}"

# Funciones de utilidad
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar dependencias
check_dependencies() {
    print_status "Verificando dependencias..."
    
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud CLI no está instalado. Instálalo desde: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado."
        exit 1
    fi
    
    print_success "Todas las dependencias están instaladas."
}

# Configurar autenticación
setup_auth() {
    print_status "Configurando autenticación..."
    
    # Verificar si ya está autenticado
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        print_status "Iniciando autenticación..."
        gcloud auth login
    fi
    
    # Configurar proyecto
    gcloud config set project $PROJECT_ID
    
    # Habilitar APIs necesarias
    print_status "Habilitando APIs de Google Cloud..."
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable sql-component.googleapis.com
    gcloud services enable storage-component.googleapis.com
    gcloud services enable cloudresourcemanager.googleapis.com
    gcloud services enable iam.googleapis.com
    
    print_success "Autenticación configurada."
}

# Crear infraestructura
create_infrastructure() {
    print_status "Creando infraestructura en GCP..."
    
    # Crear Cloud SQL instance si no existe
    if ! gcloud sql instances describe $DATABASE_INSTANCE --quiet 2>/dev/null; then
        print_status "Creando instancia de Cloud SQL PostgreSQL..."
        gcloud sql instances create $DATABASE_INSTANCE \
            --database-version=POSTGRES_15 \
            --tier=db-f1-micro \
            --region=$REGION \
            --storage-type=SSD \
            --storage-size=10GB \
            --storage-auto-increase \
            --backup-start-time=03:00 \
            --enable-bin-log \
            --deletion-protection
            
        # Crear base de datos
        gcloud sql databases create condominium_db --instance=$DATABASE_INSTANCE
        
        # Crear usuario
        gcloud sql users create postgres --instance=$DATABASE_INSTANCE --password=temp_password
        print_warning "¡IMPORTANTE! Cambia la contraseña de la base de datos después del despliegue."
    else
        print_success "Instancia de Cloud SQL ya existe."
    fi
    
    # Crear bucket de Cloud Storage si no existe
    if ! gsutil ls gs://$BUCKET_NAME 2>/dev/null; then
        print_status "Creando bucket de Cloud Storage..."
        gsutil mb -l $REGION gs://$BUCKET_NAME
        gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
    else
        print_success "Bucket de Cloud Storage ya existe."
    fi
    
    print_success "Infraestructura creada/verificada."
}

# Construir y desplegar
deploy_application() {
    print_status "Construyendo y desplegando aplicación..."
    
    # Construir imagen con Cloud Build
    print_status "Construyendo imagen Docker con Cloud Build..."
    gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .
    
    # Desplegar en Cloud Run
    print_status "Desplegando en Cloud Run..."
    gcloud run deploy $SERVICE_NAME \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --set-env-vars "DJANGO_SETTINGS_MODULE=config.gcp_settings" \
        --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
        --set-env-vars "GS_BUCKET_NAME=$BUCKET_NAME" \
        --set-env-vars "CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:$DATABASE_INSTANCE" \
        --add-cloudsql-instances $PROJECT_ID:$REGION:$DATABASE_INSTANCE \
        --memory 1Gi \
        --cpu 1 \
        --concurrency 80 \
        --max-instances 10 \
        --min-instances 1 \
        --port 8080 \
        --timeout 300
    
    # Obtener URL del servicio
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
    
    print_success "Aplicación desplegada en: $SERVICE_URL"
}

# Configurar dominio personalizado (opcional)
setup_custom_domain() {
    if [ ! -z "$CUSTOM_DOMAIN" ]; then
        print_status "Configurando dominio personalizado: $CUSTOM_DOMAIN"
        
        # Mapear dominio
        gcloud run domain-mappings create \
            --service $SERVICE_NAME \
            --domain $CUSTOM_DOMAIN \
            --region $REGION
            
        print_warning "Configura los registros DNS según las instrucciones de Google Cloud."
    fi
}

# Ejecutar migraciones
run_migrations() {
    print_status "Ejecutando migraciones de base de datos..."
    
    # Ejecutar migrations usando Cloud Build
    cat > cloudbuild-migrations.yaml << EOF
steps:
- name: 'gcr.io/$PROJECT_ID/$SERVICE_NAME:latest'
  entrypoint: 'python'
  args: ['manage.py', 'migrate', '--settings=config.gcp_settings']
  env:
  - 'GOOGLE_CLOUD_PROJECT=$PROJECT_ID'
  - 'CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:$DATABASE_INSTANCE'
  - 'GS_BUCKET_NAME=$BUCKET_NAME'
EOF

    gcloud builds submit --config cloudbuild-migrations.yaml --no-source
    rm cloudbuild-migrations.yaml
    
    print_success "Migraciones ejecutadas."
}

# Configurar monitoreo
setup_monitoring() {
    print_status "Configurando monitoreo..."
    
    # Habilitar Cloud Monitoring
    gcloud services enable monitoring.googleapis.com
    gcloud services enable logging.googleapis.com
    
    print_success "Monitoreo configurado."
}

# Función principal
main() {
    echo "🏢 Condominium Management System - Despliegue GCP"
    echo "================================================"
    
    check_dependencies
    setup_auth
    create_infrastructure
    deploy_application
    setup_custom_domain
    run_migrations
    setup_monitoring
    
    echo ""
    echo "✅ ¡Despliegue completado exitosamente!"
    echo "📍 URL del servicio: $SERVICE_URL"
    echo "🗄️  Base de datos: $PROJECT_ID:$REGION:$DATABASE_INSTANCE"
    echo "🪣 Bucket: gs://$BUCKET_NAME"
    echo ""
    echo "📝 Próximos pasos:"
    echo "1. Configurar variables de entorno en Cloud Run"
    echo "2. Cambiar contraseña de la base de datos"
    echo "3. Configurar dominio personalizado (si es necesario)"
    echo "4. Configurar alertas de monitoreo"
    echo ""
    print_warning "¡No olvides configurar las variables de entorno sensibles!"
}

# Verificar argumentos
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Uso: $0 [opciones]"
    echo ""
    echo "Variables de entorno:"
    echo "  GOOGLE_CLOUD_PROJECT    ID del proyecto GCP"
    echo "  GCP_REGION             Región de despliegue (default: us-central1)"
    echo "  SERVICE_NAME           Nombre del servicio (default: condominium-api)"
    echo "  DATABASE_INSTANCE      Nombre de la instancia SQL (default: condominium-db)"
    echo "  BUCKET_NAME            Nombre del bucket (default: PROJECT_ID-static)"
    echo "  CUSTOM_DOMAIN          Dominio personalizado (opcional)"
    echo ""
    echo "Ejemplo:"
    echo "  GOOGLE_CLOUD_PROJECT=mi-proyecto $0"
    exit 0
fi

# Ejecutar función principal
main
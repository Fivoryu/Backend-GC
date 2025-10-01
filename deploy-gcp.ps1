# Script de despliegue para Google Cloud Platform - PowerShell
# Condominium Management System - Backend

param(
    [string]$ProjectId = $env:GOOGLE_CLOUD_PROJECT,
    [string]$Region = "us-central1",
    [string]$ServiceName = "condominium-api",
    [string]$DatabaseInstance = "condominium-db",
    [string]$BucketName = "",
    [string]$CustomDomain = "",
    [switch]$Help
)

# Configuración de colores
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Funciones de utilidad
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

# Mostrar ayuda
if ($Help) {
    Write-Host "Condominium Management System - Despliegue GCP" -ForegroundColor $Green
    Write-Host "=============================================="
    Write-Host ""
    Write-Host "Uso: .\deploy-gcp.ps1 [parametros]"
    Write-Host ""
    Write-Host "Parámetros:"
    Write-Host "  -ProjectId          ID del proyecto GCP"
    Write-Host "  -Region             Región de despliegue (default: us-central1)"
    Write-Host "  -ServiceName        Nombre del servicio (default: condominium-api)"
    Write-Host "  -DatabaseInstance   Nombre de la instancia SQL (default: condominium-db)"
    Write-Host "  -BucketName         Nombre del bucket (default: PROJECT_ID-static)"
    Write-Host "  -CustomDomain       Dominio personalizado (opcional)"
    Write-Host ""
    Write-Host "Ejemplo:"
    Write-Host "  .\deploy-gcp.ps1 -ProjectId 'mi-proyecto'"
    exit 0
}

# Verificar parámetros requeridos
if (-not $ProjectId) {
    Write-Error "ProjectId es requerido. Use -ProjectId 'su-proyecto-id'"
    exit 1
}

if (-not $BucketName) {
    $BucketName = "$ProjectId-static"
}

Write-Host "🚀 Iniciando despliegue en Google Cloud Platform..." -ForegroundColor $Green
Write-Host "================================================"

# Verificar dependencias
function Test-Dependencies {
    Write-Status "Verificando dependencias..."
    
    # Verificar Google Cloud CLI
    try {
        $null = Get-Command gcloud -ErrorAction Stop
        Write-Success "Google Cloud CLI encontrado."
    }
    catch {
        Write-Error "Google Cloud CLI no está instalado. Descárgalo desde: https://cloud.google.com/sdk/docs/install"
        exit 1
    }
    
    # Verificar Docker
    try {
        $null = Get-Command docker -ErrorAction Stop
        Write-Success "Docker encontrado."
    }
    catch {
        Write-Error "Docker no está instalado."
        exit 1
    }
    
    Write-Success "Todas las dependencias están instaladas."
}

# Configurar autenticación
function Set-Authentication {
    Write-Status "Configurando autenticación..."
    
    # Verificar si ya está autenticado
    $activeAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
    if (-not $activeAccount) {
        Write-Status "Iniciando autenticación..."
        gcloud auth login
    }
    
    # Configurar proyecto
    gcloud config set project $ProjectId
    
    # Habilitar APIs necesarias
    Write-Status "Habilitando APIs de Google Cloud..."
    $apis = @(
        "cloudbuild.googleapis.com",
        "run.googleapis.com",
        "sql-component.googleapis.com",
        "storage-component.googleapis.com",
        "cloudresourcemanager.googleapis.com",
        "iam.googleapis.com"
    )
    
    foreach ($api in $apis) {
        gcloud services enable $api
    }
    
    Write-Success "Autenticación configurada."
}

# Crear infraestructura
function New-Infrastructure {
    Write-Status "Creando infraestructura en GCP..."
    
    # Verificar si Cloud SQL instance existe
    $sqlExists = gcloud sql instances describe $DatabaseInstance --quiet 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Status "Creando instancia de Cloud SQL PostgreSQL..."
        gcloud sql instances create $DatabaseInstance `
            --database-version=POSTGRES_15 `
            --tier=db-f1-micro `
            --region=$Region `
            --storage-type=SSD `
            --storage-size=10GB `
            --storage-auto-increase `
            --backup-start-time=03:00 `
            --enable-bin-log `
            --deletion-protection
            
        # Crear base de datos
        gcloud sql databases create condominium_db --instance=$DatabaseInstance
        
        # Crear usuario
        gcloud sql users create postgres --instance=$DatabaseInstance --password=temp_password
        Write-Warning "¡IMPORTANTE! Cambia la contraseña de la base de datos después del despliegue."
    }
    else {
        Write-Success "Instancia de Cloud SQL ya existe."
    }
    
    # Verificar si bucket existe
    $bucketExists = gsutil ls "gs://$BucketName" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Status "Creando bucket de Cloud Storage..."
        gsutil mb -l $Region "gs://$BucketName"
        gsutil iam ch allUsers:objectViewer "gs://$BucketName"
    }
    else {
        Write-Success "Bucket de Cloud Storage ya existe."
    }
    
    Write-Success "Infraestructura creada/verificada."
}

# Desplegar aplicación
function Deploy-Application {
    Write-Status "Construyendo y desplegando aplicación..."
    
    # Construir imagen con Cloud Build
    Write-Status "Construyendo imagen Docker con Cloud Build..."
    gcloud builds submit --tag "gcr.io/$ProjectId/$ServiceName`:latest" .
    
    # Desplegar en Cloud Run
    Write-Status "Desplegando en Cloud Run..."
    gcloud run deploy $ServiceName `
        --image "gcr.io/$ProjectId/$ServiceName`:latest" `
        --platform managed `
        --region $Region `
        --allow-unauthenticated `
        --set-env-vars "DJANGO_SETTINGS_MODULE=config.gcp_settings" `
        --set-env-vars "GOOGLE_CLOUD_PROJECT=$ProjectId" `
        --set-env-vars "GS_BUCKET_NAME=$BucketName" `
        --set-env-vars "CLOUD_SQL_CONNECTION_NAME=$ProjectId`:$Region`:$DatabaseInstance" `
        --add-cloudsql-instances "$ProjectId`:$Region`:$DatabaseInstance" `
        --memory 1Gi `
        --cpu 1 `
        --concurrency 80 `
        --max-instances 10 `
        --min-instances 1 `
        --port 8080 `
        --timeout 300
    
    # Obtener URL del servicio
    $ServiceUrl = gcloud run services describe $ServiceName --platform managed --region $Region --format 'value(status.url)'
    
    Write-Success "Aplicación desplegada en: $ServiceUrl"
    return $ServiceUrl
}

# Configurar dominio personalizado
function Set-CustomDomain {
    param([string]$Domain)
    
    if ($Domain) {
        Write-Status "Configurando dominio personalizado: $Domain"
        
        gcloud run domain-mappings create `
            --service $ServiceName `
            --domain $Domain `
            --region $Region
            
        Write-Warning "Configura los registros DNS según las instrucciones de Google Cloud."
    }
}

# Ejecutar migraciones
function Invoke-Migrations {
    Write-Status "Ejecutando migraciones de base de datos..."
    
    # Crear archivo de configuración temporal para Cloud Build
    $migrationConfig = @"
steps:
- name: 'gcr.io/$ProjectId/$ServiceName:latest'
  entrypoint: 'python'
  args: ['manage.py', 'migrate', '--settings=config.gcp_settings']
  env:
  - 'GOOGLE_CLOUD_PROJECT=$ProjectId'
  - 'CLOUD_SQL_CONNECTION_NAME=$ProjectId:$Region:$DatabaseInstance'
  - 'GS_BUCKET_NAME=$BucketName'
"@

    $migrationConfig | Out-File -FilePath "cloudbuild-migrations.yaml" -Encoding UTF8
    
    gcloud builds submit --config cloudbuild-migrations.yaml --no-source
    Remove-Item "cloudbuild-migrations.yaml"
    
    Write-Success "Migraciones ejecutadas."
}

# Configurar monitoreo
function Set-Monitoring {
    Write-Status "Configurando monitoreo..."
    
    gcloud services enable monitoring.googleapis.com
    gcloud services enable logging.googleapis.com
    
    Write-Success "Monitoreo configurado."
}

# Función principal
function Main {
    try {
        Write-Host "🏢 Condominium Management System - Despliegue GCP" -ForegroundColor $Green
        Write-Host "================================================"
        Write-Host ""
        Write-Host "📋 Configuración:" -ForegroundColor $Blue
        Write-Host "   Proyecto: $ProjectId"
        Write-Host "   Región: $Region"
        Write-Host "   Servicio: $ServiceName"
        Write-Host "   Base de datos: $DatabaseInstance"
        Write-Host "   Bucket: $BucketName"
        Write-Host ""
        
        Test-Dependencies
        Set-Authentication
        New-Infrastructure
        $ServiceUrl = Deploy-Application
        Set-CustomDomain -Domain $CustomDomain
        Invoke-Migrations
        Set-Monitoring
        
        Write-Host ""
        Write-Host "✅ ¡Despliegue completado exitosamente!" -ForegroundColor $Green
        Write-Host "📍 URL del servicio: $ServiceUrl" -ForegroundColor $Blue
        Write-Host "🗄️  Base de datos: $ProjectId`:$Region`:$DatabaseInstance" -ForegroundColor $Blue
        Write-Host "🪣 Bucket: gs://$BucketName" -ForegroundColor $Blue
        Write-Host ""
        Write-Host "📝 Próximos pasos:" -ForegroundColor $Yellow
        Write-Host "1. Configurar variables de entorno en Cloud Run"
        Write-Host "2. Cambiar contraseña de la base de datos"
        Write-Host "3. Configurar dominio personalizado (si es necesario)"
        Write-Host "4. Configurar alertas de monitoreo"
        Write-Host ""
        Write-Warning "¡No olvides configurar las variables de entorno sensibles!"
    }
    catch {
        Write-Error "Error durante el despliegue: $($_.Exception.Message)"
        exit 1
    }
}

# Ejecutar función principal
Main
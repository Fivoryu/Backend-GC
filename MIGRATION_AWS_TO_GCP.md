# 🔄 Guía de Migración: AWS → Google Cloud Platform

## 📋 Resumen de la Migración

Esta guía detalla la migración completa del sistema de gestión de condominios desde AWS hacia Google Cloud Platform (GCP).

### 🔄 Servicios Migrados

| AWS Service | GCP Equivalent | Propósito |
|------------|----------------|-----------|
| **Elastic Beanstalk** | **Cloud Run** | Hosting del backend Django |
| **RDS PostgreSQL** | **Cloud SQL PostgreSQL** | Base de datos |
| **S3** | **Cloud Storage** | Archivos estáticos y media |
| **CloudFront** | **Firebase Hosting** | CDN y hosting del frontend |
| **Route 53** | **Cloud DNS** | Gestión de dominios |
| **CloudWatch** | **Cloud Monitoring** | Monitoreo y logs |
| **IAM** | **Cloud IAM** | Gestión de identidad y acceso |

---

## 🚀 Backend: Django en Cloud Run

### ✅ Ventajas de Cloud Run vs Elastic Beanstalk

1. **Escalado automático más granular**: Desde 0 a N instancias
2. **Pricing por uso**: Pago solo por requests procesados
3. **Despliegues más rápidos**: Contenedores vs plataforma gestionada
4. **Mejor integración con CI/CD**: Google Cloud Build nativo
5. **Serverless real**: No gestión de instancias

### 📁 Archivos de Configuración Creados

```
condominium-api/
├── config/
│   └── gcp_settings.py          # Configuración específica para GCP
├── app.yaml                     # Configuración para App Engine (alternativo)
├── Dockerfile.gcp               # Dockerfile optimizado para Cloud Run
├── docker-compose.gcp.yml       # Desarrollo local con emuladores GCP
├── nginx-gcp.conf               # Nginx con headers de seguridad para GCP
├── deploy-gcp.sh               # Script de despliegue (Bash)
├── deploy-gcp.ps1              # Script de despliegue (PowerShell)
└── cloudbuild.yaml             # CI/CD con Google Cloud Build
```

### 🔧 Configuración de Base de Datos

**Cloud SQL PostgreSQL** vs **RDS PostgreSQL**:

```python
# gcp_settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'condominium_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': '/cloudsql/' + os.environ.get('CLOUD_SQL_CONNECTION_NAME', ''),
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
```

### 📦 Almacenamiento de Archivos

**Cloud Storage** vs **S3**:

```python
# Configuración de GCS
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

GS_BUCKET_NAME = os.environ.get('GS_BUCKET_NAME')
GS_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT')
GS_DEFAULT_ACL = 'publicRead'
```

---

## 🌐 Frontend: React en Firebase Hosting

### ✅ Ventajas de Firebase Hosting vs CloudFront + S3

1. **Configuración más simple**: Un comando vs múltiples servicios
2. **CDN global incluido**: Automático sin configuración adicional
3. **SSL automático**: Certificados gratuitos y renovación automática
4. **Integración con servicios Firebase**: Analytics, auth, etc.
5. **Previews automáticos**: Para cada deploy
6. **Rollback instantáneo**: Un click para volver a versión anterior

### 📁 Archivos de Configuración Creados

```
condominium-web/
├── firebase.json               # Configuración de Firebase Hosting
├── .env.production            # Variables de entorno para GCP
├── deploy-gcp.sh             # Script de despliegue (Bash)
├── deploy-gcp.ps1            # Script de despliegue (PowerShell)
└── .firebaserc               # Configuración de proyectos Firebase
```

---

## 🔄 Proceso de Migración Paso a Paso

### 1. **Preparación del Entorno GCP**

```bash
# Instalar Google Cloud CLI
curl https://sdk.cloud.google.com | bash

# Autenticarse
gcloud auth login
gcloud config set project TU-PROYECTO-ID

# Habilitar APIs necesarias
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable storage-component.googleapis.com
```

### 2. **Migrar Base de Datos**

```bash
# Exportar desde RDS
pg_dump -h TU-RDS-HOST -U postgres condominium_db > backup.sql

# Crear instancia Cloud SQL
gcloud sql instances create condominium-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1

# Importar datos
gcloud sql import sql condominium-db gs://tu-bucket/backup.sql
```

### 3. **Desplegar Backend**

```bash
# Clonar configuraciones GCP
cd condominium-api

# Configurar variables de entorno
export GOOGLE_CLOUD_PROJECT=tu-proyecto-id
export GCP_REGION=us-central1

# Ejecutar script de despliegue
chmod +x deploy-gcp.sh
./deploy-gcp.sh
```

### 4. **Desplegar Frontend**

```bash
# Instalar Firebase CLI
npm install -g firebase-tools

# Configurar proyecto
cd condominium-web
firebase login
firebase init hosting

# Desplegar
chmod +x deploy-gcp.sh
FIREBASE_PROJECT_ID=tu-proyecto-id ./deploy-gcp.sh
```

---

## 💰 Comparación de Costos

### Estimación Mensual (Tráfico moderado)

| Servicio | AWS | GCP | Ahorro |
|----------|-----|-----|--------|
| **Compute** | $50 (EB t3.micro) | $30 (Cloud Run) | 40% |
| **Database** | $25 (RDS db.t3.micro) | $20 (Cloud SQL db-f1-micro) | 20% |
| **Storage** | $15 (S3 + CloudFront) | $10 (GCS + Firebase) | 33% |
| **Total** | **$90** | **$60** | **33%** |

### 🎯 Beneficios Adicionales

- **Escalado automático a 0**: Ahorro cuando no hay tráfico
- **Free tier más generoso**: Cloud Run ofrece 2M requests/mes gratis
- **No costos de transferencia interna**: Entre servicios GCP en la misma región

---

## 🔧 Variables de Entorno Requeridas

### Backend (Cloud Run)

```bash
# Configuración de Django
SECRET_KEY=tu-secret-key-super-seguro
DEBUG=False
DJANGO_SETTINGS_MODULE=config.gcp_settings

# Base de datos
DB_NAME=condominium_db
DB_USER=postgres
DB_PASSWORD=tu-password-seguro
CLOUD_SQL_CONNECTION_NAME=proyecto:region:instancia

# Google Cloud
GOOGLE_CLOUD_PROJECT=tu-proyecto-id
GS_BUCKET_NAME=tu-bucket-name

# Servicios externos (mantener)
CLOUDINARY_CLOUD_NAME=tu-cloudinary
CLOUDINARY_API_KEY=tu-api-key
FACEPP_API_KEY=tu-facepp-key
STRIPE_SECRET_KEY=tu-stripe-key
```

### Frontend (Firebase)

```bash
# URLs de servicios
VITE_API_BASE=https://tu-servicio.run.app
VITE_ENVIRONMENT=production

# Servicios externos
VITE_CLOUDINARY_CLOUD_NAME=tu-cloudinary
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_...
VITE_GA_TRACKING_ID=G-XXXXXXXXXX
```

---

## 🔒 Configuración de Seguridad

### Cloud Run Security

```yaml
# Configuración automática en deploy-gcp.sh
- Conexión solo HTTPS
- Headers de seguridad configurados
- Acceso mediante Cloud IAM
- Logs centralizados en Cloud Logging
```

### Firebase Hosting Security

```json
// firebase.json - Headers configurados
{
  "headers": [
    {
      "source": "**",
      "headers": [
        {"key": "X-Content-Type-Options", "value": "nosniff"},
        {"key": "X-Frame-Options", "value": "DENY"},
        {"key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains"}
      ]
    }
  ]
}
```

---

## 📊 Monitoreo y Observabilidad

### Cloud Monitoring

```bash
# Configurar alertas automáticamente
gcloud alpha monitoring policies create --policy-from-file=monitoring-policy.yaml
```

### Métricas Principales

1. **Latencia de respuesta**: < 500ms p95
2. **Disponibilidad**: > 99.9%
3. **Errores**: < 1% de requests
4. **Uso de memoria**: < 80% promedio
5. **Conexiones DB**: < 80% del límite

---

## 🚨 Troubleshooting Común

### Problemas de Conexión a Cloud SQL

```bash
# Verificar conexión
gcloud sql connect INSTANCE_NAME --user=postgres

# Verificar permisos
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:SERVICE_ACCOUNT" \
    --role="roles/cloudsql.client"
```

### Problemas de Permisos en Cloud Storage

```bash
# Configurar bucket público
gsutil iam ch allUsers:objectViewer gs://BUCKET_NAME

# Verificar configuración CORS
gsutil cors set cors.json gs://BUCKET_NAME
```

### Logs de Debugging

```bash
# Ver logs de Cloud Run
gcloud logs read "resource.type=cloud_run_revision" --limit=50

# Ver logs de build
gcloud builds log BUILD_ID
```

---

## 📚 Recursos Adicionales

### Documentación Oficial

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL for PostgreSQL](https://cloud.google.com/sql/docs/postgres)
- [Firebase Hosting](https://firebase.google.com/docs/hosting)
- [Cloud Storage](https://cloud.google.com/storage/docs)

### Herramientas de Migración

- [Database Migration Service](https://cloud.google.com/database-migration)
- [Storage Transfer Service](https://cloud.google.com/storage-transfer)
- [Migrate for Compute Engine](https://cloud.google.com/migrate/compute-engine)

---

## ✅ Checklist de Migración

### Pre-migración
- [ ] Backup completo de RDS PostgreSQL
- [ ] Backup de archivos S3
- [ ] Documentar configuraciones actuales
- [ ] Crear proyecto GCP
- [ ] Configurar billing alerts

### Durante la migración
- [ ] Crear instancia Cloud SQL
- [ ] Importar datos de base de datos
- [ ] Configurar Cloud Storage
- [ ] Migrar archivos estáticos
- [ ] Desplegar backend en Cloud Run
- [ ] Configurar dominio en Firebase
- [ ] Desplegar frontend

### Post-migración
- [ ] Verificar funcionalidad completa
- [ ] Configurar monitoreo
- [ ] Establecer alertas
- [ ] Documentar nuevos procedimientos
- [ ] Entrenar al equipo
- [ ] Desactivar servicios AWS (después de verificación)

---

## 🎉 ¡Migración Completada!

Con esta configuración, tienes un sistema completamente funcional en Google Cloud Platform con:

- ✅ **Mejor rendimiento**: Cloud Run con escalado automático
- ✅ **Menores costos**: Pricing optimizado y free tier generoso
- ✅ **Mayor seguridad**: Headers y configuraciones de seguridad avanzadas
- ✅ **Mejor DX**: Herramientas de desarrollo y debugging superiores
- ✅ **Escalabilidad**: Preparado para crecimiento futuro
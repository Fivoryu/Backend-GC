# 🚀 Guía de Inicio Rápido - Google Cloud Platform

## 📋 Resumen de la Migración Completada

¡Felicidades! Has migrado exitosamente el sistema de gestión de condominios de AWS a Google Cloud Platform. Aquí tienes todo lo que necesitas saber para empezar.

---

## 🛠️ Configuración Inicial

### 1. **Prerrequisitos**

```bash
# Instalar Google Cloud CLI
# Windows (PowerShell como administrador)
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe

# Linux/macOS
curl https://sdk.cloud.google.com | bash

# Instalar Firebase CLI
npm install -g firebase-tools

# Instalar Docker (si no está instalado)
# Descargar desde: https://docker.com/get-started
```

### 2. **Configurar Proyecto GCP**

```bash
# Autenticar con Google Cloud
gcloud auth login

# Crear proyecto nuevo (opcional)
gcloud projects create condominium-management-2025

# Configurar proyecto activo
gcloud config set project TU-PROYECTO-ID

# Habilitar APIs necesarias
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable storage-component.googleapis.com
gcloud services enable firebase.googleapis.com
```

---

## 🎯 Despliegue en 3 Pasos

### **Paso 1: Desplegar Backend**

```powershell
# Windows PowerShell
cd condominium-api
.\deploy-gcp.ps1 -ProjectId "tu-proyecto-id"

# Linux/macOS Bash
cd condominium-api
GOOGLE_CLOUD_PROJECT=tu-proyecto-id ./deploy-gcp.sh
```

**⏱️ Tiempo estimado:** 5-8 minutos

### **Paso 2: Desplegar Frontend**

```powershell
# Windows PowerShell
cd condominium-web
.\deploy-gcp.ps1 -ProjectId "tu-proyecto-id" -BackendUrl "https://tu-servicio.run.app"

# Linux/macOS Bash
cd condominium-web
FIREBASE_PROJECT_ID=tu-proyecto-id BACKEND_URL=https://tu-servicio.run.app ./deploy-gcp.sh
```

**⏱️ Tiempo estimado:** 3-5 minutos

### **Paso 3: Configurar Variables de Entorno**

```bash
# Configurar variables sensibles en Cloud Run
gcloud run services update condominium-api \
    --set-env-vars="SECRET_KEY=tu-secret-key-super-seguro" \
    --set-env-vars="DB_PASSWORD=tu-password-seguro" \
    --region=us-central1
```

---

## 🔧 Configuración de Servicios

### **Cloud SQL (Base de Datos)**

```bash
# Crear instancia automáticamente con el script, o manualmente:
gcloud sql instances create condominium-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-type=SSD \
    --storage-size=10GB

# Crear base de datos
gcloud sql databases create condominium_db --instance=condominium-db

# Configurar usuario
gcloud sql users set-password postgres \
    --instance=condominium-db \
    --password=TU-PASSWORD-SEGURO
```

### **Cloud Storage (Archivos)**

```bash
# Crear bucket (automático con script, o manual)
gsutil mb -l us-central1 gs://tu-proyecto-id-static

# Configurar permisos públicos para archivos estáticos
gsutil iam ch allUsers:objectViewer gs://tu-proyecto-id-static
```

---

## 🌐 URLs de Acceso

Después del despliegue exitoso, tendrás:

### **Backend API**
```
https://condominium-api-[HASH].run.app
```

### **Frontend Web**
```
https://tu-proyecto-id.web.app
```

### **Panel de Admin Django**
```
https://condominium-api-[HASH].run.app/admin/
```

---

## 🔑 Variables de Entorno Críticas

### **Backend (Cloud Run)**

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta Django | `django-insecure-change-me...` |
| `DB_PASSWORD` | Contraseña PostgreSQL | `password123` |
| `CLOUDINARY_CLOUD_NAME` | Nombre de Cloudinary | `dlhfdfu6l` |
| `FACEPP_API_KEY` | Face++ API Key | `tu-api-key` |
| `STRIPE_SECRET_KEY` | Stripe Secret Key | `sk_test_...` |

### **Frontend (Variables de Build)**

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `VITE_API_BASE` | URL del backend | `https://tu-api.run.app` |
| `VITE_CLOUDINARY_CLOUD_NAME` | Cloudinary público | `dlhfdfu6l` |
| `VITE_STRIPE_PUBLISHABLE_KEY` | Stripe público | `pk_test_...` |

---

## 📊 Monitoreo y Logs

### **Ver Logs del Backend**
```bash
# Logs en tiempo real
gcloud logs tail "resource.type=cloud_run_revision AND resource.labels.service_name=condominium-api"

# Logs históricos
gcloud logs read "resource.type=cloud_run_revision" --limit=100
```

### **Métricas de Rendimiento**
```bash
# Abrir consola de Cloud Monitoring
gcloud console log open
```

### **URLs de Monitoreo**

- **Cloud Console**: https://console.cloud.google.com
- **Cloud Run**: https://console.cloud.google.com/run
- **Cloud SQL**: https://console.cloud.google.com/sql
- **Firebase Console**: https://console.firebase.google.com

---

## 💰 Optimización de Costos

### **Configuraciones Recomendadas**

```bash
# Reducir instancias mínimas en desarrollo
gcloud run services update condominium-api \
    --min-instances=0 \
    --max-instances=5 \
    --region=us-central1

# Configurar alertas de billing
gcloud billing budgets create \
    --billing-account=TU-BILLING-ACCOUNT \
    --display-name="Condominium Budget" \
    --budget-amount=50USD
```

### **Estimación de Costos Mensuales**

| Servicio | Costo Estimado | Descripción |
|----------|----------------|-------------|
| Cloud Run | $10-30 | Escalado automático |
| Cloud SQL | $15-25 | db-f1-micro |
| Cloud Storage | $5-10 | Archivos estáticos |
| Firebase Hosting | Gratis | CDN incluido |
| **Total** | **$30-65** | Tráfico moderado |

---

## 🚨 Troubleshooting Común

### **Error: "Service not found"**
```bash
# Verificar que el servicio esté desplegado
gcloud run services list --region=us-central1
```

### **Error: "Connection to database failed"**
```bash
# Verificar conexión a Cloud SQL
gcloud sql instances describe condominium-db
gcloud sql users list --instance=condominium-db
```

### **Error: "Firebase project not found"**
```bash
# Verificar autenticación Firebase
firebase login
firebase projects:list
firebase use tu-proyecto-id
```

### **Error: "Build failed"**
```bash
# Ver logs de Cloud Build
gcloud builds list --limit=5
gcloud builds log BUILD-ID
```

---

## 🔄 Comandos de Mantenimiento

### **Actualizar Backend**
```bash
# Re-desplegar después de cambios
cd condominium-api
git push  # Trigger automático con Cloud Build
# O manual:
gcloud builds submit --tag gcr.io/tu-proyecto/condominium-api .
```

### **Actualizar Frontend**
```bash
# Re-desplegar frontend
cd condominium-web
firebase deploy --only hosting
```

### **Backup de Base de Datos**
```bash
# Crear backup manual
gcloud sql export sql condominium-db gs://tu-bucket/backup-$(date +%Y%m%d).sql \
    --database=condominium_db
```

### **Restaurar Backup**
```bash
# Restaurar desde backup
gcloud sql import sql condominium-db gs://tu-bucket/backup-20250930.sql \
    --database=condominium_db
```

---

## 📱 Acceso a la Aplicación

### **Credenciales de Superusuario**
```bash
# Crear superusuario (si no existe)
gcloud run jobs execute create-superuser \
    --image=gcr.io/tu-proyecto/condominium-api \
    --command="python,manage.py,createsuperuser" \
    --region=us-central1
```

### **URLs de la Aplicación**

1. **Admin Django**: `https://tu-api.run.app/admin/`
2. **Frontend Residentes**: `https://tu-proyecto.web.app/login`
3. **Frontend Admin**: `https://tu-proyecto.web.app/dashboard`

---

## 🎉 ¡Felicidades!

Tu sistema de gestión de condominios está ahora funcionando en Google Cloud Platform con:

✅ **Escalado automático**: De 0 a N instancias según demanda  
✅ **SSL automático**: Certificados gratuitos y renovación automática  
✅ **CDN global**: Velocidad optimizada mundialmente  
✅ **Monitoreo integrado**: Logs y métricas centralizadas  
✅ **Backup automático**: Base de datos protegida  
✅ **CI/CD automatizado**: Despliegues con cada push  

### **Próximos Pasos Sugeridos**

1. 🔐 **Configurar autenticación de 2FA** para Admin
2. 📧 **Configurar alertas de monitoreo** 
3. 🌍 **Configurar dominio personalizado**
4. 📱 **Desplegar app móvil Flutter** (opcional)
5. 🤖 **Configurar notificaciones automáticas**

---

## 📞 Soporte

Si necesitas ayuda:

1. **Documentación oficial**: [Google Cloud Docs](https://cloud.google.com/docs)
2. **Firebase Docs**: [Firebase Documentation](https://firebase.google.com/docs)
3. **Community**: [Stack Overflow](https://stackoverflow.com/questions/tagged/google-cloud-platform)

¡Tu migración a GCP está completa y funcionando! 🚀
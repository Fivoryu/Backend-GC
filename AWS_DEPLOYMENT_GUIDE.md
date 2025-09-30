# Guía de Despliegue en AWS - Backend

## 🚀 Opciones de Despliegue en AWS

### 1. AWS Elastic Beanstalk (Recomendado - Más fácil)
- **Ventajas**: Configuración automática, escalado automático, fácil monitoreo
- **Ideal para**: Desarrollo y producción pequeña/mediana

### 2. AWS ECS con Docker (Avanzado)
- **Ventajas**: Máximo control, contenedores, microservicios
- **Ideal para**: Aplicaciones complejas, alta escala

### 3. AWS Lambda (Serverless)
- **Ventajas**: Sin servidores, pago por uso
- **Ideal para**: APIs simples, bajo tráfico

## 📋 Prerrequisitos

### 1. Instalar AWS CLI
```bash
# Windows (con Chocolatey)
choco install awscli

# O descargar desde: https://aws.amazon.com/cli/
```

### 2. Configurar credenciales AWS
```bash
aws configure
# AWS Access Key ID: [Tu Access Key]
# AWS Secret Access Key: [Tu Secret Key]
# Default region name: us-east-1
# Default output format: json
```

### 3. Instalar EB CLI
```bash
pip install awsebcli
```

## 🔧 Despliegue con Elastic Beanstalk

### Paso 1: Preparar el proyecto
```bash
cd condominium-api
```

### Paso 2: Ejecutar script de despliegue
```bash
# En Windows PowerShell
.\deploy-aws.ps1

# En Linux/Mac
chmod +x deploy-aws.sh
./deploy-aws.sh
```

### Paso 3: Configurar manualmente (si es necesario)

#### Inicializar EB
```bash
eb init
# Seleccionar región: us-east-1
# Seleccionar plataforma: Python 3.11
# Nombre de aplicación: condominium-backend
```

#### Crear entorno
```bash
eb create condominium-production
```

#### Configurar variables de entorno
```bash
eb setenv \
  SECRET_KEY="tu-secret-key-super-segura" \
  DEBUG=False \
  ALLOWED_HOSTS=".elasticbeanstalk.com" \
  DJANGO_SETTINGS_MODULE=config.aws_settings
```

#### Desplegar
```bash
eb deploy
```

## 🗄️ Configuración de Base de Datos (RDS)

### Opción 1: Desde EB Console
1. Ve a AWS Console > Elastic Beanstalk
2. Selecciona tu aplicación
3. Configuration > Database
4. Agrega RDS PostgreSQL

### Opción 2: RDS Independiente
1. Ve a AWS Console > RDS
2. Crea instancia PostgreSQL
3. Configura variables de entorno:
```bash
eb setenv \
  RDS_HOSTNAME=tu-rds-endpoint \
  RDS_DB_NAME=condominium \
  RDS_USERNAME=admin \
  RDS_PASSWORD=tu-password \
  RDS_PORT=5432
```

## 📁 Configuración de S3 (Archivos Estáticos)

### Paso 1: Crear bucket S3
```bash
aws s3 mb s3://condominium-static-files
```

### Paso 2: Configurar variables de entorno
```bash
eb setenv \
  AWS_STORAGE_BUCKET_NAME=condominium-static-files \
  AWS_ACCESS_KEY_ID=tu-access-key \
  AWS_SECRET_ACCESS_KEY=tu-secret-key \
  AWS_S3_REGION_NAME=us-east-1
```

## 🔒 Configuración de Seguridad

### 1. HTTPS/SSL
1. Ve a EB Console > Configuration > Load balancer
2. Agrega listener HTTPS:443
3. Sube certificado SSL o usa AWS Certificate Manager

### 2. Dominio Personalizado
1. Ve a Route 53
2. Crea zona hosted para tu dominio
3. Agrega registro CNAME apuntando a tu EB environment

### 3. Variables de Entorno de Producción
```bash
eb setenv \
  CORS_ALLOWED_ORIGINS=https://tu-frontend.vercel.app \
  ALLOWED_HOSTS=tu-dominio.com,.elasticbeanstalk.com
```

## 📊 Monitoreo y Logs

### Ver logs
```bash
eb logs
```

### Monitoreo en tiempo real
```bash
eb ssh
sudo tail -f /var/log/eb-engine.log
```

### CloudWatch
- Ve a AWS Console > CloudWatch
- Configura alertas para CPU, memoria, errores

## 🔄 Comandos Útiles

```bash
# Ver estado
eb status

# Ver información de la aplicación
eb list

# Conectar por SSH
eb ssh

# Configurar escalado automático
eb config

# Terminar entorno
eb terminate

# Ver configuración actual
eb config show
```

## 💰 Estimación de Costos

### Elastic Beanstalk (t3.micro)
- **Instancia EC2**: ~$8.5/mes
- **RDS db.t3.micro**: ~$12.5/mes
- **S3**: ~$1-5/mes (dependiendo del uso)
- **Total aproximado**: $22-26/mes

### Optimización de costos
- Usar instancias reservadas para producción
- Configurar auto-scaling para ajustar según demanda
- Usar CloudFront para archivos estáticos

## 🆘 Troubleshooting

### Error: Application health degraded
```bash
eb logs
# Revisar logs para identificar el problema
```

### Error de base de datos
```bash
# Verificar variables de entorno
eb printenv

# Ejecutar migraciones manualmente
eb ssh
cd /var/app/current
python manage.py migrate
```

### Error de archivos estáticos
```bash
# Recopilar archivos estáticos
eb ssh
cd /var/app/current
python manage.py collectstatic --noinput
```

## 📚 Recursos Adicionales

- [AWS Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [Django on AWS](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html)
- [AWS Free Tier](https://aws.amazon.com/free/)

## ✅ Checklist de Despliegue

- [ ] AWS CLI configurado
- [ ] EB CLI instalado
- [ ] Variables de entorno configuradas
- [ ] Base de datos RDS creada
- [ ] Bucket S3 configurado
- [ ] SSL/HTTPS configurado
- [ ] Dominio personalizado (opcional)
- [ ] Monitoreo configurado
- [ ] Backup configurado
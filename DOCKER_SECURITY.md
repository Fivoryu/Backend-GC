# Docker Security Configuration

## 🔒 Mejoras de Seguridad Implementadas

### 1. Imagen Base Segura
- **Imagen**: `python:3.11.10-slim-bookworm` (versión específica)
- **Beneficios**: Menor superficie de ataque, vulnerabilidades parcheadas

### 2. Usuario No-Root
- **Usuario**: `appuser` (no privilegiado)
- **Beneficios**: Previene escalación de privilegios

### 3. Dependencias con Versiones Fijas
- **PostgreSQL Client**: `15+248` 
- **libpq-dev**: `15.8-0+deb12u1`
- **Beneficios**: Evita vulnerabilidades conocidas

### 4. Optimizaciones de Contenedor
- **no-new-privileges**: Previene escalación de privilegios
- **read-only**: Filesystem de solo lectura para PostgreSQL
- **tmpfs**: Directorios temporales en memoria

### 5. Health Checks
- **Web**: Verifica endpoint `/api/`
- **Database**: Verifica conexión PostgreSQL
- **Nginx**: Verifica respuesta HTTP

### 6. Rate Limiting
- **API General**: 10 requests/segundo
- **Login**: 5 requests/minuto
- **Burst**: Permite picos controlados

### 7. Headers de Seguridad
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: restrictiva
Strict-Transport-Security: HSTS habilitado
```

### 8. Compresión y Performance
- **Gzip**: Habilitado para texto/JSON/CSS/JS
- **Keep-alive**: Conexiones persistentes
- **Worker connections**: Optimizado para carga

## 🛡️ Configuraciones de Producción

### Variables de Entorno Críticas
```bash
# Cambiar en producción
SECRET_KEY=your-super-secret-key-here-minimum-50-chars-long
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Base de datos segura
DB_PASSWORD=strong-password-here
```

### SSL/TLS (Para producción)
```bash
# Crear directorio SSL
mkdir ssl

# Copiar certificados
cp your-certificate.crt ssl/
cp your-private-key.key ssl/
```

### Firewall Recommendations
```bash
# Solo puertos necesarios
- 80 (HTTP)
- 443 (HTTPS)  
- 22 (SSH) - solo desde IPs específicas
```

## 🔍 Monitoreo y Logs

### Logs de Nginx
```bash
docker-compose logs nginx
```

### Logs de Aplicación
```bash
docker-compose logs web
```

### Verificar Health Checks
```bash
docker-compose ps
```

## ⚠️ Notas de Seguridad

1. **Cambiar contraseñas por defecto** antes de producción
2. **Usar HTTPS** en producción (configurar SSL)
3. **Firewall configurado** para limitar acceso
4. **Backups automáticos** de base de datos
5. **Monitoreo activo** de logs y métricas
6. **Actualizaciones regulares** de imágenes base

## 🧪 Testing de Seguridad

### Verificar Headers
```bash
curl -I http://localhost/
```

### Test de Rate Limiting
```bash
# Debería bloquearse después de varios requests
for i in {1..20}; do curl http://localhost/api/; done
```

### Verificar Usuario No-Root
```bash
docker exec -it container_name whoami
# Debería retornar: appuser
```
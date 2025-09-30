# Guía para Copiar Base de Datos Local a Docker

## 📋 Métodos Disponibles

### Método 1: Exportar/Importar Fixtures JSON (Recomendado)
**Ventajas**: Independiente del tipo de base de datos, fácil de usar
**Ideal para**: Migrar de SQLite a PostgreSQL

#### Pasos:
1. **Exportar datos actuales**:
```bash
# Exportar todos los datos como fixtures JSON
python export_fixtures.py
```

2. **Verificar fixtures generados**:
```bash
# Se crean archivos en fixtures/
ls fixtures/
```

3. **Desplegar con Docker**:
```bash
docker-compose up --build
```

Los fixtures se cargan automáticamente en el primer despliegue.

---

### Método 2: Backup SQL (Para PostgreSQL a PostgreSQL)
**Ventajas**: Backup completo con estructura y datos
**Ideal para**: Cuando ya usas PostgreSQL localmente

#### Windows:
```powershell
# Exportar base de datos
.\export_db.ps1 -DatabaseName "tu_db" -Username "postgres"

# Desplegar con Docker
docker-compose up --build
```

#### Linux/Mac:
```bash
# Exportar base de datos
chmod +x export_db.sh
./export_db.sh

# Desplegar con Docker
docker-compose up --build
```

---

### Método 3: Variables de Entorno
**Para generar datos de prueba en lugar de copiar**

```bash
# En docker-compose.yml, cambiar:
LOAD_INITIAL_DATA=true  # Genera 1911 registros de prueba
```

---

## 🔧 Configuración del Dockerfile

El Dockerfile modificado incluye:

1. **Espera a la base de datos**: Verifica que PostgreSQL esté listo
2. **Ejecuta migraciones**: Crea las tablas automáticamente  
3. **Crea superusuario**: Admin por defecto (admin/admin123)
4. **Carga datos**:
   - Si existe carpeta `fixtures/` → Carga fixtures JSON
   - Si `LOAD_INITIAL_DATA=true` → Genera datos de prueba
5. **Archivos estáticos**: Los recopila automáticamente
6. **Inicia servidor**: Gunicorn con 3 workers

## 📊 docker-compose.yml

```yaml
services:
  db:
    image: postgres:13
    # Datos se cargan en la aplicación, no en el contenedor DB
    
  web:
    build: .
    environment:
      - LOAD_INITIAL_DATA=false  # false para usar fixtures
      - DB_HOST=db
      # ... otras variables
```

## 🚀 Comandos Útiles

### Ver logs del contenedor:
```bash
docker-compose logs -f web
```

### Ejecutar comandos Django:
```bash
# Crear superusuario adicional
docker exec -it <container_name> python manage.py createsuperuser

# Cargar fixtures manualmente
docker exec -it <container_name> python manage.py loaddata fixtures/*.json

# Shell de Django
docker exec -it <container_name> python manage.py shell
```

### Backup desde contenedor:
```bash
# Exportar datos del contenedor
docker exec -it <container_name> python manage.py dumpdata > backup.json
```

## 🔍 Verificación

1. **Aplicación funcionando**: http://localhost:8000
2. **Admin panel**: http://localhost:8000/admin (admin/admin123)
3. **API**: http://localhost:8000/api/residentes/

## ⚠️ Consideraciones

### SQLite → PostgreSQL:
- Los IDs pueden cambiar
- Algunas fechas/horas pueden necesitar ajuste
- Los fixtures manejan las referencias automáticamente

### Producción:
- Cambiar contraseñas por defecto
- Usar variables de entorno seguras  
- Configurar backup automático

### Performance:
- Los fixtures pueden tardar unos minutos en cargarse
- El contenedor está listo cuando ves: "Iniciando servidor..."

## 🆘 Troubleshooting

### Error: "relation does not exist"
```bash
# Ejecutar migraciones manualmente
docker exec -it <container> python manage.py migrate --run-syncdb
```

### Error: "fixtures not found"
```bash
# Verificar que los fixtures estén en el contenedor
docker exec -it <container> ls fixtures/
```

### Base de datos no se conecta:
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose logs db
```

### Datos no aparecen:
```bash
# Verificar que se cargaron los fixtures
docker exec -it <container> python manage.py shell -c "from residentes.models import Residente; print(Residente.objects.count())"
```
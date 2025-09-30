#!/bin/bash
# Script para exportar base de datos local y preparar para Docker

# Configuración
LOCAL_DB_NAME="condominium_db"
LOCAL_DB_USER="postgres"
LOCAL_DB_HOST="localhost"
LOCAL_DB_PORT="5432"
BACKUP_FILE="database_backup.sql"

echo "=========================================="
echo "  EXPORTANDO BASE DE DATOS LOCAL"
echo "=========================================="

# Verificar que PostgreSQL esté disponible localmente
if ! command -v pg_dump &> /dev/null; then
    echo "Error: pg_dump no está disponible. Instala PostgreSQL client tools."
    exit 1
fi

# Crear backup de la base de datos local
echo "Creando backup de la base de datos local..."
pg_dump -h $LOCAL_DB_HOST -p $LOCAL_DB_PORT -U $LOCAL_DB_USER -d $LOCAL_DB_NAME \
    --clean --if-exists --no-owner --no-privileges > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Backup creado exitosamente: $BACKUP_FILE"
else
    echo "❌ Error al crear backup"
    exit 1
fi

# Crear script de importación para Docker
cat > import_db.sh << 'EOF'
#!/bin/bash
# Script para importar datos en contenedor Docker

echo "Esperando base de datos..."
while ! pg_isready -h ${DB_HOST:-db} -p ${DB_PORT:-5432} -U ${DB_USER:-postgres}; do
  echo "Esperando PostgreSQL..."
  sleep 2
done

echo "Importando datos de backup..."
psql -h ${DB_HOST:-db} -p ${DB_PORT:-5432} -U ${DB_USER:-postgres} -d ${DB_NAME:-condominium} < /app/database_backup.sql

if [ $? -eq 0 ]; then
    echo "✅ Datos importados exitosamente!"
else
    echo "❌ Error al importar datos"
fi
EOF

chmod +x import_db.sh

echo "=========================================="
echo "  ARCHIVOS GENERADOS"
echo "=========================================="
echo "📁 $BACKUP_FILE - Backup de la base de datos"
echo "📁 import_db.sh - Script de importación para Docker"
echo ""
echo "Para usar con Docker:"
echo "1. Copia estos archivos al directorio del proyecto"
echo "2. Modifica docker-compose.yml para usar el script de importación"
echo "3. Ejecuta: docker-compose up --build"
# Script para exportar base de datos local (Windows)
param(
    [string]$DatabaseName = "condominium_db",
    [string]$Username = "postgres", 
    [string]$Host = "localhost",
    [string]$Port = "5432",
    [string]$BackupFile = "database_backup.sql"
)

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  EXPORTANDO BASE DE DATOS LOCAL" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Verificar que pg_dump esté disponible
try {
    $null = Get-Command pg_dump -ErrorAction Stop
    Write-Host "PostgreSQL client tools encontrado ✅" -ForegroundColor Green
} catch {
    Write-Host "Error: pg_dump no está disponible. Instala PostgreSQL client tools." -ForegroundColor Red
    Write-Host "Descarga desde: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    exit 1
}

# Crear backup de la base de datos local
Write-Host "Creando backup de la base de datos: $DatabaseName" -ForegroundColor Yellow

$pgDumpArgs = @(
    "-h", $Host
    "-p", $Port  
    "-U", $Username
    "-d", $DatabaseName
    "--clean"
    "--if-exists"
    "--no-owner"
    "--no-privileges"
)

try {
    pg_dump @pgDumpArgs | Out-File -FilePath $BackupFile -Encoding UTF8
    Write-Host "✅ Backup creado exitosamente: $BackupFile" -ForegroundColor Green
} catch {
    Write-Host "❌ Error al crear backup: $_" -ForegroundColor Red
    exit 1
}

# Crear script de importación para Docker
$importScript = @'
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
'@

$importScript | Out-File -FilePath "import_db.sh" -Encoding UTF8

# Crear docker-compose con importación de datos
$dockerCompose = @'
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: condominium
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    environment:
      - LOAD_INITIAL_DATA=false  # false porque usaremos el backup
      - DB_HOST=db
      - DB_NAME=condominium
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - DB_PORT=5432
    ports:
      - "8000:8000"
    depends_on:
      - db
    volumes:
      - .:/app
    # Importar datos después de que el contenedor esté listo
    command: >
      sh -c "
        /app/entrypoint.sh gunicorn --bind 0.0.0.0:8000 config.wsgi:application &
        sleep 10 &&
        /app/import_db.sh &&
        wait
      "

volumes:
  postgres_data:
'@

$dockerCompose | Out-File -FilePath "docker-compose.yml" -Encoding UTF8

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  ARCHIVOS GENERADOS" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "📁 $BackupFile - Backup de la base de datos" -ForegroundColor Cyan
Write-Host "📁 import_db.sh - Script de importación para Docker" -ForegroundColor Cyan
Write-Host "📁 docker-compose.yml - Configuración Docker con importación" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para usar con Docker:" -ForegroundColor Yellow
Write-Host "1. docker-compose up --build" -ForegroundColor White
Write-Host "2. Espera a que se complete la importación" -ForegroundColor White
Write-Host "3. La aplicación estará disponible en http://localhost:8000" -ForegroundColor White

$confirm = Read-Host "¿Quieres ejecutar docker-compose up --build ahora? (y/n)"
if ($confirm -eq "y" -or $confirm -eq "Y") {
    docker-compose up --build
}
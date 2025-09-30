# Dockerfile para AWS ECS con datos iniciales
FROM python:3.11-slim

# Configurar variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear script de inicialización
RUN echo '#!/bin/bash\n\
echo "Iniciando aplicación..."\n\
echo "Esperando base de datos..."\n\
while ! pg_isready -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -U ${DB_USER:-postgres}; do\n\
  echo "Esperando PostgreSQL..."\n\
  sleep 2\n\
done\n\
echo "Base de datos disponible!"\n\
\n\
echo "Ejecutando migraciones..."\n\
python manage.py migrate --noinput\n\
\n\
echo "Creando superusuario si no existe..."\n\
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username=\"admin\").exists() or User.objects.create_superuser(\"admin\", \"admin@example.com\", \"admin123\")"\n\
\n\
echo "Cargando datos iniciales..."\n\
if [ "$LOAD_INITIAL_DATA" = "true" ]; then\n\
  echo "Ejecutando populate_database.py..."\n\
  python populate_database.py\n\
  echo "Datos iniciales cargados!"\n\
elif [ -d "fixtures" ] && [ "$(ls -A fixtures)" ]; then\n\
  echo "Cargando fixtures desde carpeta fixtures/..."\n\
  python manage.py loaddata fixtures/*.json\n\
  echo "Fixtures cargados!"\n\
fi\n\
\n\
echo "Recopilando archivos estáticos..."\n\
python manage.py collectstatic --noinput\n\
\n\
echo "Iniciando servidor..."\n\
exec "$@"' > /app/entrypoint.sh

# Hacer el script ejecutable
RUN chmod +x /app/entrypoint.sh

# Exponer puerto
EXPOSE 8000

# Usar entrypoint personalizado
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando por defecto
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
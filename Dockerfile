# Dockerfile para AWS ECS con datos iniciales
FROM python:3.11.10-slim-bookworm

# Configurar variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dockerfile para AWS ECS con datos iniciales - Optimizado y Seguro
FROM python:3.11.10-slim-bookworm

# Configurar variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalar dependencias del sistema con optimizaciones de seguridad
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client=15+248 \
        build-essential \
        libpq-dev=15.8-0+deb12u1 \
        curl \
        ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Crear directorio de trabajo y cambiar propietario
WORKDIR /app
RUN chown appuser:appuser /app

# Copiar requirements como usuario root, instalar dependencias y cambiar a usuario no-root
COPY --chown=appuser:appuser requirements.txt .

# Instalar dependencias Python con optimizaciones de seguridad
RUN pip install --no-cache-dir --upgrade pip==24.2 \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf ~/.cache/pip

# Cambiar a usuario no-root
USER appuser

# Copiar código de la aplicación
COPY --chown=appuser:appuser . .

# Crear script de inicialización con usuario no-root
USER root
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🚀 Iniciando aplicación Condominium Management System..."\n\
echo "⏳ Esperando base de datos..."\n\
while ! pg_isready -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -U ${DB_USER:-postgres} -q; do\n\
  echo "⏳ Esperando PostgreSQL... ($(date))"\n\
  sleep 3\n\
done\n\
echo "✅ Base de datos disponible!"\n\
\n\
echo "📋 Ejecutando migraciones..."\n\
python manage.py migrate --noinput\n\
\n\
echo "👤 Creando superusuario si no existe..."\n\
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='"'"'admin'"'"').exists() or User.objects.create_superuser('"'"'admin'"'"', '"'"'admin@example.com'"'"', '"'"'admin123'"'"')"\n\
\n\
echo "📊 Cargando datos iniciales..."\n\
if [ "$LOAD_INITIAL_DATA" = "true" ]; then\n\
  echo "🎲 Ejecutando populate_database.py..."\n\
  python populate_database.py\n\
  echo "✅ Datos de prueba cargados (1911 registros)!"\n\
elif [ -d "fixtures" ] && [ "$(ls -A fixtures 2>/dev/null)" ]; then\n\
  echo "📦 Cargando fixtures desde carpeta fixtures/..."\n\
  python manage.py loaddata fixtures/*.json\n\
  echo "✅ Fixtures cargados!"\n\
else\n\
  echo "ℹ️  No se encontraron datos para cargar. Usando base de datos vacía."\n\
fi\n\
\n\
echo "🎨 Recopilando archivos estáticos..."\n\
python manage.py collectstatic --noinput\n\
\n\
echo "🌟 Aplicación lista! Iniciando servidor..."\n\
echo "🔗 Acceso: http://localhost:8000"\n\
echo "🔑 Admin: http://localhost:8000/admin (admin/admin123)"\n\
exec "$@"' > /app/entrypoint.sh

# Hacer el script ejecutable y cambiar propietario
RUN chmod +x /app/entrypoint.sh \
    && chown appuser:appuser /app/entrypoint.sh

# Cambiar de vuelta a usuario no-root
USER appuser

# Configurar health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/ || exit 1

# Exponer puerto
EXPOSE 8000

# Usar entrypoint personalizado
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando por defecto optimizado
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--worker-class", "gevent", "--worker-connections", "1000", "--max-requests", "1000", "--max-requests-jitter", "100", "--timeout", "30", "--keep-alive", "2", "config.wsgi:application"]
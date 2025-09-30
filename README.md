# Condominium Management System - Backend API

Sistema de gestión de condominios desarrollado con Django REST Framework.

## 🚀 Características

- **Gestión de Residentes**: Registro y administración de propietarios/inquilinos
- **Control de Mascotas**: Registro de mascotas por residente
- **Gestión de Vehículos**: Control de vehículos de residentes
- **Sistema de Visitantes**: Registro de visitas con control de acceso
- **Autenticación JWT**: Sistema seguro de autenticación
- **API REST**: Endpoints completos para todas las funcionalidades

## 🛠️ Tecnologías

- **Python 3.11+**
- **Django 5.2.6**
- **Django REST Framework**
- **JWT Authentication**
- **PostgreSQL** (producción) / **SQLite** (desarrollo)

## ⚙️ Instalación

### Prerrequisitos
- Python 3.11 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/Fivoryu/Backend-GC.git
cd Backend-GC
```

2. **Crear entorno virtual**
```bash
python -m venv venv
```

3. **Activar entorno virtual**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Configurar variables de entorno**
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones
```

6. **Ejecutar migraciones**
```bash
python manage.py migrate
```

7. **Crear superusuario**
```bash
python manage.py createsuperuser
```

8. **Cargar datos de prueba (opcional)**
```bash
python populate_database.py
```

9. **Ejecutar servidor**
```bash
python manage.py runserver
```

## 📋 API Endpoints

### Autenticación
- `POST /api/auth/login/` - Iniciar sesión
- `POST /api/auth/logout/` - Cerrar sesión
- `POST /api/auth/refresh/` - Renovar token

### Residentes
- `GET /api/residentes/` - Listar residentes
- `POST /api/residentes/` - Crear residente
- `GET /api/residentes/{id}/` - Detalle de residente
- `PUT /api/residentes/{id}/` - Actualizar residente
- `DELETE /api/residentes/{id}/` - Eliminar residente

### Mascotas
- `GET /api/mascotas/` - Listar mascotas
- `POST /api/mascotas/` - Registrar mascota
- `GET /api/mascotas/{id}/` - Detalle de mascota
- `PUT /api/mascotas/{id}/` - Actualizar mascota
- `DELETE /api/mascotas/{id}/` - Eliminar mascota

### Vehículos
- `GET /api/vehiculos/` - Listar vehículos
- `POST /api/vehiculos/` - Registrar vehículo
- `GET /api/vehiculos/{id}/` - Detalle de vehículo
- `PUT /api/vehiculos/{id}/` - Actualizar vehículo
- `DELETE /api/vehiculos/{id}/` - Eliminar vehículo

### Visitantes
- `GET /api/visitantes/` - Listar visitantes
- `POST /api/visitantes/` - Registrar visitante
- `GET /api/visitantes/{id}/` - Detalle de visitante
- `PUT /api/visitantes/{id}/` - Actualizar visitante
- `DELETE /api/visitantes/{id}/` - Eliminar visitante

## 🔧 Configuración

### Variables de Entorno

Crear un archivo `.env` basado en `.env.example`:

```env
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Para Producción

```env
SECRET_KEY=clave_secreta_produccion
DEBUG=False
DATABASE_URL=postgresql://usuario:password@host:puerto/database
ALLOWED_HOSTS=tu-dominio.com
CORS_ALLOWED_ORIGINS=https://tu-frontend.com
```

## 🚀 Despliegue

### Railway
1. Conectar repositorio a Railway
2. Configurar variables de entorno
3. El `Procfile` está incluido para el despliegue automático

### Heroku
1. Crear app en Heroku
2. Conectar repositorio
3. Configurar variables de entorno
4. El `Procfile` está incluido

## 📝 Estructura del Proyecto

```
condominium-api/
├── apps/
│   ├── areas/           # Gestión de áreas comunes
│   ├── cuentas/         # Sistema de autenticación
│   ├── personal/        # Gestión de personal
│   ├── reserva_pagos/   # Reservas y pagos
│   ├── residentes/      # Gestión de residentes
│   └── vision_artificial/ # IA para reconocimiento
├── config/              # Configuración de Django
├── manage.py
├── requirements.txt
└── Procfile
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Autores

- **Tu Nombre** - *Desarrollo inicial* - [Fivoryu](https://github.com/Fivoryu)

## 🆘 Soporte

Si tienes problemas o preguntas, por favor:
1. Revisa la documentación
2. Busca en los issues existentes
3. Crea un nuevo issue si es necesario
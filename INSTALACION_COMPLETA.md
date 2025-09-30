# 🏢 Condominium API - Instalación y Configuración Completa

## ✅ Estado de la Instalación

**¡La instalación del backend se completó exitosamente!**

### 🔧 Componentes Instalados

- ✅ **Entorno Virtual Python** activado
- ✅ **Django 5.2.6** con todas las dependencias
- ✅ **PostgreSQL** conectado y configurado
- ✅ **Base de datos** `condominium_db` creada
- ✅ **Migraciones** aplicadas (todas las tablas creadas)
- ✅ **Superusuario** creado (admin@gmail.com)
- ✅ **Datos iniciales** cargados
- ✅ **Servidor de desarrollo** funcionando

---

## 🚀 Cómo Usar el Sistema

### 1. **Activar el Entorno Virtual**
```powershell
cd "d:\Universidad\Prácticos\Séptimo Semestre\Sistemas de Información II\1er Parcial\condominium-api"
.\venv\Scripts\activate
```

### 2. **Iniciar el Servidor**
```powershell
python manage.py runserver
```

### 3. **URLs Principales**

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **API Principal** | http://127.0.0.1:8000/ | Redirección al admin |
| **Panel Admin** | http://127.0.0.1:8000/admin/ | Panel administrativo |
| **API Docs** | http://127.0.0.1:8000/api/ | Endpoints de la API |

### 4. **Credenciales del Superusuario**
- **Email:** admin@gmail.com
- **Contraseña:** admin123

---

## 📋 Datos Preinstalados

### **Roles del Sistema:**
- Administrador
- Supervisor  
- Residente
- Personal de Seguridad
- Personal de Mantenimiento
- Personal de Limpieza

### **Residencias de Ejemplo:**
- 101, 102, 201 (Apartamentos)
- 301, 302 (Casas)

### **Áreas Comunes:**
- Piscina (Reserva: Bs. 50)
- Salón de Eventos (Reserva: Bs. 200)
- Gimnasio (Gratis)
- Cancha de Tenis (Reserva: Bs. 30)

### **Conceptos de Pago:**
- Mantenimiento Mensual (Bs. 150)
- Servicios Básicos (Bs. 80)
- Seguridad (Bs. 100)
- Y más...

---

## 🛠️ Comandos Útiles de Django

### **Gestión de Migraciones:**
```powershell
# Crear nuevas migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ver estado de migraciones
python manage.py showmigrations
```

### **Gestión de Usuarios:**
```powershell
# Crear superusuario
python manage.py createsuperuser

# Cambiar contraseña de usuario
python manage.py changepassword admin@gmail.com
```

### **Utilidades:**
```powershell
# Verificar configuración
python manage.py check

# Abrir shell de Django
python manage.py shell

# Cargar datos iniciales (si es necesario)
python load_initial_data.py
```

---

## 📡 Endpoints de la API

### **Autenticación:**
- `POST /api/cuenta/token/` - Login (JWT)
- `POST /api/cuenta/logout/` - Logout
- `GET /api/cuenta/perfil/` - Perfil del usuario
- `POST /api/cuenta/registro/` - Registro de usuario

### **Gestión:**
- `/api/cuenta/usuarios/` - CRUD Usuarios
- `/api/cuenta/roles/` - CRUD Roles
- `/api/residentes/` - CRUD Residentes
- `/api/personal/` - CRUD Personal
- `/api/areas/` - CRUD Áreas comunes
- `/api/reservas/` - CRUD Reservas
- `/api/vision/` - Reconocimiento facial/placas

---

## 🔧 Configuración de Variables de Entorno

El archivo `.env` está configurado con:
- ✅ Conexión a PostgreSQL
- ✅ Configuraciones de Django
- ⚠️ **Pendiente:** Configuraciones opcionales (Cloudinary, Stripe, Email)

### **Para Configurar Servicios Externos:**

#### **Cloudinary (Almacenamiento de Imágenes):**
```env
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-api-key
CLOUDINARY_API_SECRET=tu-api-secret
```

#### **Stripe (Pagos):**
```env
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

#### **Email (Brevo/SendinBlue):**
```env
EMAIL_HOST_USER=tu-email@ejemplo.com
EMAIL_HOST_PASSWORD=tu-password
BREVO_API_KEY=tu-api-key
```

---

## 🔍 Verificación de la Instalación

### **1. Servidor Funcionando:**
- Ve a: http://127.0.0.1:8000/
- Deberías ver una redirección al panel admin

### **2. Panel Admin Accesible:**
- Ve a: http://127.0.0.1:8000/admin/
- Inicia sesión con admin@gmail.com

### **3. Base de Datos Poblada:**
- En el admin, verifica que hay:
  - 6 Roles
  - 5 Residencias  
  - 4 Áreas comunes
  - 7 Conceptos de pago

---

## 🚨 Solución de Problemas

### **Error de Conexión a PostgreSQL:**
```powershell
# Verificar que PostgreSQL está corriendo
# Verificar credenciales en .env
# Verificar que la base de datos condominium_db existe
```

### **Error de Migraciones:**
```powershell
python manage.py migrate --fake-initial
```

### **Error de Dependencias:**
```powershell
pip install -r requirements.txt
```

---

## 🎯 Próximos Pasos

1. **Configurar servicios externos** (Cloudinary, Stripe, Email)
2. **Conectar con el frontend** (React/Vue)
3. **Configurar la app móvil** (Flutter)
4. **Realizar pruebas de la API**
5. **Configurar para producción**

---

## 📞 Información de Contacto

- **Proyecto:** Sistema de Gestión de Condominios
- **Framework:** Django 5.2.6 + PostgreSQL 17
- **Fecha:** Septiembre 30, 2025

---

¡El backend está completamente funcional y listo para usar! 🎉
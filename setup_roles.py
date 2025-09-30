#!/usr/bin/env python
"""
Script para configurar roles iniciales y asignar rol admin al superusuario
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cuentas.models import Usuario, Rol

def crear_roles_iniciales():
    """Crear los roles básicos del sistema"""
    roles_iniciales = [
        'Admin',
        'Administrador', 
        'Residente',
        'Personal',
        'Seguridad'
    ]
    
    print("🔧 Creando roles iniciales...")
    
    for nombre_rol in roles_iniciales:
        rol, creado = Rol.objects.get_or_create(nombre=nombre_rol)
        if creado:
            print(f"✅ Rol '{nombre_rol}' creado")
        else:
            print(f"ℹ️  Rol '{nombre_rol}' ya existe")
    
    return True

def asignar_rol_admin():
    """Asignar rol Admin al superusuario"""
    try:
        # Buscar el rol Admin
        rol_admin = Rol.objects.get(nombre='Admin')
        
        # Buscar usuarios superusuarios sin rol
        superusuarios = Usuario.objects.filter(is_superuser=True, rol__isnull=True)
        
        if superusuarios.exists():
            print(f"👤 Encontrados {superusuarios.count()} superusuarios sin rol")
            
            for usuario in superusuarios:
                usuario.rol = rol_admin
                usuario.save()
                print(f"✅ Rol 'Admin' asignado a {usuario.correo}")
        else:
            print("ℹ️  No hay superusuarios sin rol")
            
        # Mostrar todos los usuarios con rol Admin
        admins = Usuario.objects.filter(rol__nombre='Admin')
        print(f"\n👑 Usuarios con rol Admin ({admins.count()}):")
        for admin in admins:
            print(f"  - {admin.correo}")
            
    except Rol.DoesNotExist:
        print("❌ Error: Rol 'Admin' no encontrado")
        return False
    
    return True

def mostrar_estado():
    """Mostrar el estado actual de usuarios y roles"""
    print("\n📊 Estado actual del sistema:")
    print(f"  Total usuarios: {Usuario.objects.count()}")
    print(f"  Total roles: {Rol.objects.count()}")
    
    print("\n🎭 Roles disponibles:")
    for rol in Rol.objects.all():
        count = rol.usuarios.count()
        print(f"  - {rol.nombre}: {count} usuarios")

def main():
    print("🚀 Configurando roles iniciales del sistema...")
    print("=" * 50)
    
    # Crear roles
    if crear_roles_iniciales():
        print("✅ Roles creados correctamente")
    else:
        print("❌ Error creando roles")
        return
    
    # Asignar rol admin
    if asignar_rol_admin():
        print("✅ Roles asignados correctamente")
    else:
        print("❌ Error asignando roles")
        return
    
    # Mostrar estado
    mostrar_estado()
    
    print("\n🎉 Configuración completada!")

if __name__ == "__main__":
    main()
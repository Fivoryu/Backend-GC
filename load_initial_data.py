"""
Script para cargar datos iniciales en la base de datos del condominio
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cuentas.models import Rol, Usuario
from apps.residentes.models import Residencia, Residente
from apps.personal.models import Personal
from apps.areas.models import AreaComun, Horario
from apps.reserva_pagos.models import ConceptoPago

def crear_roles():
    """Crear roles básicos del sistema"""
    roles = [
        'Administrador',
        'Supervisor', 
        'Residente',
        'Personal de Seguridad',
        'Personal de Mantenimiento',
        'Personal de Limpieza'
    ]
    
    for rol_nombre in roles:
        rol, created = Rol.objects.get_or_create(nombre=rol_nombre)
        if created:
            print(f"✅ Rol creado: {rol_nombre}")
        else:
            print(f"ℹ️  Rol ya existe: {rol_nombre}")

def crear_residencias():
    """Crear algunas residencias de ejemplo"""
    residencias_data = [
        {"numero": 101, "direccion": "Edificio A - Piso 1", "tipo": "APARTAMENTO", "num_habitaciones": 2},
        {"numero": 102, "direccion": "Edificio A - Piso 1", "tipo": "APARTAMENTO", "num_habitaciones": 3},
        {"numero": 201, "direccion": "Edificio A - Piso 2", "tipo": "APARTAMENTO", "num_habitaciones": 2},
        {"numero": 301, "direccion": "Edificio B - Piso 1", "tipo": "CASA", "num_habitaciones": 4},
        {"numero": 302, "direccion": "Edificio B - Piso 1", "tipo": "CASA", "num_habitaciones": 3},
    ]
    
    for residencia_data in residencias_data:
        residencia, created = Residencia.objects.get_or_create(**residencia_data)
        if created:
            print(f"✅ Residencia creada: {residencia.numero}")
        else:
            print(f"ℹ️  Residencia ya existe: {residencia.numero}")

def crear_areas_comunes():
    """Crear áreas comunes básicas"""
    areas_data = [
        {
            "nombre": "Piscina",
            "descripcion": "Piscina recreativa para residentes",
            "requiere_reserva": True,
            "capacidad_maxima": 20,
            "costo_reserva": 50.00,
            "tiempo_reserva_minima": 60,
            "tiempo_reserva_maxima": 240
        },
        {
            "nombre": "Salón de Eventos",
            "descripcion": "Salón para celebraciones y eventos",
            "requiere_reserva": True,
            "capacidad_maxima": 50,
            "costo_reserva": 200.00,
            "tiempo_reserva_minima": 120,
            "tiempo_reserva_maxima": 480
        },
        {
            "nombre": "Gimnasio",
            "descripcion": "Gimnasio con equipos básicos",
            "requiere_reserva": False,
            "capacidad_maxima": 15,
            "costo_reserva": 0.00
        },
        {
            "nombre": "Cancha de Tenis",
            "descripcion": "Cancha de tenis para uso recreativo",
            "requiere_reserva": True,
            "capacidad_maxima": 4,
            "costo_reserva": 30.00,
            "tiempo_reserva_minima": 60,
            "tiempo_reserva_maxima": 120
        }
    ]
    
    for area_data in areas_data:
        area, created = AreaComun.objects.get_or_create(
            nombre=area_data["nombre"],
            defaults=area_data
        )
        if created:
            print(f"✅ Área común creada: {area.nombre}")
        else:
            print(f"ℹ️  Área común ya existe: {area.nombre}")

def crear_conceptos_pago():
    """Crear conceptos de pago básicos"""
    conceptos = [
        {"nombre": "Mantenimiento Mensual", "monto": 150.00},
        {"nombre": "Servicios Básicos", "monto": 80.00},
        {"nombre": "Seguridad", "monto": 100.00},
        {"nombre": "Limpieza", "monto": 50.00},
        {"nombre": "Reserva de Piscina", "monto": 50.00},
        {"nombre": "Reserva de Salón", "monto": 200.00},
        {"nombre": "Multa por Ruido", "monto": 100.00},
    ]
    
    for concepto_data in conceptos:
        concepto, created = ConceptoPago.objects.get_or_create(**concepto_data)
        if created:
            print(f"✅ Concepto de pago creado: {concepto.nombre}")
        else:
            print(f"ℹ️  Concepto de pago ya existe: {concepto.nombre}")

def main():
    print("🚀 Iniciando carga de datos iniciales...")
    print("\n📋 Creando roles...")
    crear_roles()
    
    print("\n🏠 Creando residencias...")
    crear_residencias()
    
    print("\n🏛️ Creando áreas comunes...")
    crear_areas_comunes()
    
    print("\n💰 Creando conceptos de pago...")
    crear_conceptos_pago()
    
    print("\n✅ ¡Datos iniciales cargados exitosamente!")
    print("\n📊 Resumen:")
    print(f"   - Roles: {Rol.objects.count()}")
    print(f"   - Residencias: {Residencia.objects.count()}")
    print(f"   - Áreas comunes: {AreaComun.objects.count()}")
    print(f"   - Conceptos de pago: {ConceptoPago.objects.count()}")
    print(f"   - Usuarios: {Usuario.objects.count()}")

if __name__ == "__main__":
    main()
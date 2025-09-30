# Script para exportar SOLO datos (sin estructura) desde SQLite a PostgreSQL
import os
import django
import json
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def export_data():
    """Exporta todos los datos como fixtures JSON"""
    print("Exportando datos de la base de datos actual...")
    
    # Crear directorio de fixtures si no existe
    os.makedirs('fixtures', exist_ok=True)
    
    # Apps y modelos a exportar
    apps_to_export = [
        'auth.User',
        'auth.Group', 
        'cuentas.Usuario',
        'residentes.Residente',
        'residentes.Residencia',
        'residentes.Mascota',
        'residentes.Vehiculo',
        'residentes.Visitante',
        'areas.AreaComun',
        'personal.Personal',
        'reserva_pagos.Reserva',
        'reserva_pagos.Factura'
    ]
    
    for app_model in apps_to_export:
        try:
            filename = f"fixtures/{app_model.replace('.', '_')}.json"
            print(f"Exportando {app_model} -> {filename}")
            
            execute_from_command_line([
                'manage.py', 'dumpdata', 
                app_model,
                '--format=json',
                '--indent=2',
                f'--output={filename}'
            ])
            
        except Exception as e:
            print(f"Error exportando {app_model}: {e}")
    
    print("✅ Exportación completada!")
    print("📁 Los archivos están en la carpeta 'fixtures/'")
    print("")
    print("Para cargar en Docker:")
    print("1. Los fixtures se cargarán automáticamente en el primer deploy")
    print("2. O ejecuta: docker exec -it <container> python manage.py loaddata fixtures/*.json")

if __name__ == "__main__":
    export_data()
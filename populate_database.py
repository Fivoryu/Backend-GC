#!/usr/bin/env python
"""
Script para poblar la base de datos del sistema de condominios con datos realistas
Genera más de 1000 registros usando datos CASE (Computer-Aided Software Engineering)
"""
import os
import sys
import django
import random
from datetime import datetime, date, timedelta
from decimal import Decimal

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Instalar faker si no está disponible
try:
    from faker import Faker
except ImportError:
    print("🔧 Instalando faker...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "faker"])
    from faker import Faker

from django.contrib.auth.hashers import make_password
from apps.cuentas.models import Usuario, Rol, Bitacora, Aviso
from apps.residentes.models import Residencia, Residente, Mascota, Vehiculo, Visitante
from apps.areas.models import AreaComun, Regla
from apps.personal.models import Personal, Tarea
from apps.reserva_pagos.models import Reserva, ConceptoPago, Factura, Pago

# Configurar Faker para español
fake = Faker('es_ES')
Faker.seed(42)  # Para reproducibilidad

class CondominiumDataGenerator:
    def __init__(self):
        self.residencias = []
        self.residentes = []
        self.personal = []
        self.areas_comunes = []
        self.usuarios = []
        self.conceptos_pago = []
        
        print("🏗️ Iniciando generador de datos para Condominium System")
        print("=" * 60)

    def crear_residencias(self, cantidad=150):
        """Crear residencias (apartamentos y casas)"""
        print(f"🏠 Creando {cantidad} residencias...")
        
        # Limpiar residencias existentes
        Residencia.objects.all().delete()
        
        residencias = []
        for i in range(1, cantidad + 1):
            tipo = random.choice(['APARTAMENTO', 'CASA'])
            num_habitaciones = random.randint(1, 5)
            
            # Direcciones realistas
            if tipo == 'APARTAMENTO':
                direccion = f"Torre {random.choice(['A', 'B', 'C', 'D'])}, Piso {random.randint(1, 20)}, Apt {i}"
            else:
                direccion = f"Casa {i}, Sector {random.choice(['Norte', 'Sur', 'Este', 'Oeste'])}"
            
            residencia = Residencia(
                numero=i,
                direccion=direccion,
                tipo=tipo,
                num_habitaciones=num_habitaciones,
                num_residentes=0  # Se actualizará después
            )
            residencias.append(residencia)
        
        self.residencias = Residencia.objects.bulk_create(residencias)
        print(f"✅ {len(self.residencias)} residencias creadas")

    def crear_residentes(self, cantidad=400):
        """Crear residentes realistas"""
        print(f"👥 Creando {cantidad} residentes...")
        
        Residente.objects.all().delete()
        
        residentes = []
        cedulas_usadas = set()
        
        for i in range(cantidad):
            # Generar cédula única
            while True:
                cedula = fake.random_int(min=10000000, max=99999999)
                if cedula not in cedulas_usadas:
                    cedulas_usadas.add(cedula)
                    break
            
            # Datos realistas
            sexo = random.choice(['M', 'F'])
            nombre = fake.first_name_male() if sexo == 'M' else fake.first_name_female()
            apellidos = f"{fake.last_name()} {fake.last_name()}"
            
            # Edad realista (18-85 años)
            edad = random.randint(18, 85)
            fecha_nacimiento = date.today() - timedelta(days=edad * 365 + random.randint(0, 365))
            
            # Tipo de residente según probabilidades reales
            tipo = random.choices(
                ['PROPIETARIO', 'INQUILINO', 'FAMILIAR_PROPIETARIO', 'FAMILIAR_INQUILINO', 'OTRO'],
                weights=[40, 30, 15, 10, 5]
            )[0]
            
            # Asignar residencia
            residencia = random.choice(self.residencias)
            
            residente = Residente(
                nombre=nombre,
                apellidos=apellidos,
                fecha_nacimiento=fecha_nacimiento,
                telefono=fake.phone_number()[:15],
                correo=fake.email(),
                dni=str(cedula),
                sexo=sexo,
                tipo=tipo,
                residencia=residencia,
                foto_perfil=f"https://picsum.photos/200/200?random={i}",
                activo=random.choice([True, True, True, False])  # 75% activos
            )
            residentes.append(residente)
        
        self.residentes = Residente.objects.bulk_create(residentes)
        
        # Actualizar conteo de residentes por residencia
        for residencia in self.residencias:
            residencia.num_residentes = residencia.residentes.count()
            residencia.save()
        
        print(f"✅ {len(self.residentes)} residentes creados")

    def crear_personal(self, cantidad=25):
        """Crear personal del condominio"""
        print(f"👷 Creando {cantidad} miembros del personal...")
        
        Personal.objects.all().delete()
        
        personal_list = []
        cedulas_usadas = set()
        
        # Distribución realista de puestos
        puestos_distribucion = [
            ('ADMINISTRADOR', 2),
            ('SUPERVISOR', 3),
            ('SEGURIDAD', 8),
            ('MANTENIMIENTO', 6),
            ('LIMPIEZA', 5),
            ('OTRO', 1)
        ]
        
        contador = 0
        for puesto, cantidad_puesto in puestos_distribucion:
            for _ in range(cantidad_puesto):
                if contador >= cantidad:
                    break
                
                # Generar cédula única
                while True:
                    cedula = fake.random_int(min=10000000, max=99999999)
                    if cedula not in cedulas_usadas:
                        cedulas_usadas.add(cedula)
                        break
                
                # Fecha de contratación realista (últimos 10 años)
                fecha_contratacion = fake.date_between(start_date='-10y', end_date='today')
                
                # Algunos empleados ya no están activos
                activo = random.choice([True, True, True, True, False])  # 80% activos
                fecha_salida = None
                if not activo:
                    fecha_salida = fake.date_between(start_date=fecha_contratacion, end_date='today')
                
                personal = Personal(
                    nombre=fake.first_name(),
                    apellido=f"{fake.last_name()} {fake.last_name()}",
                    dni=str(cedula),
                    fecha_nacimiento=fake.date_of_birth(minimum_age=18, maximum_age=65),
                    telefono=fake.phone_number()[:15],
                    correo=fake.email(),
                    direccion=fake.address()[:150],
                    fecha_contratacion=fecha_contratacion,
                    puesto=puesto,
                    activo=activo,
                    fecha_salida=fecha_salida
                )
                personal_list.append(personal)
                contador += 1
        
        self.personal = Personal.objects.bulk_create(personal_list)
        print(f"✅ {len(self.personal)} miembros del personal creados")

    def crear_areas_comunes(self):
        """Crear áreas comunes del condominio"""
        print("🏛️ Creando áreas comunes...")
        
        AreaComun.objects.all().delete()
        
        areas_data = [
            # Áreas recreativas
            ('Piscina Principal', 'Piscina olímpica con área de descanso', True, 50, 25.00, 120, 480),
            ('Piscina Infantil', 'Piscina para niños menores de 12 años', True, 15, 15.00, 60, 240),
            ('Cancha de Tenis', 'Cancha profesional de tenis', True, 4, 30.00, 60, 180),
            ('Cancha de Fútbol', 'Cancha de fútbol 7', True, 14, 40.00, 90, 240),
            ('Cancha de Básquet', 'Cancha de baloncesto', True, 10, 20.00, 60, 180),
            ('Gimnasio', 'Gimnasio con equipos modernos', True, 20, 15.00, 60, 120),
            ('Salón de Eventos', 'Salón para celebraciones y reuniones', True, 100, 150.00, 240, 720),
            ('Salón de Juegos', 'Área de juegos para niños', False, 30, 0, None, None),
            ('BBQ Area Norte', 'Zona de parrillas sector norte', True, 20, 35.00, 120, 360),
            ('BBQ Area Sur', 'Zona de parrillas sector sur', True, 20, 35.00, 120, 360),
            
            # Áreas de servicios
            ('Lavandería Comunitaria', 'Lavadoras y secadoras compartidas', False, 8, 0, None, None),
            ('Parqueadero Visitantes', 'Estacionamiento para visitantes', False, 50, 0, None, None),
            ('Zona WiFi', 'Área con internet gratuito', False, 25, 0, None, None),
            ('Jardín Central', 'Jardín principal del condominio', False, None, 0, None, None),
            ('Mirador', 'Terraza con vista panorámica', False, 15, 0, None, None),
            
            # Áreas administrativas
            ('Sala de Reuniones', 'Sala para reuniones de propietarios', True, 50, 50.00, 120, 480),
            ('Oficina Administración', 'Oficina principal de administración', False, 5, 0, None, None),
            ('Recepción', 'Área de recepción y portería', False, None, 0, None, None),
        ]
        
        areas = []
        for nombre, descripcion, requiere_reserva, capacidad, costo, tiempo_min, tiempo_max in areas_data:
            estado = random.choices(
                ['disponible', 'mantenimiento', 'cerrado'],
                weights=[85, 10, 5]
            )[0]
            
            area = AreaComun(
                nombre=nombre,
                descripcion=descripcion,
                requiere_reserva=requiere_reserva,
                capacidad_maxima=capacidad,
                costo_reserva=Decimal(str(costo)) if costo > 0 else None,
                tiempo_reserva_minima=tiempo_min,
                tiempo_reserva_maxima=tiempo_max,
                estado=estado
            )
            areas.append(area)
        
        self.areas_comunes = AreaComun.objects.bulk_create(areas)
        print(f"✅ {len(self.areas_comunes)} áreas comunes creadas")

    def crear_reglas(self):
        """Crear reglas para las áreas comunes"""
        print("📋 Creando reglas...")
        
        Regla.objects.all().delete()
        
        reglas_data = [
            ('Prohibido fumar', 'No se permite fumar en ninguna área común'),
            ('Horario de uso de piscina', 'La piscina está disponible de 6:00 AM a 10:00 PM'),
            ('Máximo de invitados', 'Máximo 4 invitados por apartamento en áreas comunes'),
            ('Uso de equipos deportivos', 'Los equipos deben devolverse limpios después del uso'),
            ('Reservas cancelación', 'Las cancelaciones deben hacerse con 24 horas de anticipación'),
            ('Menores de edad', 'Los menores deben estar acompañados por un adulto'),
            ('Volumen de música', 'Mantener volumen moderado para no molestar a otros residentes'),
            ('Limpieza después del uso', 'Cada usuario debe limpiar el área después de usarla'),
            ('Prohibido el alcohol', 'No se permite el consumo de alcohol en áreas deportivas'),
            ('Uso de parrillas', 'Las parrillas deben apagarse completamente después del uso'),
        ]
        
        reglas = []
        for nombre, descripcion in reglas_data:
            regla = Regla(nombre=nombre, descripcion=descripcion)
            reglas.append(regla)
        
        reglas = Regla.objects.bulk_create(reglas)
        
        # Asignar reglas a áreas aleatorias
        for regla in reglas:
            areas_asignadas = random.sample(self.areas_comunes, random.randint(1, 5))
            regla.areas.set(areas_asignadas)
        
        print(f"✅ {len(reglas)} reglas creadas")

    def crear_vehiculos(self, cantidad=300):
        """Crear vehículos de residentes"""
        print(f"🚗 Creando {cantidad} vehículos...")
        
        Vehiculo.objects.all().delete()
        
        vehiculos = []
        matriculas_usadas = set()
        
        marcas = ['Toyota', 'Chevrolet', 'Nissan', 'Hyundai', 'Kia', 'Mazda', 'Honda', 'Ford', 'Volkswagen', 'Renault']
        tipos = ['COCHE', 'MOTO', 'BICICLETA', 'OTRO']
        colores = ['Blanco', 'Negro', 'Gris', 'Rojo', 'Azul', 'Plata', 'Verde', 'Amarillo']
        
        for i in range(cantidad):
            # Generar matrícula única
            while True:
                matricula = f"{fake.random_letter().upper()}{fake.random_letter().upper()}{fake.random_letter().upper()}-{fake.random_int(min=100, max=999)}"
                if matricula not in matriculas_usadas:
                    matriculas_usadas.add(matricula)
                    break
            
            tipo = random.choice(tipos)
            marca = random.choice(marcas)
            
            vehiculo = Vehiculo(
                matricula=matricula,
                marca=marca,
                modelo=fake.word().title(),
                color=random.choice(colores),
                tipo=tipo,
                residente=random.choice(self.residentes)
            )
            vehiculos.append(vehiculo)
        
        Vehiculo.objects.bulk_create(vehiculos)
        print(f"✅ {cantidad} vehículos creados")

    def crear_mascotas(self, cantidad=150):
        """Crear mascotas de residentes"""
        print(f"🐕 Creando {cantidad} mascotas...")
        
        Mascota.objects.all().delete()
        
        mascotas = []
        tipos = ['PERRO', 'GATO', 'OTRO']
        nombres_perro = ['Max', 'Luna', 'Buddy', 'Bella', 'Charlie', 'Lucy', 'Rocky', 'Molly', 'Duke', 'Daisy']
        nombres_gato = ['Whiskers', 'Shadow', 'Mittens', 'Tiger', 'Princess', 'Smokey', 'Felix', 'Nala', 'Simba', 'Cleo']
        razas_perro = ['Labrador', 'Golden Retriever', 'Pastor Alemán', 'Bulldog', 'Beagle', 'Poodle', 'Mestizo']
        razas_gato = ['Persa', 'Siamés', 'Maine Coon', 'Británico', 'Mestizo', 'Angora']
        
        for i in range(cantidad):
            tipo = random.choices(tipos, weights=[60, 35, 5])[0]  # Más perros que gatos
            
            if tipo == 'PERRO':
                nombre = random.choice(nombres_perro)
                raza = random.choice(razas_perro)
            elif tipo == 'GATO':
                nombre = random.choice(nombres_gato)
                raza = random.choice(razas_gato)
            else:
                nombre = fake.first_name()
                raza = random.choice(['Loro', 'Hamster', 'Pez', 'Tortuga', 'Conejo'])
            
            mascota = Mascota(
                nombre=nombre,
                tipo=tipo,
                raza=raza,
                residente=random.choice(self.residentes)
            )
            mascotas.append(mascota)
        
        Mascota.objects.bulk_create(mascotas)
        print(f"✅ {cantidad} mascotas creadas")

    def crear_tareas(self, cantidad=200):
        """Crear tareas para el personal"""
        print(f"📝 Creando {cantidad} tareas...")
        
        Tarea.objects.all().delete()
        
        tareas_tipos = {
            'MANTENIMIENTO': [
                'Revisar sistema de aire acondicionado',
                'Reparar iluminación de pasillo',
                'Mantenimiento de ascensores',
                'Revisión de sistema de agua',
                'Pintura de áreas comunes',
                'Reparación de equipos de gimnasio'
            ],
            'LIMPIEZA': [
                'Limpieza profunda de piscina',
                'Mantenimiento de jardines',
                'Limpieza de áreas comunes',
                'Desinfección de ascensores',
                'Limpieza de salón de eventos',
                'Mantenimiento de zona BBQ'
            ],
            'SEGURIDAD': [
                'Revisión de cámaras de seguridad',
                'Control de acceso vehicular',
                'Ronda nocturna de seguridad',
                'Actualización de códigos de acceso',
                'Revisión de sistema de alarmas',
                'Control de visitantes'
            ],
            'ADMINISTRADOR': [
                'Elaborar informe mensual',
                'Reunión con proveedores',
                'Revisión de presupuestos',
                'Atención a quejas de residentes',
                'Coordinación de mantenimiento',
                'Actualización de reglamentos'
            ]
        }
        
        tareas = []
        for i in range(cantidad):
            # Seleccionar personal activo
            personal_activo = [p for p in self.personal if p.activo]
            if not personal_activo:
                break
                
            personal = random.choice(personal_activo)
            puesto = personal.puesto
            
            # Seleccionar tarea según el puesto
            if puesto in tareas_tipos:
                nombre_tarea = random.choice(tareas_tipos[puesto])
            else:
                nombre_tarea = "Tarea administrativa general"
            
            fecha_asignacion = fake.date_between(start_date='-3m', end_date='today')
            fecha_vencimiento = fecha_asignacion + timedelta(days=random.randint(1, 30))
            
            # Estado según la fecha
            if fecha_vencimiento < date.today():
                estado = random.choice(['COMPLETADO', 'COMPLETADO', 'PENDIENTE'])  # Mayoría completadas
            else:
                estado = random.choice(['PENDIENTE', 'PROGRESO'])
            
            tarea = Tarea(
                nombre=nombre_tarea,
                descripcion=fake.text(max_nb_chars=200),
                fecha_asignacion=fecha_asignacion,
                fecha_vencimiento=fecha_vencimiento,
                personal=personal,
                estado=estado
            )
            tareas.append(tarea)
        
        Tarea.objects.bulk_create(tareas)
        print(f"✅ {cantidad} tareas creadas")

    def crear_conceptos_pago(self):
        """Crear conceptos de pago"""
        print("💰 Creando conceptos de pago...")
        
        ConceptoPago.objects.all().delete()
        
        conceptos_data = [
            ('Administración', 120000),
            ('Agua', 45000),
            ('Gas', 35000),
            ('Seguridad', 80000),
            ('Mantenimiento', 60000),
            ('Limpieza', 40000),
            ('Multa por ruido', 150000),
            ('Multa por mascotas', 100000),
            ('Multa por parqueadero', 80000),
            ('Reserva piscina', 25000),
            ('Reserva salón eventos', 150000),
            ('Reserva cancha tenis', 30000),
            ('Servicios adicionales', 25000),
        ]
        
        conceptos = []
        for nombre, monto in conceptos_data:
            concepto = ConceptoPago(
                nombre=nombre,
                monto=Decimal(str(monto))
            )
            conceptos.append(concepto)
        
        self.conceptos_pago = ConceptoPago.objects.bulk_create(conceptos)
        print(f"✅ {len(self.conceptos_pago)} conceptos de pago creados")

    def crear_reservas(self, cantidad=100):
        """Crear reservas de áreas comunes"""
        print(f"📅 Creando {cantidad} reservas...")
        
        Reserva.objects.all().delete()
        
        # Solo áreas que requieren reserva
        areas_reservables = [area for area in self.areas_comunes if area.requiere_reserva]
        
        reservas = []
        for i in range(cantidad):
            area = random.choice(areas_reservables)
            residente = random.choice(self.residentes)
            
            # Fecha de reserva (últimos 6 meses o próximos 3 meses)
            fecha_reserva = fake.date_between(start_date='-6m', end_date='+3m')
            
            # Horarios realistas
            hora_inicio = fake.time_object()
            duracion = random.randint(area.tiempo_reserva_minima or 60, area.tiempo_reserva_maxima or 240)
            hora_fin = (datetime.combine(date.today(), hora_inicio) + timedelta(minutes=duracion)).time()
            
            # Estado según la fecha
            if fecha_reserva < date.today():
                estado = random.choices(
                    ['finalizada', 'cancelada'],
                    weights=[80, 20]
                )[0]
            else:
                estado = random.choices(
                    ['confirmada', 'pendiente', 'cancelada'],
                    weights=[70, 25, 5]
                )[0]
            
            reserva = Reserva(
                residente=residente,
                area=area,
                monto_total=area.costo_reserva or 0,
                descripcion=fake.text(max_nb_chars=150),
                fecha_reserva=fecha_reserva,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                estado=estado
            )
            reservas.append(reserva)
        
        Reserva.objects.bulk_create(reservas)
        print(f"✅ {cantidad} reservas creadas")

    def crear_facturas_y_pagos(self, cantidad=300):
        """Crear facturas y pagos"""
        print(f"🧾 Creando {cantidad} facturas y pagos...")
        
        Factura.objects.all().delete()
        Pago.objects.all().delete()
        
        facturas = []
        pagos = []
        
        for i in range(cantidad):
            residente = random.choice(self.residentes)
            
            # Fecha de factura (últimos 12 meses)
            fecha_emision = fake.date_between(start_date='-12m', end_date='today')
            fecha_limite = fecha_emision + timedelta(days=30)
            
            # Conceptos aleatorios para la factura - calcular monto total
            conceptos_factura = random.sample(self.conceptos_pago, random.randint(3, 6))
            monto_total = sum(concepto.monto for concepto in conceptos_factura)
            
            # Estado según fecha de vencimiento
            if fecha_limite < date.today():
                estado = random.choices(
                    ['pagada', 'vencida', 'cancelada'],
                    weights=[70, 25, 5]
                )[0]
            else:
                estado = random.choices(
                    ['pendiente', 'pagada'],
                    weights=[60, 40]
                )[0]
            
            factura = Factura(
                residente=residente,
                fecha_limite=fecha_limite,
                monto_total=monto_total,
                estado=estado,
                descripcion=f"Factura mensual - {fecha_emision.strftime('%B %Y')}"
            )
            facturas.append(factura)
        
        # Crear facturas primero
        facturas_creadas = Factura.objects.bulk_create(facturas)
        
        # Crear pagos para facturas pagadas
        for factura in facturas_creadas:
            if factura.estado == 'pagada':
                # Fecha de pago realista
                fecha_pago = fake.date_between(
                    start_date=factura.fecha_emision,
                    end_date=min(factura.fecha_limite, date.today())
                )
                
                metodo_pago = random.choice(['efectivo', 'transferencia', 'stripe'])
                
                pago = Pago(
                    factura=factura,
                    residente=factura.residente,
                    monto=factura.monto_total,
                    metodo_pago=metodo_pago,
                    estado='completado',
                    referencia_pago=f"REF-{fake.random_int(min=100000, max=999999)}"
                )
                pagos.append(pago)
        
        Pago.objects.bulk_create(pagos)
        print(f"✅ {len(facturas_creadas)} facturas y {len(pagos)} pagos creados")

    def crear_usuarios_adicionales(self, cantidad=50):
        """Crear usuarios adicionales del sistema"""
        print(f"👤 Creando {cantidad} usuarios adicionales...")
        
        # Obtener roles existentes
        roles = list(Rol.objects.all())
        
        if not roles:
            print("❌ No hay roles disponibles. Ejecutar setup_roles.py primero.")
            return
        
        usuarios = []
        correos_usados = set(Usuario.objects.values_list('correo', flat=True))
        
        for i in range(cantidad):
            # Generar correo único
            while True:
                correo = fake.email()
                if correo not in correos_usados:
                    correos_usados.add(correo)
                    break
            
            # Asignar rol aleatorio
            rol = random.choice(roles)
            
            # Relacionar con residente o personal según el rol
            residente = None
            personal = None
            
            if 'residente' in rol.nombre.lower():
                residente = random.choice(self.residentes)
            elif any(palabra in rol.nombre.lower() for palabra in ['personal', 'seguridad', 'administrador']):
                personal_disponible = [p for p in self.personal if p.activo]
                if personal_disponible:
                    personal = random.choice(personal_disponible)
            
            usuario = Usuario(
                correo=correo,
                nombre=fake.first_name(),
                apellido=fake.last_name(),
                telefono=fake.phone_number()[:15],
                rol=rol,
                residente=residente,
                personal=personal,
                is_active=random.choice([True, True, True, False]),  # 75% activos
                password=make_password('password123')  # Password por defecto
            )
            usuarios.append(usuario)
        
        Usuario.objects.bulk_create(usuarios)
        print(f"✅ {cantidad} usuarios adicionales creados")

    def crear_avisos(self, cantidad=30):
        """Crear avisos del sistema"""
        print(f"📢 Creando {cantidad} avisos...")
        
        Aviso.objects.all().delete()
        
        asuntos_avisos = [
            'Mantenimiento de ascensores programado',
            'Corte de agua temporal',
            'Mantenimiento de piscina',
            'Revisión de sistemas eléctricos',
            'Corte de energía imprevisto',
            'Problema en sistema de agua',
            'Nuevas normas de convivencia',
            'Horarios de áreas comunes actualizados',
            'Asamblea general de propietarios',
            'Reunión del consejo de administración',
            'Celebración día del niño',
            'Torneo de tenis comunitario',
            'Jornada de vacunación mascotas',
            'Actualización de códigos de acceso',
            'Mantenimiento de jardines',
            'Fumigación preventiva',
            'Limpieza de tanques de agua'
        ]
        
        avisos = []
        for i in range(cantidad):
            asunto = random.choice(asuntos_avisos)
            
            fecha_push = fake.date_between(start_date='-2m', end_date='+1m')
            hora_push = fake.time_object()
            
            urgente = random.choice([True, False, False, False])  # 25% urgentes
            
            # Estado según la fecha
            if fecha_push <= date.today():
                estado = random.choices(
                    ['ENVIADO', 'FALLIDO'],
                    weights=[90, 10]
                )[0]
            else:
                estado = 'PENDIENTE'
            
            aviso = Aviso(
                asunto=asunto,
                mensaje=fake.text(max_nb_chars=300),
                fecha_push=fecha_push,
                hora_push=hora_push,
                urgente=urgente,
                estado=estado
            )
            avisos.append(aviso)
        
        Aviso.objects.bulk_create(avisos)
        print(f"✅ {cantidad} avisos creados")

    def generar_reporte_final(self):
        """Generar reporte final de datos creados"""
        print("\n" + "="*60)
        print("📊 REPORTE FINAL DE DATOS GENERADOS")
        print("="*60)
        
        stats = {
            'Residencias': Residencia.objects.count(),
            'Residentes': Residente.objects.count(),
            'Personal': Personal.objects.count(),
            'Usuarios': Usuario.objects.count(),
            'Áreas Comunes': AreaComun.objects.count(),
            'Reglas': Regla.objects.count(),
            'Vehículos': Vehiculo.objects.count(),
            'Mascotas': Mascota.objects.count(),
            'Tareas': Tarea.objects.count(),
            'Conceptos de Pago': ConceptoPago.objects.count(),
            'Reservas': Reserva.objects.count(),
            'Facturas': Factura.objects.count(),
            'Pagos': Pago.objects.count(),
            'Avisos': Aviso.objects.count(),
        }
        
        total_registros = sum(stats.values())
        
        for modelo, cantidad in stats.items():
            print(f"  📋 {modelo:<20}: {cantidad:>6} registros")
        
        print("-" * 60)
        print(f"  🎯 TOTAL REGISTROS     : {total_registros:>6} registros")
        print(f"  ✅ OBJETIVO CUMPLIDO   : {'SÍ' if total_registros >= 1000 else 'NO'}")
        print("="*60)
        
        return total_registros

    def ejecutar_generacion_completa(self):
        """Ejecutar la generación completa de datos"""
        try:
            print("🚀 Iniciando generación masiva de datos...")
            print("⚠️  ADVERTENCIA: Este proceso eliminará todos los datos existentes")
            
            # Generar datos en orden correcto por dependencias
            self.crear_residencias(150)          # 150 registros
            self.crear_residentes(400)           # 400 registros  
            self.crear_personal(25)              # 25 registros
            self.crear_areas_comunes()           # ~18 registros
            self.crear_reglas()                  # ~10 registros
            self.crear_vehiculos(300)            # 300 registros
            self.crear_mascotas(150)             # 150 registros
            self.crear_tareas(200)               # 200 registros
            self.crear_conceptos_pago()          # ~13 registros
            self.crear_reservas(100)             # 100 registros
            self.crear_facturas_y_pagos(300)     # 300 facturas + ~210 pagos
            self.crear_usuarios_adicionales(50)  # 50 registros
            self.crear_avisos(30)                # 30 registros
            
            total = self.generar_reporte_final()
            
            print(f"\n🎉 ¡GENERACIÓN COMPLETADA EXITOSAMENTE!")
            print(f"✅ Se generaron {total} registros en total")
            print("💾 La base de datos está lista para usar")
            
        except Exception as e:
            print(f"❌ Error durante la generación: {str(e)}")
            import traceback
            traceback.print_exc()

def main():
    """Función principal"""
    generator = CondominiumDataGenerator()
    generator.ejecutar_generacion_completa()

if __name__ == "__main__":
    main()
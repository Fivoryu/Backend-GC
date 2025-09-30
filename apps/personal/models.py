from django.db import models


class Personal(models.Model):
    PUESTO_CHOICES = (
        ('ADMINISTRADOR', 'Administrador'),
        ('SUPERVISOR', 'Supervisor'),
        ('MANTENIMIENTO', 'Mantenimiento'),
        ('SEGURIDAD', 'Seguridad'),
        ('LIMPIEZA', 'Limpieza'),
        ('OTRO', 'Otro'),
    )
        
        
    nombre = models.CharField(max_length=80)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=30, unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(max_length=150, blank=True)
    direccion = models.CharField(max_length=150, blank=True)
    fecha_contratacion = models.DateField(null=True, blank=True)
    puesto = models.CharField(max_length=100, blank=True)
    activo = models.BooleanField(default=True)
    fecha_salida = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Personal'
        verbose_name_plural = 'Personal'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Tarea(models.Model):
    ESTADO_CHOICES = (
        ('PENDIENTE', 'Pendiente'),
        ('PROGRESO', 'En Progreso'),
        ('COMPLETADO', 'Completado'),
    )
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    fecha_asignacion = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    personal = models.ForeignKey(Personal, related_name='tareas', on_delete=models.CASCADE)
    estado = models.CharField(max_length=12, choices=ESTADO_CHOICES, default='PENDIENTE')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'

    def __str__(self):
        return self.nombre

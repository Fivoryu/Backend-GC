from django.db import models
from django.utils import timezone

class AreaComun(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('mantenimiento', 'En Mantenimiento'),
        ('cerrado', 'Cerrado'),
    ]
    
    nombre = models.CharField(max_length=120, unique=True)
    descripcion = models.TextField(blank=True)
    requiere_reserva = models.BooleanField(default=False)
    capacidad_maxima = models.PositiveIntegerField(null=True, blank=True)
    costo_reserva = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    tiempo_reserva_minima = models.PositiveIntegerField(null=True, blank=True, help_text="En minutos")
    tiempo_reserva_maxima = models.PositiveIntegerField(null=True, blank=True, help_text="En minutos")
    estado = models.CharField(max_length=50, default='disponible', choices=ESTADO_CHOICES)
    
    # Campos de auditoría
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Área Común'
        verbose_name_plural = 'Áreas Comunes'

    def __str__(self):
        return self.nombre

class Regla(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    areas = models.ManyToManyField(AreaComun, related_name='reglas', blank=True)
    
    # Campos de auditoría
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Regla'
        verbose_name_plural = 'Reglas'

    def __str__(self):
        return self.nombre

class Horario(models.Model):  
    DIAS_CHOICES = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ]
    
    area = models.ForeignKey(AreaComun, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.CharField(max_length=20, choices=DIAS_CHOICES)
    hora_apertura = models.TimeField()
    hora_cierre = models.TimeField()
    
    # Campos de auditoría
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['dia_semana', 'hora_apertura']
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
        unique_together = ['area', 'dia_semana'] 

    def __str__(self):
        return f"{self.area.nombre} - {self.dia_semana}: {self.hora_apertura} - {self.hora_cierre}"

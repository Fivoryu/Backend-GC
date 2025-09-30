from django.db import models


class Residencia(models.Model):
    TIPO_CHOICES = (
        ("APARTAMENTO", "Apartamento"),
        ("CASA", "Casa"),
    )

    numero = models.IntegerField(null=False, primary_key=True, unique=True
    )
    direccion = models.CharField(max_length=200)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    num_habitaciones = models.IntegerField(default=1)
    num_residentes = models.IntegerField(default=0)

    class Meta:
        ordering = ["numero"]

    def __str__(self):
        return str(self.numero)


class Residente(models.Model):
    SEXO_CHOICES = (("M", "Masculino"), ("F", "Femenino"))
    TIPO_CHOICES = (
        ("PROPIETARIO", "Propietario"),
        ("INQUILINO", "Inquilino"),
        ("FAMILIAR_PROPIETARIO", "Familiar Propietario"),
        ("FAMILIAR_INQUILINO", "Familiar Inquilino"),
        ("OTRO", "Otro"),
    )

    nombre = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(max_length=150, blank=True)
    dni = models.CharField(max_length=30, unique=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    tipo = models.CharField(max_length=25, choices=TIPO_CHOICES)
    residencia = models.ForeignKey(
        Residencia, related_name="residentes", on_delete=models.CASCADE,null=True
    )
    foto_perfil = models.URLField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"

class Vehiculo(models.Model):
    TIPO_CHOICES = (
        ("COCHE", "Coche"),
        ("MOTO", "Moto"),
        ("BICICLETA", "Bicicleta"),
        ("OTRO", "Otro"),
    )

    marca = models.CharField(max_length=50,)
    modelo = models.CharField(max_length=50, blank=True)
    matricula = models.CharField(max_length=20, unique=True, blank=True )
    color = models.CharField(max_length=30, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    residente = models.ForeignKey(
        Residente, related_name="vehiculos", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.matricula}"

class Mascota(models.Model):
    TIPO_CHOICES = (
        ("PERRO", "Perro"),
        ("GATO", "Gato"),
        ("OTRO", "Otro"),
    )

    nombre = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    raza = models.CharField(max_length=50, blank=True)
    residente = models.ForeignKey(
        Residente, related_name="mascotas", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.nombre} - {self.tipo}"

class Visitante(models.Model):
    nombre = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=100)
    dni = models.CharField(max_length=30, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    residente = models.ForeignKey(
        Residente, related_name="visitantes", on_delete=models.CASCADE
    )
    foto_referencial = models.URLField(null=True, blank=True)
    fecha_visita = models.DateTimeField(auto_now_add=True)
    hora_entrada = models.DateTimeField(null=True, blank=True)
    hora_salida = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"
    
    
        
from django.db import models
from apps.residentes.models import Residente
from apps.areas.models import AreaComun


class Reserva(models.Model):
    ESTADO_CHOICE = [
        ("pendiente", "Pendiente"),
        ("confirmada", "Confirmada"),
        ("cancelada", "Cancelada"),
        ("finalizada", "Finalizada"),
    ]

    residente = models.ForeignKey(Residente, on_delete=models.CASCADE)
    area = models.ForeignKey(AreaComun, on_delete=models.CASCADE)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descripcion = models.TextField(max_length=200, blank=True)
    fecha_reserva = models.DateField(blank=True, null=True)
    hora_inicio = models.TimeField(blank=True, null=True)
    hora_fin = models.TimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICE, default="pendiente")

    class Meta:
        ordering = ["id"]
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"

    def __str__(self):
        return f"Reserva de {self.residente} en {self.area} el {self.fecha_reserva}"


class ConceptoPago(models.Model):
    nombre = models.CharField(max_length=50)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["id"]
        verbose_name = "Concepto de Pago"
        verbose_name_plural = "Conceptos de Pago"

    def __str__(self):
        return self.nombre


class Factura(models.Model):
    FACTURA_ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("pagada", "Pagada"),
        ("vencida", "Vencida"),
        ("cancelada", "Cancelada"),
    ]
    
    residente = models.ForeignKey(Residente, on_delete=models.CASCADE)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    estado = models.CharField(
        max_length=20, choices=FACTURA_ESTADO_CHOICES, default="pendiente"
    )
    fecha_limite = models.DateField(null=True, blank=True)
    fecha_emision = models.DateField(auto_now_add=True)
    descripcion = models.TextField(max_length=200, blank=True)


    class Meta:
        ordering = ["id"]
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"

    def __str__(self):
        return f"Factura {self.id} para {self.residente}"


class DetalleFactura(models.Model):
    factura = models.ForeignKey(
        Factura, on_delete=models.CASCADE, related_name="detalles"
    )
    concepto = models.ForeignKey(ConceptoPago, on_delete=models.CASCADE)
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="detalles_factura",
    )
    monto = models.DecimalField(
        max_digits=10, decimal_places=2, default=0  
    )

    def __str__(self):
        return f"Detalle de {self.concepto.nombre} para Factura {self.factura.id}"


class Pago(models.Model):
    ESTADOS_PAGO = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('cancelado', 'Cancelado'),
        ('reembolsado', 'Reembolsado'),
    ]
    
    METODOS_PAGO = [
        ('stripe', 'Stripe'),
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
    ]
    
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='pagos')
    residente = models.ForeignKey(Residente, on_delete=models.CASCADE, default=1)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='stripe')
    estado = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='pendiente')
    
    # Campos específicos de Stripe
    stripe_payment_intent_id = models.CharField(max_length=200, null=True, blank=True)
    stripe_client_secret = models.CharField(max_length=300, null=True, blank=True)
    
    # Timestamps y datos adicionales
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    referencia_pago = models.CharField(max_length=100, null=True, blank=True)
    notas = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
    
    def __str__(self):
        return f'Pago #{self.id} - Factura #{self.factura.id} - Bs{self.monto}'

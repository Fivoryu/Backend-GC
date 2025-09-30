from rest_framework import serializers
from .models import Reserva, Factura, DetalleFactura, ConceptoPago, Pago
from apps.areas.models import AreaComun
from apps.residentes.models import Residente

class AreaComunMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaComun
        fields = ['id', 'nombre']

class ResidenteMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Residente
        fields = ['id', 'nombre']

class ReservaSerializer(serializers.ModelSerializer):
    area = AreaComunMiniSerializer(read_only=True)
    area_id = serializers.PrimaryKeyRelatedField(
        queryset=AreaComun.objects.all(), source='area', write_only=True
    )
    residente = ResidenteMiniSerializer(read_only=True)
    residente_id = serializers.PrimaryKeyRelatedField(
        queryset=Residente.objects.all(), source='residente', write_only=True
    )

    class Meta:
        model = Reserva
        fields = '__all__'

class ConceptoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptoPago
        fields = '__all__'

class FacturaSerializer(serializers.ModelSerializer):
    residente_id = serializers.PrimaryKeyRelatedField(
        queryset=Residente.objects.all(), source='residente', write_only=True
    )
    residente = ResidenteMiniSerializer(read_only=True)

    class Meta:
        model = Factura
        fields = ['id', 'residente', 'residente_id', 'monto_total', 'estado', 'fecha_limite', 'fecha_emision', 'descripcion']
        read_only_fields = ['fecha_emision']

    def create(self, validated_data):
        if 'monto_total' not in validated_data:
            validated_data['monto_total'] = 0
        return super().create(validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Recalcula el monto_total basado en los detalles actuales
        total = sum(d.monto for d in instance.detalles.all())
        instance.monto_total = total
        
        instance.save()
        return instance

class DetalleFacturaSerializer(serializers.ModelSerializer):
    concepto_nombre = serializers.CharField(source='concepto.nombre', read_only=True)

    class Meta:
        model = DetalleFactura
        fields = ['id', 'factura', 'concepto', 'monto', 'reserva', 'concepto_nombre']

    def create(self, validated_data):
        concepto = validated_data['concepto']
        detalle = DetalleFactura.objects.create(
            factura=validated_data['factura'],
            concepto=concepto,
            monto=concepto.monto,
            reserva=validated_data.get('reserva')
        )
        self.actualizar_monto_factura(detalle.factura)
        return detalle

    def actualizar_monto_factura(self, factura):
        total = sum(d.monto for d in factura.detalles.all())
        factura.monto_total = total
        factura.save()

class PagoSerializer(serializers.ModelSerializer):
    residente_nombre = serializers.CharField(source='residente.nombre', read_only=True)
    factura_numero = serializers.IntegerField(source='factura.id', read_only=True)
    
    class Meta:
        model = Pago
        fields = [
            'id', 'factura', 'residente', 'monto', 'metodo_pago', 'estado',
            'stripe_payment_intent_id', 'stripe_client_secret',
            'fecha_creacion', 'fecha_actualizacion', 'referencia_pago', 'notas',
            'residente_nombre', 'factura_numero'
        ]
        read_only_fields = ['stripe_payment_intent_id', 'stripe_client_secret']

class PagoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ['factura', 'residente', 'monto', 'metodo_pago']
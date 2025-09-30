from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action  # ✅ Asegúrate de importar esto
from .models import Reserva, ConceptoPago, Factura, DetalleFactura, Pago
from .serializers import (
    ReservaSerializer, ConceptoPagoSerializer, FacturaSerializer,
    DetalleFacturaSerializer, PagoSerializer, PagoCreateSerializer
)
import stripe
from django.conf import settings

# Configurar Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all().order_by('id')
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]

class ConceptoPagoViewSet(viewsets.ModelViewSet):
    queryset = ConceptoPago.objects.all().order_by('id')
    serializer_class = ConceptoPagoSerializer
    permission_classes = [IsAuthenticated]

class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all().order_by('id')
    serializer_class = FacturaSerializer
    permission_classes = [IsAuthenticated]

class DetalleFacturaViewSet(viewsets.ModelViewSet):
    serializer_class = DetalleFacturaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = DetalleFactura.objects.all().order_by('id')
        factura_id = self.request.query_params.get('factura')
        if factura_id:
            queryset = queryset.filter(factura_id=factura_id)
        return queryset

    def destroy(self, request, *args, **kwargs):
        detalle = self.get_object()
        factura = detalle.factura
        response = super().destroy(request, *args, **kwargs)
        # Actualiza el monto_total de la factura después de eliminar el detalle
        total = sum(d.monto for d in factura.detalles.all())
        factura.monto_total = total
        factura.save()
        return response

class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PagoCreateSerializer
        return PagoSerializer
    
    def perform_create(self, serializer):
        serializer.save(residente=self.request.user.residente)

    @action(detail=False, methods=['post'])  # ✅ Verifica que tenga este decorador
    def crear_payment_intent(self, request):
        """Crear un PaymentIntent de Stripe"""
        try:
            factura_id = request.data.get('factura_id')
            if not factura_id:
                return Response(
                    {'error': 'factura_id es requerido'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar que la factura existe y pertenece al usuario
            try:
                factura = Factura.objects.get(id=factura_id, residente=request.user.residente)
            except Factura.DoesNotExist:
                return Response(
                    {'error': 'Factura no encontrada'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar que la factura no esté ya pagada
            if factura.estado == 'pagada':
                return Response(
                    {'error': 'La factura ya está pagada'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Convertir monto a centavos (Stripe usa centavos)
            monto_centavos = int(float(factura.monto_total) * 100)
            
            # Crear PaymentIntent en Stripe
            intent = stripe.PaymentIntent.create(
                amount=monto_centavos,
                currency='usd',  # o 'bob' si soporta bolivianos
                metadata={
                    'factura_id': factura.id,
                    'residente_id': request.user.residente.id,
                    'descripcion': factura.descripcion or f'Pago factura #{factura.id}'
                }
            )
            
            # Crear registro de pago en la BD
            pago = Pago.objects.create(
                factura=factura,
                residente=request.user.residente,
                monto=factura.monto_total,
                metodo_pago='stripe',
                estado='pendiente',
                stripe_payment_intent_id=intent.id,
                stripe_client_secret=intent.client_secret
            )
            
            return Response({
                'payment_intent_id': intent.id,
                'client_secret': intent.client_secret,
                'pago_id': pago.id,
                'monto': float(factura.monto_total),
                'factura_id': factura.id
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])  # ✅ Verifica que tenga este decorador
    def confirmar_pago(self, request):
        """Confirmar el pago desde el backend (sin Stripe)"""
        try:
            factura_id = request.data.get('factura_id')
            if not factura_id:
                return Response(
                    {'error': 'factura_id es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Buscar la factura y el pago pendiente
            try:
                factura = Factura.objects.get(id=factura_id, residente=request.user.residente)
            except Factura.DoesNotExist:
                return Response(
                    {'error': 'Factura no encontrada'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Buscar el último pago pendiente o crear uno nuevo
            pago = Pago.objects.filter(
                factura=factura,
                residente=request.user.residente
            ).order_by('-id').first()

            if pago:
                pago.estado = 'completado'
                pago.metodo_pago = 'efectivo'
                pago.save()
            else:
                pago = Pago.objects.create(
                    factura=factura,
                    residente=request.user.residente,
                    monto=factura.monto_total,
                    metodo_pago='efectivo',
                    estado='completado'
                )

            factura.estado = 'pagada'
            factura.save()

            return Response({
                'message': 'Pago confirmado exitosamente',
                'pago_id': pago.id,
                'factura_id': factura.id,
                'estado': 'pagada'
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

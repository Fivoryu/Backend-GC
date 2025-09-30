from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReservaViewSet, ConceptoPagoViewSet, FacturaViewSet,
    DetalleFacturaViewSet, PagoViewSet
)

router = DefaultRouter()
router.register('reservas', ReservaViewSet, basename='reservas') 
router.register('conceptos-pago', ConceptoPagoViewSet, basename='conceptos-pago')
router.register('facturas', FacturaViewSet, basename='facturas')
router.register('detalles-factura', DetalleFacturaViewSet, basename='detalles-factura')
router.register(r'pagos', PagoViewSet, basename='pagos') 

urlpatterns = [
    path('', include(router.urls)),
]
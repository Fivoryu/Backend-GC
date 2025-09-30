from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('residentes', ResidenteViewSet, basename='residentes')
router.register('residencias', ResidenciaViewSet, basename='residencias')
router.register('vehiculos', VehiculoViewSet, basename='vehiculos')
router.register('mascotas', MascotaViewSet, basename='mascotas')
router.register('visitantes', VisitanteViewSet, basename='visitantes')
urlpatterns = [
    path('', include(router.urls)),
]
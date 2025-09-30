from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AreaComunViewSet, ReglaViewSet, HorarioViewSet

router = DefaultRouter()
router.register('areas-comunes', AreaComunViewSet, basename='areas-comunes')
router.register('reglas', ReglaViewSet, basename='reglas')
router.register('horarios', HorarioViewSet, basename='horarios')

urlpatterns = [
    path('', include(router.urls)),
]
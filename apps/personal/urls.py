from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PersonalViewSet, TareaViewSet

router = DefaultRouter()
router.register('personal', PersonalViewSet, basename='personal')
router.register('tareas', TareaViewSet, basename='tareas')

urlpatterns = [
    path('', include(router.urls)),
]
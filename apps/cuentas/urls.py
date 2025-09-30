from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register('roles', RolViewSet, basename='roles')
router.register('usuarios', UsuarioViewSet, basename='usuarios')
router.register('bitacora', BitacoraViewSet, basename='bitacora')
router.register('avisos', AvisoViewSet, basename='avisos')

urlpatterns = [
    path('cuenta/token/', LoginJWTView.as_view(), name='token_obtain_pair'),
    path('cuenta/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('cuenta/logout/', LogoutJWTView.as_view(), name='logout'),
    path('cuenta/perfil/', PerfilView.as_view(), name='perfil'),
    path('cuenta/registro/', RegistroView.as_view(), name='registro'),
    path('cuenta/solicitar-recuperacion/', SolicitarRecuperacionView.as_view(), name='solicitar_recuperacion'),
    path('cuenta/confirmar-recuperacion/', ConfirmarRecuperacionView.as_view(), name='confirmar_recuperacion'),
    path('cuenta/', include(router.urls)),
]

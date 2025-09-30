from django.urls import path
from .views import ReconocimientoFacialView, LogReconocimientoListView, ReconocimientoPlacaView, LogReconocimientoPlacaListView

urlpatterns = [
    path('vision/reconocer/', ReconocimientoFacialView.as_view(), name='reconocer-facial'),
    path('vision/logs/', LogReconocimientoListView.as_view(), name='logs-reconocimiento'),
    path('vision/reconocer-placa/', ReconocimientoPlacaView.as_view(), name='reconocer-placa'),
    path('vision/logs-placa/', LogReconocimientoPlacaListView.as_view(), name='logs-reconocimiento-placa'),
]
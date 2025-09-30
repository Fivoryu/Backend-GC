from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Residente
from .serializers import *

class ResidenteViewSet(viewsets.ModelViewSet):
    queryset = Residente.objects.all().order_by('id')
    serializer_class = ResidenteSerializer
    permission_classes = [IsAuthenticated]

class ResidenciaViewSet(viewsets.ModelViewSet):
    queryset = Residencia.objects.all().order_by('numero')
    serializer_class = ResidenciaSerializer
    permission_classes = [IsAuthenticated]


class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all().order_by('id')
    serializer_class = VehiculoSerializer
    permission_classes = [IsAuthenticated]

class MascotaViewSet(viewsets.ModelViewSet):
    queryset = Mascota.objects.select_related('residente').all().order_by('id')
    serializer_class = MascotaSerializer
    permission_classes = [IsAuthenticated]

class VisitanteViewSet(viewsets.ModelViewSet):
    queryset = Visitante.objects.all().order_by('id')
    serializer_class = VisitanteSerializer
    permission_classes = [IsAuthenticated]
    

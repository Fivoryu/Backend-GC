from django.shortcuts import render
from django.db import IntegrityError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AreaComun, Regla, Horario
from .serializers import (
    AreaComunSerializer, 
    ReglaSerializer, 
    HorarioSerializer,
    HorarioCreateSerializer
)

class AreaComunViewSet(viewsets.ModelViewSet):
    queryset = AreaComun.objects.all().order_by('id')
    serializer_class = AreaComunSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='asignar-reglas')
    def asignar_reglas(self, request, pk=None):
        area = self.get_object()
        reglas_ids = request.data.get('reglas', [])
        if not isinstance(reglas_ids, list):
            return Response({'detail': 'Formato inválido. Debe ser lista.'},
                            status=status.HTTP_400_BAD_REQUEST)
        reglas = Regla.objects.filter(id__in=reglas_ids)
        area.reglas.set(reglas)
        area.save()
        return Response({'detail': 'Reglas asignadas', 'reglas': [r.id for r in reglas]})

    @action(detail=True, methods=['get'], url_path='horarios')
    def obtener_horarios(self, request, pk=None):
        area = self.get_object()
        horarios = area.horarios.filter(activo=True)
        serializer = HorarioSerializer(horarios, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='crear-horario')
    def crear_horario(self, request, pk=None):
        area = self.get_object()
        data = request.data.copy()
        data['area'] = area.id
        serializer = HorarioCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReglaViewSet(viewsets.ModelViewSet):
    queryset = Regla.objects.all().order_by('id')
    serializer_class = ReglaSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='activas')
    def activas(self, request):
        reglas = Regla.objects.filter(activo=True)
        serializer = self.get_serializer(reglas, many=True)
        return Response(serializer.data)

class HorarioViewSet(viewsets.ModelViewSet):
    queryset = Horario.objects.select_related('area').all().order_by('area','id')
    serializer_class = HorarioSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create','update','partial_update']:
            return HorarioCreateSerializer
        return HorarioSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request,*args,**kwargs)
        except IntegrityError:
            return Response(
                {"detail":"Ya existe un horario para ese día en esa área."},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request,*args,**kwargs)
        except IntegrityError:
            return Response(
                {"detail":"Conflicto de día/área existente."},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='por-area/(?P<area_id>[^/.]+)')
    def por_area(self, request, area_id=None):
        horarios = Horario.objects.filter(area_id=area_id, activo=True)
        serializer = self.get_serializer(horarios, many=True)
        return Response(serializer.data)

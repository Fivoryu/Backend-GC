from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Personal, Tarea
from .serializers import PersonalSerializer, TareaSerializer

class PersonalViewSet(viewsets.ModelViewSet):
    queryset = Personal.objects.all().order_by('id')
    serializer_class = PersonalSerializer
    permission_classes = [IsAuthenticated]

class TareaViewSet(viewsets.ModelViewSet):
    queryset = Tarea.objects.select_related('personal').all().order_by('id')
    serializer_class = TareaSerializer
    permission_classes = [IsAuthenticated]

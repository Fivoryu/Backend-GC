from rest_framework import serializers
from .models import Personal, Tarea

class PersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personal
        fields = [
            'id','nombre','apellido','dni','fecha_nacimiento','telefono','correo',
            'direccion','fecha_contratacion','puesto','activo','fecha_salida',
            'fecha_creacion','actualizado'
        ]

class TareaSerializer(serializers.ModelSerializer):
    personal_id = serializers.PrimaryKeyRelatedField(
        source='personal', queryset=Personal.objects.all()
    )
    personal_nombre = serializers.CharField(source='personal.nombre', read_only=True)
    personal_apellido = serializers.CharField(source='personal.apellido', read_only=True)

    class Meta:
        model = Tarea
        fields = [
            'id','nombre','descripcion','fecha_asignacion','fecha_vencimiento',
            'estado','personal_id','personal_nombre','personal_apellido',
            'creado','actualizado'
        ]
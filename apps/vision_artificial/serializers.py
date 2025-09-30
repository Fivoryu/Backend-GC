from rest_framework import serializers
from .models import logReconocimiento, logReconocimientoPlaca

class LogReconocimientoSerializer(serializers.ModelSerializer):
    nombre_residente = serializers.SerializerMethodField()
    apellido_residente = serializers.SerializerMethodField()
    foto_residente = serializers.SerializerMethodField()

    def get_nombre_residente(self, obj):
        try:
            if obj.residente:
                return obj.residente.nombre or ""
            return ""
        except:
            return ""

    def get_apellido_residente(self, obj):
        try:
            if obj.residente:
                return obj.residente.apellidos or ""
            return ""
        except:
            return ""

    def get_foto_residente(self, obj):
        try:
            if obj.residente and hasattr(obj.residente, 'foto_perfil'):
                return obj.residente.foto_perfil or ""
            return ""
        except:
            return ""

    class Meta:
        model = logReconocimiento
        fields = [
            'id',
            'residente',
            'fecha_hora',
            'foto_ruta',
            'descripcion',
            'coincidencia',
            'nombre_residente',
            'apellido_residente',
            'foto_residente',
        ]

class LogReconocimientoPlacaSerializer(serializers.ModelSerializer):
    nombre_propietario = serializers.SerializerMethodField()
    apellido_propietario = serializers.SerializerMethodField()
    marca_vehiculo = serializers.SerializerMethodField()
    modelo_vehiculo = serializers.SerializerMethodField()
    matricula_vehiculo = serializers.SerializerMethodField()

    def get_nombre_propietario(self, obj):
        try:
            if obj.vehiculo and obj.vehiculo.residente:
                return obj.vehiculo.residente.nombre or ""
            return ""
        except:
            return ""

    def get_apellido_propietario(self, obj):
        try:
            if obj.vehiculo and obj.vehiculo.residente:
                return obj.vehiculo.residente.apellidos or ""
            return ""
        except:
            return ""

    def get_marca_vehiculo(self, obj):
        try:
            if obj.vehiculo:
                return obj.vehiculo.marca or ""
            return ""
        except:
            return ""

    def get_modelo_vehiculo(self, obj):
        try:
            if obj.vehiculo:
                return obj.vehiculo.modelo or ""
            return ""
        except:
            return ""

    def get_matricula_vehiculo(self, obj):
        try:
            if obj.vehiculo:
                return obj.vehiculo.matricula or ""
            return ""
        except:
            return ""

    class Meta:
        model = logReconocimientoPlaca
        fields = [
            'id',
            'vehiculo',
            'fecha_hora',
            'foto_ruta',
            'placa_detectada',
            'descripcion',
            'confianza',
            'nombre_propietario',
            'apellido_propietario',
            'marca_vehiculo',
            'modelo_vehiculo',
            'matricula_vehiculo',
        ]


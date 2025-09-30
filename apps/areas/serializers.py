from rest_framework import serializers
from .models import AreaComun, Regla, Horario


class HorarioSerializer(serializers.ModelSerializer):
    area_nombre = serializers.CharField(source="area.nombre", read_only=True)

    class Meta:
        model = Horario
        fields = [
            "id",
            "area",
            "area_nombre",
            "dia_semana",
            "hora_apertura",
            "hora_cierre",
            "activo",
            "creado",
            "actualizado",
        ]


class HorarioCreateSerializer(serializers.ModelSerializer):
    area_nombre = serializers.CharField(source="area.nombre", read_only=True)

    class Meta:
        model = Horario
        fields = [
            "id",
            "area",
            "dia_semana",
            "hora_apertura",
            "hora_cierre",
            "activo",
            "area_nombre",
        ]

    def validate(self, attrs):
        area = attrs.get("area")
        dia = attrs.get("dia_semana")
        instance = getattr(self, "instance", None)
        qs = Horario.objects.filter(area=area, dia_semana=dia)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {"dia_semana": "Ya existe un horario para este día en esta área."}
            )
        if attrs["hora_apertura"] >= attrs["hora_cierre"]:
            raise serializers.ValidationError(
                {"hora_cierre": "La hora de cierre debe ser mayor que la de apertura."}
            )
        return attrs


class ReglaSerializer(serializers.ModelSerializer):
    areas_ids = serializers.PrimaryKeyRelatedField(
        many=True, source="areas", queryset=AreaComun.objects.all(), required=False
    )

    class Meta:
        model = Regla
        fields = [
            "id",
            "nombre",
            "descripcion",
            "areas_ids",
            "activo",
            "creado",
            "actualizado",
        ]


class AreaComunSerializer(serializers.ModelSerializer):
    reglas_ids = serializers.PrimaryKeyRelatedField(
        many=True, source="reglas", queryset=Regla.objects.all(), required=False
    )
    reglas = ReglaSerializer(many=True, read_only=True)
    horarios = HorarioSerializer(many=True, read_only=True)

    class Meta:
        model = AreaComun
        fields = [
            "id",
            "nombre",
            "descripcion",
            "requiere_reserva",
            "capacidad_maxima",
            "costo_reserva",
            "tiempo_reserva_minima",
            "tiempo_reserva_maxima",
            "estado",
            "reglas_ids",
            "reglas",
            "horarios",
            "activo",
            "creado",
            "actualizado",
        ]

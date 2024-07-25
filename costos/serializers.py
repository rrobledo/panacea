from .models import Insumos, Productos, Costos, Programacion
from rest_framework import serializers
from django.urls import reverse


# Serializers define the API representation.
class InsumosSerializer(serializers.HyperlinkedModelSerializer):
    absolute_url = serializers.SerializerMethodField()

    def get_absolute_url(self, obj):
        request = self.context.get('request')
        base_url = f"{request.scheme}://{request.get_host()}"
        absolute_url = reverse('insumos-detail', args=[str(obj.id)])
        return f"{base_url}{absolute_url}"

    class Meta:
        model = Insumos
        fields = ["absolute_url", "id", "nombre", "unidad_medida", "cantidad", "precio"]


class ProductosSerializer(serializers.HyperlinkedModelSerializer):
    absolute_url = serializers.SerializerMethodField()

    def get_absolute_url(self, obj):
        request = self.context.get('request')
        base_url = f"{request.scheme}://{request.get_host()}"
        absolute_url = reverse('productos-detail', args=[str(obj.id)])
        return f"{base_url}{absolute_url}"

    class Meta:
        model = Productos
        fields = ["absolute_url", 'id', 'codigo', 'nombre', "ref_id", "utilidad", "precio_actual", "unidad_medida", "lote_produccion", "tiempo_produccion"]


class CostosSerializer(serializers.HyperlinkedModelSerializer):
    insumo_nombre = serializers.CharField(source='insumo.nombre', required=False, read_only=True)
    insumo_unidad_medida = serializers.CharField(source='insumo.unidad_medida', required=False, read_only=True)

    class Meta:
        model = Costos
        fields = ["id", "producto", "insumo", 'insumo_nombre', "insumo_unidad_medida", "cantidad"]


class ProgramacionSerializer(serializers.HyperlinkedModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', required=False, read_only=True)

    class Meta:
        model = Programacion
        fields = ["id", "producto", "producto_nombre", "responsable", "s01_lunes_plan", "s01_lunes_real", "s01_martes_plan", "s01_martes_real", "s01_miercoles_plan", "s01_miercoles_real", "s01_jueves_plan", "s01_jueves_real", "s01_viernes_plan", "s01_viernes_real", "s01_sabado_plan", "s01_sabado_real", "s02_lunes_plan", "s02_lunes_real", "s02_martes_plan", "s02_martes_real", "s02_miercoles_plan", "s02_miercoles_real", "s02_jueves_plan", "s02_jueves_real", "s02_viernes_plan", "s02_viernes_real", "s02_sabado_plan", "s02_sabado_real", "s03_lunes_plan", "s03_lunes_real", "s03_martes_plan", "s03_martes_real", "s03_miercoles_plan", "s03_miercoles_real", "s03_jueves_plan", "s03_jueves_real", "s03_viernes_plan", "s03_viernes_real", "s03_sabado_plan", "s03_sabado_real", "s04_lunes_plan", "s04_lunes_real", "s04_martes_plan", "s04_martes_real", "s04_miercoles_plan", "s04_miercoles_real", "s04_jueves_plan", "s04_jueves_real", "s04_viernes_plan", "s04_viernes_real", "s04_sabado_plan", "s04_sabado_real"]


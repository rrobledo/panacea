from .models import Insumos, Productos, Costos
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


from .models import Supplies, Products, Costs, CostsDetails, Compras
from rest_framework import serializers
from django.urls import reverse


# Serializers define the API representation.
class SupplySerializer(serializers.HyperlinkedModelSerializer):
    absolute_url = serializers.SerializerMethodField()

    def get_absolute_url(self, obj):
        request = self.context.get('request')
        base_url = f"{request.scheme}://{request.get_host()}"
        absolute_url = reverse('supplies-detail', args=[str(obj.code)])
        return f"{base_url}{absolute_url}"

    class Meta:
        model = Supplies
        fields = ["absolute_url", "id", "code", "name", "measure", "measure_units", "price"]


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Products
        fields = ['code', 'name', 'ref_id']


class CostSerializer(serializers.HyperlinkedModelSerializer):
    absolute_url = serializers.SerializerMethodField()

    def get_absolute_url(self, obj):
        request = self.context.get('request')
        base_url = f"{request.scheme}://{request.get_host()}"
        absolute_url = reverse('costs-detail', args=[str(obj.code)])
        return f"{base_url}{absolute_url}"

    class Meta:
        model = Costs
        fields = ["absolute_url", "id", "code", "product_code", "revenue", "current_price", "units", "measure_units", "production_time"]


class CostsDetailsSerializer(serializers.HyperlinkedModelSerializer):
    supply_name = serializers.CharField(source='supply_code.name', required=False, read_only=True)
    supply_measure_units = serializers.CharField(source='supply_code.measure_units', required=False, read_only=True)

    class Meta:
        model = CostsDetails
        fields = ["id", "cost_code", "supply_code", 'supply_name', "supply_measure_units", "amount", "type"]


class ComprasSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Compras
        fields = ["id", "data", "ticket_number", "provider", "notes", "amount"]

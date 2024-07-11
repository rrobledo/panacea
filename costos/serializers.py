from .models import Supplies, Products, Costs, CostsDetails, Compras
from rest_framework import serializers


# Serializers define the API representation.
class SupplySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Supplies
        fields = ["id", "code", "name", "measure", "measure_units", "price"]


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Products
        fields = ['code', 'name', 'ref_id']


class CostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Costs
        fields = ["id", "code", "product_code", "revenue", "current_price", "units", "measure_units", "production_time"]


class CostsDetailsSerializer(serializers.HyperlinkedModelSerializer):
    supply_name = serializers.CharField(source='supply_code.name')
    supply_measure_units = serializers.CharField(source='supply_code.measure_units')

    class Meta:
        model = CostsDetails
        fields = ["id", "cost_code", "supply_code", 'supply_name', "supply_measure_units", "amount", "type"]


class ComprasSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Compras
        fields = ["id", "data", "ticket_number", "provider", "notes", "amount"]

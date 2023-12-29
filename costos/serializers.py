from .models import Supplies, Products, Costs, CostsDetails
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
    class Meta:
        model = CostsDetails
        fields = ["cost_code", "supply_code", "amount", "type"]

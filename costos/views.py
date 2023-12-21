from .models import Supplies, Products, Costs, CostsDetails
from .serializers import SupplySerializer, ProductSerializer, CostSerializer, CostsDetailsSerializer
from rest_framework import viewsets


# ViewSets define the view behavior.
class SuppliesViewSet(viewsets.ModelViewSet):
    queryset = Supplies.objects.order_by("name").all()
    serializer_class = SupplySerializer


class ProductsViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer


class CostsViewSet(viewsets.ModelViewSet):
    queryset = Costs.objects.all()
    serializer_class = CostSerializer


class CostsDetailsViewSet(viewsets.ModelViewSet):
    queryset = CostsDetails.objects.all()
    serializer_class = CostsDetailsSerializer


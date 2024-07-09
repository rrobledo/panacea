from .models import Supplies, Products, Costs, CostsDetails, Compras
from .serializers import SupplySerializer, ProductSerializer, CostSerializer, CostsDetailsSerializer, ComprasSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_swagger.views import get_swagger_view

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
    serializer_class = CostsDetailsSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given cost,
        by filtering against a `cost` query parameter in the URL.
        """
        queryset = CostsDetails.objects.all()
        code_cost = self.kwargs.get('costo_pk')
        if code_cost is not None:
            queryset = queryset.filter(cost_code=code_cost)
        return queryset


class ComprasViewSet(viewsets.ModelViewSet):
    queryset = Compras.objects.all()
    serializer_class = ComprasSerializer

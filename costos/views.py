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
    serializer_class = CostsDetailsSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = CostsDetails.objects.all()
        code_cost = self.request.query_params.get('cost_code')
        if code_cost is not None:
            queryset = queryset.filter(cost_code=code_cost)
        return queryset

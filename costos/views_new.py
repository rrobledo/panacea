from .models import Insumos, Productos, Costos, Programacion
from .serializers import InsumosSerializer, ProductosSerializer, CostosSerializer, ProgramacionSerializer
from rest_framework import viewsets
from rest_framework import filters


# ViewSets define the view behavior.
class InsumosViewSet(viewsets.ModelViewSet):
    queryset = Insumos.objects.order_by("nombre").all()
    serializer_class = InsumosSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre']

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        name = self.request.query_params.get('nombre')
        if name is not None:
            return Insumos.objects.order_by("nombre").filter(nombre__icontains=name)
        return Insumos.objects.order_by("nombre").all()


class ProductosViewSet(viewsets.ModelViewSet):
    queryset = Productos.objects.order_by("nombre").all()
    serializer_class = ProductosSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        name = self.request.query_params.get('nombre')
        if name is not None:
            return Productos.objects.order_by("nombre").filter(nombre__icontains=name)
        return Productos.objects.order_by("nombre").all()


class CostosViewSet(viewsets.ModelViewSet):
    serializer_class = CostosSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given cost,
        by filtering against a `cost` query parameter in the URL.
        """
        queryset = Costos.objects.all()
        producto_id = self.kwargs.get('producto_pk')
        if producto_id is not None:
            queryset = queryset.filter(producto_id=producto_id)
        return queryset


class ProgramacionViewSet(viewsets.ModelViewSet):
    serializer_class = ProgramacionSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given cost,
        by filtering against a `cost` query parameter in the URL.
        """
        queryset = Programacion.objects.all()
        year = self.kwargs.get('year')
        if year is not None:
            queryset = queryset.filter(year=year)
        return queryset

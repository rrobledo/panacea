from .models import Insumos, Productos, Costos, Programacion
from .serializers import InsumosSerializer, ProductosSerializer, CostosSerializer, ProgramacionSerializer
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status


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
        queryset = Programacion.objects.order_by("producto__nombre").all()
        responsable = self.kwargs.get('responsable')
        if responsable is not None:
            if responsable != "Todos":
                queryset = queryset.filter(responsable=responsable)
        return queryset

    def partial_update(self, request, pk=None):
        if isinstance(request.data, list):
            for item in request.data:
                instance = Programacion.objects.get(id=item.get("id"))
                serializer = self.get_serializer(instance, data=item, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
        else:
            return super().partial_update(request.data, pk=pk)
        return Response(status=status.HTTP_200_OK)

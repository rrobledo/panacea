from .models import Insumos, Productos, Costos, Programacion, Remitos, RemitoDetalles, Clientes
from .serializers import (InsumosSerializer, ProductosSerializer, CostosSerializer,
                          ProgramacionSerializer, RemitosSerializer, RemitoDetallesSerializer, ClientesSerializer)
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.db import transaction, IntegrityError


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


class ClientesViewSet(viewsets.ModelViewSet):
    queryset = Clientes.objects.order_by("nom1").all()
    serializer_class = ClientesSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        nombre = self.request.query_params.get('nombre')
        if nombre is not None:
            return Clientes.objects.order_by("nom1").filter(Q(nom1__icontains=nombre) | Q(nom2__icontains=nombre))
        return Clientes.objects.order_by("nom1").all()


class RemitosViewSet(viewsets.ModelViewSet):
    queryset = Remitos.objects.order_by("fecha_entrega").all()
    serializer_class = RemitosSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given cost,
        by filtering against a `cost` query parameter in the URL.
        """
        queryset = Remitos.objects.order_by("fecha_entrega").all()
        cliente = self.request.query_params.get('cliente')
        if cliente is not None:
            queryset = queryset.filter(Q(cliente__nom1__icontains=cliente) | Q(cliente__nom2__icontains=cliente))
        estado = self.request.query_params.get('estado')
        if estado is not None and estado != "ALL":
            queryset = queryset.filter(estado=estado)
        return queryset


class ProgramacionViewSet(viewsets.ModelViewSet):
    serializer_class = ProgramacionSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given cost,
        by filtering against a `cost` query parameter in the URL.
        """
        queryset = Programacion.objects.order_by("producto__nombre").all()
        responsable = self.request.query_params.get('responsable')
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

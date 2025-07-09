from .models import Insumos, Productos, Costos, Programacion, Remitos, RemitoDetalles, Clientes, Proveedor, \
    CuentaCorrienteProveedor
from .serializers import (InsumosSerializer, ProductosSerializer, CostosSerializer,
                          ProgramacionSerializer, RemitosSerializer, RemitoDetallesSerializer, ClientesSerializer,
                          ProveedorSerializer, CuentaCorrienteProveedorSerializer)
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.db import transaction, IntegrityError
from . import produccion
from django.http import JsonResponse, HttpResponse


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
        return Productos.objects.order_by("prioridad", "nombre").all()


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


class ProgramacionViewSet(viewsets.ViewSet):
        """
        Example empty viewset demonstrating the standard
        actions that will be handled by a router class.

        If you're using format suffixes, make sure to also include
        the `format=None` keyword argument for each action.
        """

        def list(self, request):
            anio = self.request.query_params.get('anio')
            if anio is None:
                anio = 2025
            mes = self.request.query_params.get('mes')
            if mes is None:
                mes = 9
            responsable = self.request.query_params.get('responsable')
            semana = self.request.query_params.get('semana')
            res = produccion.get_programacion(request, anio, mes, responsable, semana)
            return JsonResponse(res, safe=False)

        def create(self, request):
            produccion.update_programacion(request.data)
            return Response(status=status.HTTP_204_NO_CONTENT)

        def retrieve(self, request, pk=None):
            pass

        def update(self, request, pk=None):
            pass

        def partial_update(self, request, pk=None):
            pass

        def destroy(self, request, pk=None):
            pass


class PlanificacionViewSet(viewsets.ViewSet):
    """
    Example empty viewset demonstrating the standard
    actions that will be handled by a router class.

    If you're using format suffixes, make sure to also include
    the `format=None` keyword argument for each action.
    """

    def list(self, request):
        anio = self.request.query_params.get('anio')
        if anio is None:
            anio = 2025
        res = produccion.get_planning(request, anio)
        return JsonResponse(res, safe=False)

    def create(self, request):
        produccion.update_planificacion(request.data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.order_by("nombre").all()
    serializer_class = ProveedorSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given cost,
        by filtering against a `cost` query parameter in the URL.
        """
        queryset = Proveedor.objects.order_by("nombre").all()
        nombre = self.request.query_params.get('nombre')
        if nombre is not None:
            queryset = queryset.filter(nombre__icontains=nombre)
        estado = self.request.query_params.get('estado')
        if estado is not None and estado != "ALL":
            queryset = queryset.filter(estado=estado)
        return queryset


class CuentaCorrienteProveedorViewSet(viewsets.ModelViewSet):
    queryset = CuentaCorrienteProveedor.objects.filter(tipo_movimiento="FACTURA").order_by("fecha_emision").all()
    serializer_class = CuentaCorrienteProveedorSerializer

    # def get_queryset(self):
    #     """
    #     Optionally restricts the returned purchases to a given cost,
    #     by filtering against a `cost` query parameter in the URL.
    #     """
    #     queryset = Factura.objects.order_by("nombre").all()
    #     nombre = self.request.query_params.get('nombre')
    #     if nombre is not None:
    #         queryset = queryset.filter(nombre__icontains=nombre)
    #     estado = self.request.query_params.get('estado')
    #     if estado is not None and estado != "ALL":
    #         queryset = queryset.filter(estado=estado)
    #     return queryset

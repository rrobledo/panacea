from .models import Insumos, Productos, Costos, Programacion, Planificacion2024, Clientes, Remitos, RemitoDetalles, \
    Planificacion, Proveedor, CuentaCorrienteProveedor, CuentaCorrienteProveedorAfect
from rest_framework import serializers
from django.urls import reverse
import base64

# Serializers define the API representation.
class InsumosSerializer(serializers.HyperlinkedModelSerializer):
    absolute_url = serializers.SerializerMethodField()

    def get_absolute_url(self, obj):
        request = self.context.get('request')
        base_url = f"{request.scheme}://{request.get_host()}"
        absolute_url = reverse('insumos-detail', args=[str(obj.id)])
        return f"{base_url}{absolute_url}"

    class Meta:
        model = Insumos
        fields = ["absolute_url", "id", "nombre", "unidad_medida", "cantidad", "precio"]


class ProductosSerializer(serializers.HyperlinkedModelSerializer):
    absolute_url = serializers.SerializerMethodField()

    def get_absolute_url(self, obj):
        request = self.context.get('request')
        base_url = f"{request.scheme}://{request.get_host()}"
        absolute_url = reverse('productos-detail', args=[str(obj.id)])
        return f"{base_url}{absolute_url}"

    class Meta:
        model = Productos
        fields = ["absolute_url", 'id', 'codigo', 'nombre', "ref_id", "utilidad", "precio_actual", "unidad_medida", "lote_produccion", "tiempo_produccion", "responsable", "categoria", "habilitado", "prioridad", "is_producto"]


class CostosSerializer(serializers.HyperlinkedModelSerializer):
    insumo_nombre = serializers.CharField(source='insumo.nombre', required=False, read_only=True)
    insumo_unidad_medida = serializers.CharField(source='insumo.unidad_medida', required=False, read_only=True)

    class Meta:
        model = Costos
        fields = ["id", "producto", "insumo", 'insumo_nombre', "insumo_unidad_medida", "cantidad"]


class ClientesSerializer(serializers.HyperlinkedModelSerializer):
    absolute_url = serializers.SerializerMethodField()

    def get_absolute_url(self, obj):
        request = self.context.get('request')
        base_url = f"{request.scheme}://{request.get_host()}"
        absolute_url = reverse('clientes-detail', args=[str(obj.id)])
        return f"{base_url}{absolute_url}"

    class Meta:
        model = Clientes
        fields = ["absolute_url", "id", "nombre"]


class RemitoDetallesSerializer(serializers.HyperlinkedModelSerializer):
    producto_id = serializers.CharField(source='producto.id', required=False, read_only=True)
    producto_nombre = serializers.CharField(source='producto.nombre', required=False, read_only=True)

    class Meta:
        model = RemitoDetalles
        fields = ["id", "remito", "producto", "producto_id", "producto_nombre" , "cantidad", "entregado", "observaciones"]


class RemitosSerializer(serializers.HyperlinkedModelSerializer):
    estado = serializers.SerializerMethodField()
    cliente_id = serializers.CharField(source='cliente.id', required=False, read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', required=False, read_only=True)
    productos = RemitoDetallesSerializer(many=True)

    def get_estado(self, obj):
        if obj.fecha_recibido:
            return "ENTREGADO"
        if obj.fecha_despacho:
            return "EN CAMINO"
        if obj.fecha_listo:
            return "PREPARADO"
        if obj.fecha_preparacion:
            return "EN_PREPARACION"
        if obj.fecha_preparacion:
            return "EN_PREPARACION"
        else:
            return "PENDIENTE"

    class Meta:
        model = Remitos
        fields = ["id", "cliente_id", "cliente_nombre", "cliente", "estado", "observaciones", "vendedor", "fecha_carga", "fecha_entrega", "fecha_preparacion", "fecha_listo", "fecha_despacho", "fecha_recibido", "fecha_facturacion", "productos"]


    def create(self, validated_data):
        productos_data = validated_data.pop('productos')
        remito = Remitos.objects.create(**validated_data)
        for producto_data in productos_data:
            if producto_data.get("cantidad") > 0:
                RemitoDetalles.objects.create(remito=remito, **producto_data)
        return remito

    def update(self, remito, validated_data):
        productos = RemitoDetalles.objects.filter(remito_id=remito.id)
        productos_data = validated_data.pop('productos')
        diff = productos - productos_data
        return  remito

class ProgramacionSerializer(serializers.HyperlinkedModelSerializer):
    producto_nombre = serializers.SerializerMethodField()
    planeado = serializers.SerializerMethodField()

    def get_producto_nombre(self, obj):
        if obj.producto:
            return obj.producto.nombre
        else:
            return obj.producto_nombre

    def get_planeado(self, obj):
        planificado = None
        planeado = None
        try:
            planificado = Planificacion2024.objects.get(codigo=int(obj.producto.ref_id))
        except:
            planificado = None
        if planificado:
            planeado = planificado.jul2024corr
        return planeado


    class Meta:
        model = Programacion
        fields = ["id", "producto", "producto_nombre", "planeado", "responsable", "s01_lunes_plan", "s01_lunes_real", "s01_martes_plan", "s01_martes_real", "s01_miercoles_plan", "s01_miercoles_real", "s01_jueves_plan", "s01_jueves_real", "s01_viernes_plan", "s01_viernes_real", "s01_sabado_plan", "s01_sabado_real", "s02_lunes_plan", "s02_lunes_real", "s02_martes_plan", "s02_martes_real", "s02_miercoles_plan", "s02_miercoles_real", "s02_jueves_plan", "s02_jueves_real", "s02_viernes_plan", "s02_viernes_real", "s02_sabado_plan", "s02_sabado_real", "s03_lunes_plan", "s03_lunes_real", "s03_martes_plan", "s03_martes_real", "s03_miercoles_plan", "s03_miercoles_real", "s03_jueves_plan", "s03_jueves_real", "s03_viernes_plan", "s03_viernes_real", "s03_sabado_plan", "s03_sabado_real", "s04_lunes_plan", "s04_lunes_real", "s04_martes_plan", "s04_martes_real", "s04_miercoles_plan", "s04_miercoles_real", "s04_jueves_plan", "s04_jueves_real", "s04_viernes_plan", "s04_viernes_real", "s04_sabado_plan", "s04_sabado_real"]


class PlanificacionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Planificacion
        fields = ["id", "producto_nombre"]


class ProveedorSerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField()

    def get_absolute_url(self, obj):
        request = self.context.get('request')
        base_url = f"{request.scheme}://{request.get_host()}"
        absolute_url = reverse('proveedores-detail', args=[str(obj.id)])
        return f"{base_url}{absolute_url}"

    class Meta:
        model = Proveedor
        fields = [
            "absolute_url", 'id', 'nombre', 'cuit', 'direccion', 'telefono',
            'email', 'fecha_alta', 'estado'
        ]

class CuentaCorrienteProveedorSerializer(serializers.ModelSerializer):
    proveedor_id = serializers.CharField(source='proveedor.id', required=False, read_only=True)
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', required=False, read_only=True)
    factura_id = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = CuentaCorrienteProveedor
        fields = [
            'id', "proveedor_id", "proveedor_nombre", 'proveedor', 'tipo_movimiento', 'numero', 'fecha_emision',
            'observaciones', 'fecha_vencimiento', 'importe_total', 'categoria',
            'estado', 'caja', 'tipo_pago', 'image', 'factura_id'
        ]

    def create(self, validated_data):
        if validated_data.get('tipo_movimiento') == 'PAGO':
            factura_id = validated_data.pop("factura_id", None)
            if factura_id:
                comprobante = CuentaCorrienteProveedor.objects.create(**validated_data)
                CuentaCorrienteProveedorAfect.objects.create(factura_id=factura_id,
                                                             pago_id=comprobante.id,
                                                             importe=comprobante.importe_total)
        else:
            if validated_data.get('tipo_pago') == 'EFECTIVO' or validated_data.get('tipo_pago') == 'TRANSFERENCIA':
                validated_data["estado"] = "PAGADO"
            comprobante = CuentaCorrienteProveedor.objects.create(**validated_data)
        return comprobante

    def update(self, comprobante, validated_data):
        if validated_data.get('tipo_pago') == 'EFECTIVO' or validated_data.get('tipo_pago') == 'TRANSFERENCIA':
            validated_data["estado"] = "PAGADO"
        instance = super().update(comprobante, validated_data)
        return  instance

class CuentaCorrienteProveedorReadSerializer(serializers.ModelSerializer):
    proveedor_id = serializers.CharField(source='proveedor.id', required=False, read_only=True)
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', required=False, read_only=True)

    class Meta:
        model = CuentaCorrienteProveedor
        fields = [
            'id', "proveedor_id", "proveedor_nombre", 'proveedor', 'tipo_movimiento', 'numero', 'fecha_emision',
            'observaciones', 'fecha_vencimiento', 'importe_total', 'categoria',
            'estado', 'caja', 'tipo_pago'
        ]


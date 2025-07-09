from django.db import models


class Insumos(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=50, default="")
    nombre = models.CharField(max_length=250)
    unidad_medida = models.CharField(max_length=10, default="GR")
    cantidad = models.FloatField()
    precio = models.FloatField()


class Productos(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=50)
    categoria = models.CharField(max_length=250, default='PANADERIA')
    nombre = models.CharField(max_length=250)
    ref_id = models.CharField(max_length=250, null=True)
    utilidad = models.FloatField()
    precio_actual = models.FloatField()
    unidad_medida = models.CharField(max_length=10, default="GR")
    lote_produccion = models.IntegerField()
    tiempo_produccion = models.IntegerField(default=0)
    responsable = models.CharField(max_length=50, default="Todos")
    is_producto = models.BooleanField(default=True)
    habilitado = models.BooleanField(default=True)
    prioridad = models.IntegerField(default=10)


class ProductosRef(models.Model):
    id = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Productos, on_delete=models.RESTRICT)
    ref_id = models.CharField(max_length=250, null=True)
    unidad_conversion = models.IntegerField(default=1)

class Costos(models.Model):
    id = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Productos, on_delete=models.RESTRICT)
    insumo =  models.ForeignKey(Insumos, on_delete=models.RESTRICT)
    cantidad = models.IntegerField()


class Clientes(models.Model):
    id = models.IntegerField(db_column="idcliente", unique=True, primary_key=True)
    nom1 = models.CharField(db_column="nom1")
    nom2 = models.CharField(db_column="nom2")

    @property
    def nombre(self):
        return f'{self.nom1}, {self.nom2}'

    class Meta:
        db_table = "clientes"
        managed = False


class Remitos(models.Model):
    id = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Clientes, on_delete=models.RESTRICT, null=True)
    observaciones = models.CharField(max_length=1000, null=True)
    vendedor = models.CharField(max_length=255)

    fecha_carga = models.DateTimeField(auto_now=True)
    fecha_entrega = models.DateTimeField()
    fecha_preparacion = models.DateTimeField(null=True)
    fecha_listo = models.DateTimeField(null=True)
    fecha_despacho = models.DateTimeField(null=True)
    fecha_recibido = models.DateTimeField(null=True)
    fecha_facturacion = models.DateTimeField(null=True)


class RemitoDetalles(models.Model):
    id = models.AutoField(primary_key=True)
    remito = models.ForeignKey(Remitos, related_name='productos', on_delete=models.RESTRICT, null=True)
    producto = models.ForeignKey(Productos, on_delete=models.RESTRICT)
    cantidad = models.IntegerField()
    entregado = models.IntegerField(null=True)
    observaciones = models.CharField(max_length=1000, null=True)



class Programacion(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateField(null=True)
    producto = models.ForeignKey(Productos, on_delete=models.RESTRICT, null=True)
    producto_nombre = models.CharField(max_length=255, null=True)
    responsable = models.CharField(max_length=50)

    plan = models.IntegerField(null=True)
    prod = models.IntegerField(null=True)


class Planificacion(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateField(null=True)
    producto = models.ForeignKey(Productos, on_delete=models.RESTRICT, null=True)
    plan = models.IntegerField(null=True)
    sistema = models.IntegerField(null=True)
    corregido = models.IntegerField(null=True)
    indice = models.FloatField(null=True)


class Planificacion2024(models.Model):
    codigo = models.IntegerField(default=0, primary_key=True)
    productos = models.CharField(max_length=50)
    jan2024 = models.IntegerField(default=0)
    feb2024 = models.IntegerField(default=0)
    mar2024 = models.IntegerField(default=0)
    apr2024 = models.IntegerField(default=0)
    may2024 = models.IntegerField(default=0)
    may2024corr = models.IntegerField(default=0)
    jun2024 = models.IntegerField(default=0)
    jun2024corr = models.IntegerField(default=0)
    jul2024 = models.IntegerField(default=0)
    jul2024corr = models.IntegerField(default=0)
    aug2024 = models.IntegerField(default=0)
    sep2024 = models.IntegerField(default=0)
    oct2024 = models.IntegerField(default=0)
    nov2024 = models.IntegerField(default=0)
    dec2024 = models.IntegerField(default=0)

    class Meta:
        db_table = "planificacion2024"
        managed = False

class Proveedor(models.Model):
    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
    ]

    nombre = models.CharField(max_length=255)
    cuit = models.CharField(max_length=20, unique=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    fecha_alta = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="activo")


class CuentaCorrienteProveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.RESTRICT, null=False)
    tipo_movimiento = models.CharField(max_length=250, default='GASTO')
    numero = models.CharField(max_length=50)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField(blank=True, null=True)
    importe_total = models.DecimalField(max_digits=15, decimal_places=2)
    observaciones = models.CharField(max_length=250, null=True)
    categoria = models.CharField(max_length=250, default='MATERIA_PRIMA')
    tipo_pago = models.CharField(max_length=250, default='CUENTA_CORRIENTE')
    caja = models.CharField(max_length=250, default='VA')
    estado = models.CharField(max_length=250, default='PENDIENTE')


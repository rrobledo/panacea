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

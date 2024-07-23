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

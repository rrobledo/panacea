from django.db import models


class Supplies(models.Model):
    code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=250)
    measure = models.FloatField()
    measure_units = models.CharField(max_length=10, default="GR")
    price = models.FloatField()

    @property
    def id(self):
        return f"{self.code}/"


class Products(models.Model):
    code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=250)


class Costs(models.Model):
    code = models.CharField(max_length=50, primary_key=True)
    product_code = models.ForeignKey(Products, on_delete=models.CASCADE)
    revenue = models.FloatField()
    current_price = models.FloatField()
    units = models.IntegerField()
    measure_units = models.CharField(max_length=10, default="GR")
    production_time = models.IntegerField(default=0)

    @property
    def id(self):
        return f"{self.code}/"


class CostsDetails(models.Model):
    id = models.AutoField(primary_key=True)
    COST_TYPES = [
        ("F", "Fixed"),
        ("V", "Variable"),
    ]
    cost_code = models.ForeignKey(Costs, on_delete=models.CASCADE)
    supply_code = models.ForeignKey(Supplies, on_delete=models.CASCADE)
    amount = models.IntegerField()
    type = models.CharField(max_length=1, choices=COST_TYPES)


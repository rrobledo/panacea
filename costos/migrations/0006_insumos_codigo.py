# Generated by Django 4.2.1 on 2024-07-22 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0005_insumos_productos_alter_costs_product_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='insumos',
            name='codigo',
            field=models.CharField(default='', max_length=20),
        ),
    ]

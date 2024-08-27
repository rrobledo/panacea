# Generated by Django 4.2.1 on 2024-08-13 16:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0017_rename_fecha_entregado_remitos_fecha_despacho_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remitodetalles',
            name='entregado',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='remitodetalles',
            name='remito',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='costos.remitos'),
        ),
    ]
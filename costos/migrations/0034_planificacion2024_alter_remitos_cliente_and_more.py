# Generated by Django 4.2.1 on 2025-07-07 03:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0033_planificacion2024_remove_factura_proveedor_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CuentaCorrienteProveedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=50)),
                ('fecha_emision', models.DateField()),
                ('fecha_vencimiento', models.DateField(blank=True, null=True)),
                ('importe_total', models.DecimalField(decimal_places=2, max_digits=15)),
                ('observaciones', models.CharField(max_length=250, null=True)),
                ('categoria', models.CharField(default='MATERIA_PRIMA', max_length=250)),
                ('tipo_movimiento', models.CharField(default='GASTO', max_length=250)),
                ('estado', models.CharField(default='PENDIENTE', max_length=250)),
                ('proveedor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='facturas', to='costos.proveedor')),
            ],
        ),
    ]

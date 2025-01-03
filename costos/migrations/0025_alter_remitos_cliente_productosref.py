# Generated by Django 4.2.1 on 2024-11-01 00:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0024_productos_is_producto_alter_remitos_cliente'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductosRef',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ref_id', models.CharField(max_length=250, null=True)),
                ('unidad_conversion', models.IntegerField(default=1)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='costos.productos')),
            ],
        ),
    ]

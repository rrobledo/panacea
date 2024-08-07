# Generated by Django 4.2.1 on 2024-08-06 16:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0015_planificacion_alter_programacion_producto'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clientes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idcliente', models.IntegerField(unique=True)),
                ('nom1', models.CharField()),
                ('nom2', models.CharField()),
            ],
            options={
                'db_table': 'clientes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Planificacion',
            fields=[
                ('codigo', models.IntegerField(default=0, primary_key=True, serialize=False)),
                ('productos', models.CharField(max_length=50)),
                ('jan2024', models.IntegerField(default=0)),
                ('feb2024', models.IntegerField(default=0)),
                ('mar2024', models.IntegerField(default=0)),
                ('apr2024', models.IntegerField(default=0)),
                ('may2024', models.IntegerField(default=0)),
                ('may2024corr', models.IntegerField(default=0)),
                ('jun2024', models.IntegerField(default=0)),
                ('jun2024corr', models.IntegerField(default=0)),
                ('jul2024', models.IntegerField(default=0)),
                ('jul2024corr', models.IntegerField(default=0)),
                ('aug2024', models.IntegerField(default=0)),
                ('sep2024', models.IntegerField(default=0)),
                ('oct2024', models.IntegerField(default=0)),
                ('nov2024', models.IntegerField(default=0)),
                ('dec2024', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'planificacion2024',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Remitos',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('observaciones', models.CharField(max_length=1000, null=True)),
                ('vendedor', models.CharField(max_length=255)),
                ('fecha_carga', models.DateTimeField(auto_now=True)),
                ('fecha_pedido', models.DateTimeField()),
                ('fecha_preparacion', models.DateTimeField(null=True)),
                ('fecha_listo', models.DateTimeField(null=True)),
                ('fecha_entregado', models.DateTimeField(null=True)),
                ('fecha_recibido', models.DateTimeField(null=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='costos.clientes', to_field='idcliente')),
            ],
        ),
        migrations.CreateModel(
            name='RemitoDetalles',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cantidad', models.IntegerField()),
                ('entregado', models.IntegerField()),
                ('observaciones', models.CharField(max_length=1000, null=True)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='costos.productos')),
                ('remito', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='costos.remitos')),
            ],
        ),
    ]

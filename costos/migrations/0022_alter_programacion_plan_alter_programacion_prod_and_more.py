# Generated by Django 4.2.1 on 2024-09-23 02:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0021_productos_categoria_alter_remitos_cliente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programacion',
            name='plan',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='programacion',
            name='prod',
            field=models.IntegerField(null=True),
        )
    ]
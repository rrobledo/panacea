# Generated by Django 4.2.1 on 2024-09-18 23:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0020_alter_programacion_fecha_alter_remitos_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='productos',
            name='categoria',
            field=models.CharField(default='PANADERIA', max_length=250),
        )
    ]

# Generated by Django 4.2.1 on 2024-07-22 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0008_alter_insumos_codigo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productos',
            name='codigo',
            field=models.CharField(max_length=50),
        ),
    ]

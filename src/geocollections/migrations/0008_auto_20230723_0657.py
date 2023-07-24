# Generated by Django 3.2.18 on 2023-07-23 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geocollections', '0007_shptogeojson'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shptogeojson',
            name='geojson_data',
        ),
        migrations.AddField(
            model_name='shptogeojson',
            name='shp_geojson_data',
            field=models.JSONField(null=True),
        ),
    ]
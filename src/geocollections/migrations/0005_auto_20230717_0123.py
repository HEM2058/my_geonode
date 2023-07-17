# Generated by Django 3.2.18 on 2023-07-17 01:23

from django.db import migrations, models
import geocollections.models


class Migration(migrations.Migration):

    dependencies = [
        ('geocollections', '0004_geocollection_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='geocollection',
            name='image_folder',
            field=models.FileField(blank=True, null=True, upload_to=geocollections.models.get_image_folder),
        ),
        migrations.AddField(
            model_name='geocollection',
            name='zip_file',
            field=models.FileField(blank=True, null=True, upload_to='zip_files/'),
        ),
    ]

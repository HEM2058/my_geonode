from django.db import models
import os
import zipfile
from django.db import models
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from geonode.base.models import ResourceBase
from geonode.groups.models import GroupProfile


def get_image_folder(instance, filename):
    return os.path.join(instance.category, filename)

class Geocollection(models.Model):
    CATEGORY_CHOICES = [
        ('cooperatives', 'Cooperatives'),
        ('forest-offices', 'Forest Offices'),
        ('health-institutions', 'Health Institutions'),
        ('heat-institutions', 'Heat Institutions'),
        ('municipal-offices', 'Municipal Offices'),
        ('religious-places', 'Religious Places'),
        ('schools', 'Schools'),
        ('security-offices', 'Security Offices'),
        ('tourism', 'Tourism'),
        ('others', 'Others'),
    ]

    geojson_data = models.JSONField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True)
    image_folder = models.FileField(upload_to=get_image_folder, blank=True, null=True)
    zip_file = models.FileField(upload_to='zip_files/', blank=True, null=True)
    print("Uploaded Zip file")
    def __str__(self):
        return self.category

    def extract_zip_file(self):
        if self.zip_file:
            zip_file_path = self.zip_file.path
            print("zip file path:", zip_file_path)
            category_folder_path = os.path.join(settings.MEDIA_ROOT, self.category)
            os.makedirs(category_folder_path, exist_ok=True)
            print("Extracting zip file:", zip_file_path)
            print("Destination folder:", category_folder_path)

            # Delete previously extracted files
            if self.image_folder:
                for file_name in os.listdir(self.image_folder.path):
                    file_path = os.path.join(self.image_folder.path, file_name)
                    os.remove(file_path)

            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(category_folder_path)

            self.image_folder = category_folder_path
            self.save()
            print("Zip file extraction complete")
            
@receiver(post_save, sender=Geocollection)
def handle_zip_file_extraction(sender, instance, created, **kwargs):
    if created and instance.zip_file:
        print("Handling zip file extraction...")
        instance.extract_zip_file()

            
    

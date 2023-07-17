from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Geocollection

@receiver(post_save, sender=Geocollection)
def handle_zip_file_extraction(sender, instance, created, **kwargs):
    if created and instance.zip_file:
        print("Handle zip file extraction called")
        instance.extract_zip_file()


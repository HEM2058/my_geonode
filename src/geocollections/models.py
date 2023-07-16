from django.db import models


from geonode.base.models import ResourceBase
from geonode.groups.models import GroupProfile


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
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES,null=True)
    
    def __str__(self):
        return self.category
    

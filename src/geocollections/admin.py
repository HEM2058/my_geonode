from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Geocollection,SHPtoGeojson



@admin.register(Geocollection)
class GeocollectionAdmin(admin.ModelAdmin):
    readonly_fields = ('display_geojson_data',)

    def display_geojson_data(self, instance):
        return instance.geojson_data

    display_geojson_data.short_description = 'GeoJSON Data'
    

@admin.register(SHPtoGeojson)
class SHPtoGeojson(admin.ModelAdmin):
    readonly_fields = ('display_geojson_data',)

    def display_geojson_data(self, instance):
        return instance.geojson_data

    display_geojson_data.short_description = 'GeoJSON Data'
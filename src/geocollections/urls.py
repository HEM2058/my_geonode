from django.conf.urls import url
from django.urls import path
from .views import GeoCollections,DatasetsUpload,convert_csv_to_geojson

urlpatterns = [
   
     path('Map/', GeoCollections, name='geocollections'),
     path('Upload_datasets/', DatasetsUpload, name='DatasetsUpload'),
     # URL pattern for converting CSV to GeoJSON
    path('convert-csv-to-geojson/', convert_csv_to_geojson, name='convert_csv_to_geojson'),
]
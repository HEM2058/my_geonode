from django.conf.urls import url
from django.urls import path
from .views import GeoCollections,DatasetsUpload,convert_csv_to_geojson,ShpUpload,convert_shp_to_geojson
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
   
     path('Map/', GeoCollections, name='geocollections'),
     path('Upload_datasets/', DatasetsUpload, name='DatasetsUpload'),
     path('Upload_shp_files/', ShpUpload, name='ShpUpload'),
     # URL pattern for converting CSV to GeoJSON
     path('convert-csv-to-geojson/', convert_csv_to_geojson, name='convert_csv_to_geojson'),
    # URL pattern for converting shp to GeoJSON
     path('convert-shp-to-geojson/', convert_shp_to_geojson, name='convert_shp_to_geojson'),
     path('convert-shapefile/', convert_shp_to_geojson.as_view(), name='convert_shapefile'),
]+static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
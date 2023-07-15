from django.conf.urls import url
from django.urls import path
from .views import GeoCollections,DatasetsUpload

urlpatterns = [
   
     path('Map/', GeoCollections, name='geocollections'),
     path('Upload_datasets/', DatasetsUpload, name='DatasetsUpload'),
]
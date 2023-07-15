from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import request,HttpResponse


def GeoCollections(request):
    return render(request,'geocollections/geocollection_detail.html')

def DatasetsUpload(request):
    return render(request,'geocollections/upload.html')
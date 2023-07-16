from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import request,HttpResponse
import csv
import json
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Geocollection

def GeoCollections(request):
    geocollection_objects = Geocollection.objects.all()
    geojson_data = []
    print(geocollection_objects)
    for geocollection in geocollection_objects:
        
        geojson_data.append(geocollection.geojson_data)

    return render(request, 'geocollections/geocollection_detail.html', {'geojson_data': geojson_data,'geocollection_objects':geocollection_objects})


def DatasetsUpload(request):
    if request.user.is_superuser:
        return render(request, 'geocollections/upload.html')
    else:
        return HttpResponse('You are not authorized to access this page.')
    


@csrf_exempt
def convert_csv_to_geojson(request):
    if request.method == 'POST' and 'file' in request.FILES:
        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({'error': 'Invalid file format. Please upload a CSV file.'})

        csv_data = csv.reader(csv_file.read().decode('utf-8').splitlines())
        header = next(csv_data)

        longitude_field = request.POST.get('longitude')
        latitude_field = request.POST.get('latitude')
        elevation_field = request.POST.get('elevation')

        if not longitude_field or not latitude_field or not elevation_field:
            return JsonResponse({'error': 'Invalid field selection. Please select the longitude, latitude, and elevation fields.'})

        # Get the selected category
        category = request.POST.get('category')

        data = []
        for row in csv_data:
            longitude_index = header.index(longitude_field)
            latitude_index = header.index(latitude_field)
            elevation_index = header.index(elevation_field)

            if (
                not row[longitude_index] or
                not row[latitude_index] or
                not row[elevation_index]
            ):
                continue  # Skip the row if any of the required fields are empty

            try:
                longitude = float(row[longitude_index])
                latitude = float(row[latitude_index])
                elevation = float(row[elevation_index])
            except ValueError:
                return JsonResponse({'error': 'Invalid values found. Longitude, latitude, and elevation fields must contain numeric values.'})

            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [longitude, latitude, elevation],
                },
                'properties': {},
            }

            # Add additional properties from other columns in the CSV
            for index, value in enumerate(row):
                if index != longitude_index and index != latitude_index and index != elevation_index:
                    column_name = header[index]
                    feature['properties'][column_name] = value

            data.append(feature)

        geojson_data = {
            'type': 'FeatureCollection',
            'features': data,
            'crs': {
                'type': 'EPSG',
                'properties': {
                    'code': 4326,  # WGS 1984 coordinate system
                },
            },
        }

        # Create or update a Geocollection object with the category
        geocollection = Geocollection.objects.create(geojson_data=geojson_data, category=category)

        # Return the success response
        response_data = {
            'success': 'File converted and saved successfully.',
            'geocollection_id': geocollection.id
        }
        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request.'})

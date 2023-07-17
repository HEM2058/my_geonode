from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import request,HttpResponse
import csv
from django.core.files.base import ContentFile
import json
import os
import zipfile
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Geocollection
from django.contrib.sites.shortcuts import get_current_site

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
    if request.method == 'POST' and 'file' in request.FILES and 'images' in request.FILES:
        csv_file = request.FILES['file']
        zip_file = request.FILES['images']
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({'error': 'Invalid file format. Please upload a CSV file.'})

        csv_data = csv.reader(csv_file.read().decode('utf-8').splitlines())
        header = [h.strip() for h in next(csv_data)]  # Remove leading/trailing whitespace characters

        longitude_field = request.POST.get('longitude')
        latitude_field = request.POST.get('latitude')
        elevation_field = request.POST.get('elevation')
        image_link_field = request.POST.get('image_link').strip()  # Remove leading/trailing whitespace characters
        print(image_link_field)
        print(elevation_field)
        if not longitude_field or not latitude_field or not elevation_field or not image_link_field:
            return JsonResponse({'error': 'Invalid field selection. Please select the longitude, latitude, elevation, and image link fields.'})

        # Get the selected category
        category = request.POST.get('category')

        data = []
        for row in csv_data:
            if len(row) != len(header):
                continue  # Skip rows with different column counts

            row = [value.strip() for value in row]  # Remove leading/trailing whitespace characters

            try:
                longitude_index = header.index(longitude_field)
                latitude_index = header.index(latitude_field)
                elevation_index = header.index(elevation_field)
                image_link_index = header.index(image_link_field)
            except ValueError:
                return JsonResponse({'error': 'Invalid field selection. Please select valid field names.'})

            if (
                not row[longitude_index]
                or not row[latitude_index]
                or not row[elevation_index]
            ):
                continue  # Skip the row if any of the required fields (longitude, latitude, elevation) are empty

            try:
                longitude = float(row[longitude_index])
                latitude = float(row[latitude_index])
                elevation = float(row[elevation_index])
                image_link = row[image_link_index] if image_link_index < len(row) else ''  # Handle cases where image_link is missing
            except ValueError:
                return JsonResponse({'error': 'Invalid values found. Longitude, latitude, elevation, and image link fields must contain numeric values.'})

            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [longitude, latitude, elevation],
                },
                'properties': {
                    'image_link': image_link,  # Add the image link property
                },
            }

            # Add additional properties from other columns in the CSV
            for index, value in enumerate(row):
                if index not in [longitude_index, latitude_index, elevation_index, image_link_index]:
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

        # Check if a Geocollection object with the category already exists
        geocollection = Geocollection.objects.filter(category=category).first()

        if geocollection:
            # Delete the existing zip file and extracted images
            if geocollection.zip_file:
                geocollection.zip_file.delete()

            if geocollection.image_folder:
                for file_name in os.listdir(geocollection.image_folder.path):
                    file_path = os.path.join(geocollection.image_folder.path, file_name)
                    os.remove(file_path)

            # Save the new zip file
            geocollection.zip_file.save(zip_file.name, zip_file)

            # Extract the zip file
            geocollection.extract_zip_file()
            
            # Construct image URLs based on the media folder, localhost URL, and category folder
            localhost_url = request.build_absolute_uri('/')[:-1]

            media_url = settings.MEDIA_URL
            category_folder = geocollection.category

            image_folder_path = geocollection.image_folder.path
            for file_name in os.listdir(image_folder_path):
                 file_path = os.path.join(image_folder_path, file_name)
                 if os.path.isfile(file_path):
                   relative_url = file_path.replace(image_folder_path, '').lstrip('/')
                   image_url = f"{localhost_url}/geocollections{media_url}/{category_folder}/{relative_url}"
                   print(f"Image URL: {image_url}")

           

            # Override the existing Geocollection with the new data and category
            geocollection.geojson_data = geojson_data
            geocollection.save()
        else:
            # Create a new Geocollection object with the category
            geocollection = Geocollection.objects.create(
                geojson_data=geojson_data,
                category=category,
                zip_file=zip_file
            )

            # Extract the zip file
            geocollection.extract_zip_file()

        # Return the success response
        response_data = {
            'success': 'File converted and saved successfully.',
            'geocollection_id': geocollection.id,
        }
        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request.'})
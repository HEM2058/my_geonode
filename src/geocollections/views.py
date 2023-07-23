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
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ShapefileUploadSerializer, ConvertedDataSerializer
from .models import *
import zipfile
import tempfile
import shapefile

def GeoCollections(request):
    geocollection_objects = Geocollection.objects.all()
    geojson_data = []
    shp_geojson_data = {}
    all_data = SHPtoGeojson.objects.all()
    for geocollection in geocollection_objects:
         geojson_data.append(geocollection.geojson_data)

    for data in all_data:
        shp_geojson_data[data.id] = data.shp_geojson_data

    return render(request, 'geocollections/geocollection_detail.html', {'geojson_data': geojson_data,'geocollection_objects':geocollection_objects,'shp_geojson_data': shp_geojson_data})



    
 

def DatasetsUpload(request):
    if request.user.is_superuser:
        return render(request, 'geocollections/upload.html')
    else:
        return HttpResponse('You are not authorized to access this page.')
    
def ShpUpload(request):
    if request.user.is_superuser:
        return render(request, 'geocollections/uploadshp.html')
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

            # Create a list to store the image URLs
            image_urls = []
    
            for file_name in os.listdir(image_folder_path):
                file_path = os.path.join(image_folder_path, file_name)
                if os.path.isfile(file_path):
                    relative_url = file_path.replace(image_folder_path, '').lstrip('/')
                    image_url = f"{localhost_url}/geocollections{media_url}/{category_folder}/{relative_url}"
                    # Add the image URL to the list
                    image_urls.append(image_url)
                    # Sort the list of image URLs in alphabetical order
            image_urls.sort()
            # Now the image_urls list is sorted in alphabetical order
            print("Sorted image URLs:")
            for url in image_urls:
                   print(url)
            # Assign the image URLs to the corresponding image_link in the GeoJSON features
            for i, feature in enumerate(data):
                if i < len(image_urls):
                    feature['properties']['image_link'] = image_urls[i]
                else:
                    feature['properties']['image_link'] = ''

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



class convert_shp_to_geojson(APIView):
    def post(self, request):
        print("Inside function")
        serializer = ShapefileUploadSerializer(data=request.data)
        if serializer.is_valid():
            zip_file = serializer.validated_data['zip_file']

            # Create a temporary directory to extract the contents of the zip file
            temp_dir = tempfile.TemporaryDirectory()

            try:
                # Extract the contents of the zip file to the temporary directory
                with zipfile.ZipFile(zip_file, 'r') as z:
                    z.extractall(temp_dir.name)

                # Find the .shp file in the extracted contents
                shapefile_path = None
                for root, dirs, files in os.walk(temp_dir.name):
                    for file in files:
                        if file.endswith(".shp"):
                            shapefile_path = os.path.join(root, file)
                            break
                    if shapefile_path:
                        break

                if shapefile_path:
                    # Read Shapefile and convert to GeoJSON
                    shape_reader = shapefile.Reader(shapefile_path)
                    fields = shape_reader.fields[1:]
                    field_names = [field[0] for field in fields]
                    features = []
                    for shape_record in shape_reader.shapeRecords():
                        geometry = shape_record.shape.__geo_interface__
                        attributes = dict(zip(field_names, shape_record.record))
                        features.append({
                            'type': 'Feature',
                            'geometry': geometry,
                            'properties': attributes
                        })
                    geojson_data = {
                        'type': 'FeatureCollection',
                        'features': features
                    }

                    # Save the converted GeoJSON to the database
                    converted_data = SHPtoGeojson.objects.create(shp_geojson_data=geojson_data)

                    converted_serializer = ConvertedDataSerializer(converted_data)
                    return Response(converted_serializer.data, status=status.HTTP_201_CREATED)
                 
                else:
                    return Response({'error': 'Shapefile not found in the uploaded ZIP file.'}, status=status.HTTP_400_BAD_REQUEST)

            finally:
                # Clean up extracted files and temporary directory
                temp_dir.cleanup()

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
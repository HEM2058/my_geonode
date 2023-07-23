from rest_framework import serializers
from .models import SHPtoGeojson
class ShapefileUploadSerializer(serializers.Serializer):
    zip_file = serializers.FileField()

class ConvertedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SHPtoGeojson
        fields = ('shp_geojson_data',)

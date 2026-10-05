from rest_framework import serializers
from .models import Hotel, HotelService

class HotelServiceSerializer(serializers.ModelSerializer):
    class Meta: model=HotelService; fields=("id","name","slug","short_description","description","icon","image_url","starting_price","is_featured")
class HotelSerializer(serializers.ModelSerializer):
    services=HotelServiceSerializer(many=True,read_only=True)
    class Meta:
        model=Hotel; exclude=("is_active",); read_only_fields=("id","created_at","updated_at")

from rest_framework import serializers
from .models import Amenity, Room, RoomType

class AmenitySerializer(serializers.ModelSerializer):
    class Meta: model=Amenity; fields=("id","name","icon")
class RoomTypeSerializer(serializers.ModelSerializer):
    amenities=AmenitySerializer(many=True,read_only=True); available_rooms=serializers.IntegerField(read_only=True)
    class Meta: model=RoomType; fields=("id","name","slug","description","capacity","base_rate","size_sqm","bed_description","image_url","amenities","available_rooms")
class RoomSerializer(serializers.ModelSerializer):
    room_type_name=serializers.CharField(source="room_type.name",read_only=True)
    room_type_base_rate=serializers.DecimalField(source='room_type.base_rate',max_digits=12,decimal_places=2,read_only=True)
    class Meta: model=Room; fields="__all__"; read_only_fields=("id","created_at","updated_at")

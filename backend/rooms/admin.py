from django.contrib import admin
from .models import Amenity, Room, RoomType
admin.site.register(Amenity); admin.site.register(RoomType)
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin): list_display=("number","room_type","occupancy_status","cleaning_status","is_active"); list_filter=("occupancy_status","cleaning_status","room_type")

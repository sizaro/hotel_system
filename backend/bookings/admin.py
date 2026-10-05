from django.contrib import admin
from .models import Booking, GuestProfile
admin.site.register(GuestProfile)
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin): list_display=("reference","guest","room_type","arrival_date","departure_date","status"); list_filter=("status","arrival_date","room_type"); search_fields=("reference","guest__first_name","guest__last_name","guest__email")

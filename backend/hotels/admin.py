from django.contrib import admin
from .models import AuditLog, Hotel, HotelService

class HotelServiceInline(admin.TabularInline): model=HotelService; extra=0
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin): list_display=("name","city","country","currency","is_active","updated_at"); inlines=(HotelServiceInline,)
admin.site.register(AuditLog)

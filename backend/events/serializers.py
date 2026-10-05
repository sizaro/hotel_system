from rest_framework import serializers
from .models import EventBooking,EventService,EventTask,EventType,Venue
class VenueSerializer(serializers.ModelSerializer):
    class Meta:model=Venue;fields='__all__'
class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:model=EventType;fields='__all__'
class EventServiceSerializer(serializers.ModelSerializer):
    class Meta:model=EventService;fields='__all__';read_only_fields=('amount',)
class EventTaskSerializer(serializers.ModelSerializer):
    class Meta:model=EventTask;fields='__all__'
class EventBookingSerializer(serializers.ModelSerializer):
    services=EventServiceSerializer(many=True,read_only=True);tasks=EventTaskSerializer(many=True,read_only=True)
    class Meta:model=EventBooking;fields='__all__';read_only_fields=('reference','created_by')

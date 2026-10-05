from django.contrib import admin
from .models import EventBooking,EventService,EventTask,EventType,Venue
admin.site.register([Venue,EventType,EventBooking,EventService,EventTask])

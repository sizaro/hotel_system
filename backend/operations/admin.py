from django.contrib import admin
from .models import Campaign,Communication,HousekeepingTask,MaintenanceTicket,Notification,SyncOperation
admin.site.register([HousekeepingTask,MaintenanceTicket,Notification,Communication,Campaign,SyncOperation])

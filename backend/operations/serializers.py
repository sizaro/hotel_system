from rest_framework import serializers
from .models import Campaign,Communication,HousekeepingTask,MaintenanceTicket,Notification,SyncOperation
class HousekeepingTaskSerializer(serializers.ModelSerializer):
    class Meta:model=HousekeepingTask;fields='__all__'
class MaintenanceTicketSerializer(serializers.ModelSerializer):
    class Meta:model=MaintenanceTicket;fields='__all__';read_only_fields=('reported_by',)
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:model=Notification;fields='__all__';read_only_fields=('user',)
class CommunicationSerializer(serializers.ModelSerializer):
    class Meta:model=Communication;fields='__all__';read_only_fields=('created_by','status','sent_at')
class CampaignSerializer(serializers.ModelSerializer):
    class Meta:model=Campaign;fields='__all__';read_only_fields=('created_by',)
class SyncOperationSerializer(serializers.ModelSerializer):
    class Meta:model=SyncOperation;fields='__all__';read_only_fields=('user','status','result','conflict','attempts','processed_at')

from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rooms.models import Room
from users.permissions import IsHotelStaff,IsManagement
from .models import Campaign,Communication,HousekeepingTask,MaintenanceTicket,Notification,SyncOperation
from .serializers import CampaignSerializer,CommunicationSerializer,HousekeepingTaskSerializer,MaintenanceTicketSerializer,NotificationSerializer,SyncOperationSerializer
class HousekeepingViewSet(viewsets.ModelViewSet):
    queryset=HousekeepingTask.objects.select_related('room','assigned_to').all();serializer_class=HousekeepingTaskSerializer;permission_classes=[IsHotelStaff]
    @action(detail=True,methods=['post'])
    @transaction.atomic
    def complete(self,request,pk=None):
        task=self.get_object();task.status=HousekeepingTask.Status.DONE;task.completed_at=timezone.now();task.room.cleaning_status=Room.Cleaning.CLEAN;task.room.save(update_fields=['cleaning_status','updated_at']);task.save(update_fields=['status','completed_at','updated_at']);return Response(self.get_serializer(task).data)
class MaintenanceViewSet(viewsets.ModelViewSet):
    queryset=MaintenanceTicket.objects.select_related('room','reported_by','assigned_to').all();serializer_class=MaintenanceTicketSerializer;permission_classes=[IsHotelStaff]
    def perform_create(self,serializer):
        ticket=serializer.save(reported_by=self.request.user)
        if ticket.room:ticket.room.occupancy_status=Room.Occupancy.OUT_OF_SERVICE;ticket.room.save(update_fields=['occupancy_status','updated_at'])
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class=NotificationSerializer
    def get_queryset(self):return Notification.objects.filter(user=self.request.user)
    @action(detail=True,methods=['post'])
    def read(self,request,pk=None):item=self.get_object();item.is_read=True;item.save(update_fields=['is_read']);return Response(self.get_serializer(item).data)
class CommunicationViewSet(viewsets.ModelViewSet):
    queryset=Communication.objects.all();serializer_class=CommunicationSerializer;permission_classes=[IsHotelStaff]
    def perform_create(self,serializer):serializer.save(created_by=self.request.user)
class CampaignViewSet(viewsets.ModelViewSet):
    queryset=Campaign.objects.all();serializer_class=CampaignSerializer;permission_classes=[IsManagement]
    def perform_create(self,serializer):serializer.save(created_by=self.request.user)
class SyncViewSet(viewsets.ModelViewSet):
    serializer_class=SyncOperationSerializer
    def get_queryset(self):return SyncOperation.objects.filter(user=self.request.user)
    def perform_create(self,serializer):serializer.save(user=self.request.user)

import secrets
from django.db import transaction
from rest_framework import permissions,serializers,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from hotels.audit import record_audit
from users.models import User
from users.permissions import IsHotelStaff,IsManagement
from .models import EventBooking,EventService,EventTask,EventType,Venue
from .serializers import EventBookingSerializer,EventServiceSerializer,EventTaskSerializer,EventTypeSerializer,VenueSerializer
class PublicReadManagementWriteMixin:
    def get_permissions(self):return [permissions.AllowAny()] if self.action in ['list','retrieve'] else [IsManagement()]
class VenueViewSet(PublicReadManagementWriteMixin,viewsets.ModelViewSet):queryset=Venue.objects.filter(is_active=True);serializer_class=VenueSerializer
class EventTypeViewSet(PublicReadManagementWriteMixin,viewsets.ModelViewSet):queryset=EventType.objects.filter(is_active=True);serializer_class=EventTypeSerializer
class EventBookingViewSet(viewsets.ModelViewSet):
    serializer_class=EventBookingSerializer
    def get_permissions(self):return [permissions.AllowAny()] if self.request.method=='POST' else [permissions.IsAuthenticated()]
    def get_queryset(self):
        qs=EventBooking.objects.prefetch_related('services','tasks').select_related('venue','event_type','assigned_to')
        return qs.filter(email__iexact=self.request.user.email) if self.request.user.is_authenticated and self.request.user.role==User.Role.CUSTOMER else qs
    @transaction.atomic
    def perform_create(self,serializer):
        venue=serializer.validated_data['venue'];start=serializer.validated_data['start_at'];end=serializer.validated_data['end_at']
        if EventBooking.objects.select_for_update().filter(venue=venue,status__in=[EventBooking.Status.CONFIRMED,EventBooking.Status.IN_PROGRESS],start_at__lt=end,end_at__gt=start).exists():raise serializers.ValidationError('The venue is unavailable during that time.')
        serializer.save(reference=f'EVT-{secrets.token_hex(5).upper()}',created_by=self.request.user if self.request.user.is_authenticated else None)
    @action(detail=True,methods=['post'],permission_classes=[IsHotelStaff])
    @transaction.atomic
    def confirm(self,request,pk=None):
        event=self.get_object(); conflict=EventBooking.objects.select_for_update().filter(venue=event.venue,status__in=[EventBooking.Status.CONFIRMED,EventBooking.Status.IN_PROGRESS],start_at__lt=event.end_at,end_at__gt=event.start_at).exclude(pk=event.pk).exists()
        if conflict:return Response({'detail':'The venue is already committed during that time.'},status=409)
        event.status=EventBooking.Status.CONFIRMED;event.assigned_to=request.user;event.save(update_fields=['status','assigned_to','updated_at']);record_audit(actor=request.user,action='EVENT_CONFIRMED',instance=event,new={'status':event.status});return Response(self.get_serializer(event).data)
    @action(detail=True,methods=['post'],permission_classes=[IsHotelStaff])
    def cancel(self,request,pk=None):
        event=self.get_object();reason=request.data.get('reason','').strip()
        if event.status==EventBooking.Status.COMPLETED:return Response({'detail':'A completed event cannot be cancelled.'},status=409)
        event.status=EventBooking.Status.CANCELLED;event.save(update_fields=['status','updated_at']);record_audit(actor=request.user,action='EVENT_CANCELLED',instance=event,reason=reason);return Response(self.get_serializer(event).data)
class EventServiceViewSet(viewsets.ModelViewSet):
    queryset=EventService.objects.all();serializer_class=EventServiceSerializer;permission_classes=[IsHotelStaff]
    def perform_create(self,serializer):serializer.save(amount=serializer.validated_data['quantity']*serializer.validated_data['unit_price'])
class EventTaskViewSet(viewsets.ModelViewSet):queryset=EventTask.objects.all();serializer_class=EventTaskSerializer;permission_classes=[IsHotelStaff]

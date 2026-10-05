from django.db import transaction
from django.db.models import Q
from rest_framework import generics,permissions,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rooms.models import Room
from users.permissions import IsHotelStaff,IsReceptionStaff
from hotels.audit import record_audit
from .models import Booking,GuestProfile
from .serializers import BookingRequestSerializer,BookingSerializer,CounterStaySerializer,GuestProfileSerializer

class BookingRequestView(generics.CreateAPIView): permission_classes=[permissions.AllowAny]; serializer_class=BookingRequestSerializer
class MyBookingsView(generics.ListAPIView):
    serializer_class=BookingSerializer
    def get_queryset(self):
        return Booking.objects.select_related("guest","room_type","room").filter(Q(guest__user=self.request.user)|Q(guest__email__iexact=self.request.user.email)).distinct()
class GuestProfileViewSet(viewsets.ModelViewSet):
    serializer_class=GuestProfileSerializer;permission_classes=[IsReceptionStaff];queryset=GuestProfile.objects.all().order_by('first_name','last_name')
    def get_queryset(self):
        qs=super().get_queryset();search=self.request.query_params.get('search','').strip()
        return qs.filter(Q(first_name__icontains=search)|Q(last_name__icontains=search)|Q(email__icontains=search)|Q(phone__icontains=search)) if search else qs
class BookingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class=BookingSerializer;permission_classes=[IsHotelStaff];queryset=Booking.objects.select_related('guest','room_type','room','hotel').all()
    @action(detail=False,methods=['post'],permission_classes=[IsReceptionStaff])
    @transaction.atomic
    def counter(self,request):
        from django.utils import timezone
        from finance.services import create_stay_with_folio
        serializer=CounterStaySerializer(data=request.data);serializer.is_valid(raise_exception=True);data=serializer.validated_data;guest_id=data.pop('guest_id',None);room=data.pop('room');check_in_now=data.pop('check_in_now')
        guest_fields={key:data.pop(key,'') for key in ('first_name','last_name','phone','email','nationality','country_of_residence','address','identity_type','identity_number','identity_document_url')}
        if guest_id:
            try:guest=GuestProfile.objects.get(id=guest_id)
            except GuestProfile.DoesNotExist:return Response({'detail':'The selected guest no longer exists.'},status=404)
        else:
            email=guest_fields.pop('email').lower();guest,created=GuestProfile.objects.get_or_create(email=email,defaults=guest_fields)
            if not created:
                for key,value in guest_fields.items():
                    if value:setattr(guest,key,value)
                guest.save()
        stay=create_stay_with_folio(actor=request.user,hotel=room.hotel,guest=guest,room=room,**data)
        if check_in_now:
            stay.status=stay.Status.CHECKED_IN;stay.checked_in_at=timezone.now();stay.room.occupancy_status=stay.room.Occupancy.OCCUPIED;stay.room.save(update_fields=['occupancy_status','updated_at']);stay.save(update_fields=['status','checked_in_at','updated_at'])
        return Response({'stay_id':stay.id,'folio_id':stay.folio.id,'guest_id':guest.id},status=201)
    @action(detail=True,methods=['post'])
    @transaction.atomic
    def confirm(self,request,pk=None):
        from finance.services import create_stay_with_folio
        booking=self.get_object();room_id=request.data.get('room_id')
        try:room=Room.objects.get(id=room_id,room_type=booking.room_type,is_active=True)
        except Room.DoesNotExist:return Response({'detail':'Select an active room of the requested type.'},status=400)
        stay=create_stay_with_folio(actor=request.user,hotel=booking.hotel,guest=booking.guest,room=room,arrival_date=booking.arrival_date,departure_date=booking.departure_date,rate=booking.nightly_rate,booking=booking,occupants=booking.adults+booking.children,notes=booking.special_requests)
        booking.status=Booking.Status.CONFIRMED;booking.room=room;booking.save(update_fields=['status','room','updated_at']);return Response({'booking':self.get_serializer(booking).data,'stay_id':stay.id})
    @action(detail=True,methods=['post'])
    @transaction.atomic
    def cancel(self,request,pk=None):
        booking=self.get_object();reason=request.data.get('reason','').strip()
        if booking.status==Booking.Status.CHECKED_IN:return Response({'detail':'A checked-in stay must be checked out through reception.'},status=409)
        previous={'status':booking.status}
        if hasattr(booking,'stay'):
            stay=booking.stay
            if stay.status==stay.Status.CHECKED_IN:return Response({'detail':'A checked-in stay cannot be cancelled.'},status=409)
            stay.status=stay.Status.CANCELLED;stay.save(update_fields=['status','updated_at'])
            if hasattr(stay,'folio'):
                stay.folio.status=stay.folio.Status.VOID;stay.folio.save(update_fields=['status','updated_at']);stay.folio.charges.update(is_void=True,void_reason=reason or 'Booking cancelled')
        booking.status=Booking.Status.CANCELLED;booking.save(update_fields=['status','updated_at']);record_audit(actor=request.user,action='BOOKING_CANCELLED',instance=booking,reason=reason,previous=previous,new={'status':booking.status});return Response(self.get_serializer(booking).data)

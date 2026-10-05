from django.db.models import Count, Q
from rest_framework import generics,permissions,viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Room, RoomType
from .serializers import RoomSerializer, RoomTypeSerializer

class PublicRoomTypesView(generics.ListAPIView):
    permission_classes=[permissions.AllowAny]; serializer_class=RoomTypeSerializer
    def get_queryset(self):
        return RoomType.objects.filter(is_active=True,hotel__is_active=True).prefetch_related("amenities").annotate(available_rooms=Count("rooms",filter=Q(rooms__is_active=True,rooms__occupancy_status=Room.Occupancy.AVAILABLE,rooms__cleaning_status=Room.Cleaning.CLEAN)))

class RoomViewSet(viewsets.ModelViewSet):
    serializer_class=RoomSerializer
    def get_queryset(self): return Room.objects.select_related("hotel","room_type").all()
    def get_permissions(self): return [permissions.IsAuthenticated()] if self.action in ("list","retrieve") else [permissions.IsAdminUser()]
class AvailabilityView(APIView):
    permission_classes=[permissions.AllowAny]
    def get(self,request):
        from finance.models import Stay
        arrival=request.query_params.get('arrival');departure=request.query_params.get('departure');guests=int(request.query_params.get('guests',1))
        if not arrival or not departure:return Response({'detail':'arrival and departure are required.'},status=400)
        blocked=Stay.objects.filter(status__in=[Stay.Status.RESERVED,Stay.Status.CHECKED_IN],arrival_date__lt=departure,departure_date__gt=arrival).values_list('room_id',flat=True)
        rooms=Room.objects.filter(is_active=True,room_type__capacity__gte=guests,room_type__is_active=True).exclude(id__in=blocked)
        return Response(list(rooms.values('id','number','room_type_id','room_type__name','room_type__base_rate','room_type__capacity')))

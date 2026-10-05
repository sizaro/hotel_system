import secrets
from django.db import transaction
from rest_framework import serializers
from hotels.models import Hotel
from rooms.models import Room,RoomType
from .models import Booking, GuestProfile

class BookingSerializer(serializers.ModelSerializer):
    guest_name=serializers.CharField(source="guest.__str__",read_only=True); room_type_name=serializers.CharField(source="room_type.name",read_only=True)
    class Meta: model=Booking; fields="__all__"; read_only_fields=("id","reference","hotel","nightly_rate","status","created_by","created_at","updated_at")

class GuestProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=GuestProfile;fields='__all__';read_only_fields=('id','user','created_at','updated_at')

class CounterStaySerializer(serializers.Serializer):
    guest_id=serializers.UUIDField(required=False)
    first_name=serializers.CharField(max_length=80,required=False);last_name=serializers.CharField(max_length=80,required=False)
    phone=serializers.CharField(max_length=32,required=False,allow_blank=True);email=serializers.EmailField(required=False)
    nationality=serializers.CharField(max_length=80,required=False,allow_blank=True);country_of_residence=serializers.CharField(max_length=80,required=False,allow_blank=True)
    address=serializers.CharField(required=False,allow_blank=True);identity_type=serializers.CharField(max_length=40,required=False,allow_blank=True)
    identity_number=serializers.CharField(max_length=80,required=False,allow_blank=True);identity_document_url=serializers.URLField(required=False,allow_blank=True)
    room_id=serializers.UUIDField();arrival_date=serializers.DateField();departure_date=serializers.DateField();occupants=serializers.IntegerField(min_value=1,default=1)
    rate=serializers.DecimalField(max_digits=12,decimal_places=2,min_value=0);vehicle_registration=serializers.CharField(max_length=40,required=False,allow_blank=True)
    vehicle_colour=serializers.CharField(max_length=40,required=False,allow_blank=True);purpose_of_visit=serializers.CharField(max_length=160,required=False,allow_blank=True)
    coming_from=serializers.CharField(max_length=160,required=False,allow_blank=True);going_to=serializers.CharField(max_length=160,required=False,allow_blank=True)
    account_payer=serializers.CharField(max_length=160,required=False,allow_blank=True);notes=serializers.CharField(required=False,allow_blank=True);check_in_now=serializers.BooleanField(default=True)
    def validate(self,data):
        if data['departure_date']<=data['arrival_date']:raise serializers.ValidationError({'departure_date':'Departure must be after arrival.'})
        try:data['room']=Room.objects.get(id=data.pop('room_id'),is_active=True)
        except Room.DoesNotExist:raise serializers.ValidationError({'room_id':'Select an active room.'})
        if not data.get('guest_id') and not all(data.get(key) for key in ('first_name','last_name','email')):raise serializers.ValidationError('Choose an existing guest or provide the guest name and email.')
        return data

class BookingRequestSerializer(serializers.Serializer):
    room_type_id=serializers.UUIDField(); arrival_date=serializers.DateField(); departure_date=serializers.DateField(); adults=serializers.IntegerField(min_value=1,max_value=20); children=serializers.IntegerField(min_value=0,max_value=20,default=0)
    first_name=serializers.CharField(max_length=80); last_name=serializers.CharField(max_length=80); email=serializers.EmailField(); phone=serializers.CharField(max_length=32); special_requests=serializers.CharField(required=False,allow_blank=True)
    def validate(self,data):
        if data["departure_date"]<=data["arrival_date"]: raise serializers.ValidationError({"departure_date":"Departure must be after arrival."})
        try: data["room_type"]=RoomType.objects.get(id=data.pop("room_type_id"),is_active=True,hotel__is_active=True)
        except RoomType.DoesNotExist: raise serializers.ValidationError({"room_type_id":"This room type is unavailable."})
        if data["adults"]+data["children"]>data["room_type"].capacity: raise serializers.ValidationError("The selected room type cannot accommodate this party.")
        return data
    @transaction.atomic
    def create(self,data):
        request=self.context["request"]; room_type=data.pop("room_type"); hotel=Hotel.objects.get(is_active=True)
        guest,created=GuestProfile.objects.get_or_create(email=data["email"].lower(),defaults={"first_name":data["first_name"],"last_name":data["last_name"],"phone":data["phone"],"user":request.user if request.user.is_authenticated else None})
        if not created:
            guest.first_name=data["first_name"]; guest.last_name=data["last_name"]; guest.phone=data["phone"]
            if request.user.is_authenticated and guest.user_id is None: guest.user=request.user
            guest.save(update_fields=["first_name","last_name","phone","user","updated_at"])
        return Booking.objects.create(reference=f"BK-{secrets.token_hex(4).upper()}",hotel=hotel,guest=guest,room_type=room_type,nightly_rate=room_type.base_rate,arrival_date=data["arrival_date"],departure_date=data["departure_date"],adults=data["adults"],children=data["children"],special_requests=data.get("special_requests",""),created_by=request.user if request.user.is_authenticated else None)

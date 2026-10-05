import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from hotels.models import Hotel
from rooms.models import Room, RoomType

class GuestProfile(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="guest_profile")
    first_name=models.CharField(max_length=80); last_name=models.CharField(max_length=80); phone=models.CharField(max_length=32); email=models.EmailField(unique=True); nationality=models.CharField(max_length=80,blank=True)
    country_of_residence=models.CharField(max_length=80,blank=True); address=models.TextField(blank=True); preferences=models.JSONField(default=dict,blank=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    identity_type=models.CharField(max_length=40,blank=True); identity_number=models.CharField(max_length=80,blank=True); identity_document_url=models.URLField(blank=True); home_address=models.TextField(blank=True); workplace=models.CharField(max_length=160,blank=True); occupation=models.CharField(max_length=120,blank=True); designation=models.CharField(max_length=120,blank=True); signature_url=models.URLField(blank=True)
    def __str__(self): return f"{self.first_name} {self.last_name}"

class Booking(models.Model):
    class Status(models.TextChoices): REQUESTED="REQUESTED","Requested"; CONFIRMED="CONFIRMED","Confirmed"; CHECKED_IN="CHECKED_IN","Checked in"; CHECKED_OUT="CHECKED_OUT","Checked out"; CANCELLED="CANCELLED","Cancelled"; NO_SHOW="NO_SHOW","No show"
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); reference=models.CharField(max_length=24,unique=True,db_index=True); hotel=models.ForeignKey(Hotel,on_delete=models.PROTECT,related_name="bookings")
    guest=models.ForeignKey(GuestProfile,on_delete=models.PROTECT,related_name="bookings"); room_type=models.ForeignKey(RoomType,on_delete=models.PROTECT,related_name="bookings"); room=models.ForeignKey(Room,on_delete=models.PROTECT,null=True,blank=True,related_name="bookings")
    arrival_date=models.DateField(db_index=True); departure_date=models.DateField(db_index=True); adults=models.PositiveSmallIntegerField(default=1); children=models.PositiveSmallIntegerField(default=0)
    nightly_rate=models.DecimalField(max_digits=12,decimal_places=2); status=models.CharField(max_length=20,choices=Status.choices,default=Status.REQUESTED,db_index=True); special_requests=models.TextField(blank=True)
    source=models.CharField(max_length=40,default="DIRECT"); idempotency_key=models.UUIDField(default=uuid.uuid4,unique=True); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_bookings")
    created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=("-created_at",); indexes=[models.Index(fields=["hotel","arrival_date","departure_date","status"])]
    def clean(self):
        if self.departure_date<=self.arrival_date: raise ValidationError("Departure must be after arrival.")
    def __str__(self): return self.reference

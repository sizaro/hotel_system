import uuid
from django.db import models
from hotels.models import Hotel

class Amenity(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); name=models.CharField(max_length=80,unique=True); icon=models.CharField(max_length=40,blank=True)
    def __str__(self): return self.name

class RoomType(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE,related_name="room_types")
    name=models.CharField(max_length=100); slug=models.SlugField(max_length=120); description=models.TextField(blank=True); capacity=models.PositiveSmallIntegerField(default=2)
    base_rate=models.DecimalField(max_digits=12,decimal_places=2); size_sqm=models.DecimalField(max_digits=7,decimal_places=2,null=True,blank=True); bed_description=models.CharField(max_length=120,blank=True)
    image_url=models.URLField(blank=True); amenities=models.ManyToManyField(Amenity,blank=True,related_name="room_types"); is_active=models.BooleanField(default=True); display_order=models.PositiveIntegerField(default=0)
    class Meta: ordering=("display_order","base_rate"); constraints=[models.UniqueConstraint(fields=["hotel","slug"],name="unique_hotel_room_type")]
    def __str__(self): return self.name

class Room(models.Model):
    class Occupancy(models.TextChoices): AVAILABLE="AVAILABLE","Available"; RESERVED="RESERVED","Reserved"; OCCUPIED="OCCUPIED","Occupied"; OUT_OF_SERVICE="OUT_OF_SERVICE","Out of service"
    class Cleaning(models.TextChoices): CLEAN="CLEAN","Clean"; DIRTY="DIRTY","Needs cleaning"; IN_PROGRESS="IN_PROGRESS","Cleaning"; INSPECT="INSPECT","Awaiting inspection"
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE,related_name="rooms"); room_type=models.ForeignKey(RoomType,on_delete=models.PROTECT,related_name="rooms")
    number=models.CharField(max_length=20); floor=models.CharField(max_length=30,blank=True); occupancy_status=models.CharField(max_length=20,choices=Occupancy.choices,default=Occupancy.AVAILABLE,db_index=True)
    cleaning_status=models.CharField(max_length=20,choices=Cleaning.choices,default=Cleaning.CLEAN,db_index=True); notes=models.TextField(blank=True); is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=("number",); constraints=[models.UniqueConstraint(fields=["hotel","number"],name="unique_hotel_room_number")]
    def __str__(self): return f"{self.number} · {self.room_type.name}"

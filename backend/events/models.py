import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from finance.models import Folio
from hotels.models import Hotel

class Venue(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE,related_name='venues'); name=models.CharField(max_length=120); capacity=models.PositiveIntegerField(); base_rate=models.DecimalField(max_digits=12,decimal_places=2,default=0); description=models.TextField(blank=True); image_url=models.URLField(blank=True); is_active=models.BooleanField(default=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['hotel','name'],name='unique_hotel_venue')]
class EventType(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE,related_name='event_types'); name=models.CharField(max_length=100); is_active=models.BooleanField(default=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['hotel','name'],name='unique_hotel_event_type')]
class EventBooking(models.Model):
    class Status(models.TextChoices): REQUESTED='REQUESTED','Requested'; QUOTED='QUOTED','Quoted'; CONFIRMED='CONFIRMED','Confirmed'; IN_PROGRESS='IN_PROGRESS','In progress'; COMPLETED='COMPLETED','Completed'; CANCELLED='CANCELLED','Cancelled'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); hotel=models.ForeignKey(Hotel,on_delete=models.PROTECT,related_name='event_bookings'); reference=models.CharField(max_length=28,unique=True); event_type=models.ForeignKey(EventType,on_delete=models.PROTECT,related_name='bookings'); venue=models.ForeignKey(Venue,on_delete=models.PROTECT,related_name='bookings'); folio=models.OneToOneField(Folio,on_delete=models.PROTECT,null=True,blank=True,related_name='event_booking'); customer_type=models.CharField(max_length=30,default='INDIVIDUAL'); customer_name=models.CharField(max_length=180); organization_name=models.CharField(max_length=180,blank=True); contact_name=models.CharField(max_length=140); email=models.EmailField(); phone=models.CharField(max_length=40); start_at=models.DateTimeField(); end_at=models.DateTimeField(); attendance=models.PositiveIntegerField(); requirements=models.JSONField(default=dict,blank=True); quoted_amount=models.DecimalField(max_digits=12,decimal_places=2,default=0); status=models.CharField(max_length=16,choices=Status.choices,default=Status.REQUESTED,db_index=True); assigned_to=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='assigned_events'); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='created_events'); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: indexes=[models.Index(fields=['venue','start_at','end_at','status'])]
    def clean(self):
        if self.end_at<=self.start_at: raise ValidationError('Event end must be after its start.')
        if self.attendance>self.venue.capacity: raise ValidationError('Attendance exceeds venue capacity.')
class EventService(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); event=models.ForeignKey(EventBooking,on_delete=models.CASCADE,related_name='services'); name=models.CharField(max_length=140); quantity=models.DecimalField(max_digits=10,decimal_places=2,default=1); unit_price=models.DecimalField(max_digits=12,decimal_places=2); amount=models.DecimalField(max_digits=12,decimal_places=2); notes=models.TextField(blank=True)
class EventTask(models.Model):
    class Status(models.TextChoices): TODO='TODO','To do'; IN_PROGRESS='IN_PROGRESS','In progress'; DONE='DONE','Done'; BLOCKED='BLOCKED','Blocked'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); event=models.ForeignKey(EventBooking,on_delete=models.CASCADE,related_name='tasks'); title=models.CharField(max_length=180); assigned_to=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='event_tasks'); due_at=models.DateTimeField(null=True,blank=True); status=models.CharField(max_length=16,choices=Status.choices,default=Status.TODO); notes=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True)

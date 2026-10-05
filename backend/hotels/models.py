import uuid
from django.conf import settings
from django.db import models
from django.db.models import Q

class Hotel(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name=models.CharField(max_length=160); short_name=models.CharField(max_length=60,blank=True); legal_name=models.CharField(max_length=180,blank=True)
    tagline=models.CharField(max_length=220,blank=True); description=models.TextField(blank=True); logo_url=models.URLField(blank=True); hero_image_url=models.URLField(blank=True)
    phone=models.CharField(max_length=40,blank=True); secondary_phone=models.CharField(max_length=40,blank=True); email=models.EmailField(blank=True); website=models.URLField(blank=True)
    address=models.TextField(blank=True); city=models.CharField(max_length=100,blank=True); country=models.CharField(max_length=100,default="Uganda")
    latitude=models.DecimalField(max_digits=10,decimal_places=7,null=True,blank=True); longitude=models.DecimalField(max_digits=10,decimal_places=7,null=True,blank=True)
    currency=models.CharField(max_length=8,default="UGX"); timezone=models.CharField(max_length=64,default="Africa/Kampala")
    check_in_time=models.TimeField(default="14:00"); check_out_time=models.TimeField(default="11:00")
    tax_rate=models.DecimalField(max_digits=5,decimal_places=2,default=0); service_charge_rate=models.DecimalField(max_digits=5,decimal_places=2,default=0)
    social_links=models.JSONField(default=dict,blank=True); policies=models.JSONField(default=dict,blank=True); brand_colors=models.JSONField(default=dict,blank=True)
    is_active=models.BooleanField(default=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=["is_active"],condition=Q(is_active=True),name="one_active_hotel")]
    def __str__(self): return self.name

class HotelService(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE,related_name="services")
    name=models.CharField(max_length=120); slug=models.SlugField(max_length=140); short_description=models.CharField(max_length=240); description=models.TextField(blank=True)
    icon=models.CharField(max_length=40,blank=True); image_url=models.URLField(blank=True); starting_price=models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    is_featured=models.BooleanField(default=False); is_active=models.BooleanField(default=True); display_order=models.PositiveIntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=("display_order","name"); constraints=[models.UniqueConstraint(fields=["hotel","slug"],name="unique_hotel_service_slug")]
    def __str__(self): return self.name

class AuditLog(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True)
    action=models.CharField(max_length=80); entity_type=models.CharField(max_length=80); entity_id=models.CharField(max_length=80); reason=models.TextField(blank=True)
    previous_state=models.JSONField(null=True,blank=True); new_state=models.JSONField(null=True,blank=True); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=("-created_at",); indexes=[models.Index(fields=["entity_type","entity_id"])]

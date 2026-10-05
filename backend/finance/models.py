import uuid
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from bookings.models import Booking,GuestProfile
from hotels.models import Hotel
from rooms.models import Room

class Stay(models.Model):
    class Status(models.TextChoices): RESERVED='RESERVED','Reserved'; CHECKED_IN='CHECKED_IN','Checked in'; CHECKED_OUT='CHECKED_OUT','Checked out'; CANCELLED='CANCELLED','Cancelled'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); hotel=models.ForeignKey(Hotel,on_delete=models.PROTECT,related_name='stays'); booking=models.OneToOneField(Booking,on_delete=models.PROTECT,null=True,blank=True,related_name='stay'); guest=models.ForeignKey(GuestProfile,on_delete=models.PROTECT,related_name='stays'); room=models.ForeignKey(Room,on_delete=models.PROTECT,related_name='stays')
    arrival_date=models.DateField(); departure_date=models.DateField(); occupants=models.PositiveSmallIntegerField(default=1); rate=models.DecimalField(max_digits=12,decimal_places=2); status=models.CharField(max_length=16,choices=Status.choices,default=Status.RESERVED,db_index=True)
    vehicle_registration=models.CharField(max_length=40,blank=True); vehicle_colour=models.CharField(max_length=40,blank=True); purpose_of_visit=models.CharField(max_length=160,blank=True); coming_from=models.CharField(max_length=160,blank=True); going_to=models.CharField(max_length=160,blank=True); account_payer=models.CharField(max_length=160,blank=True); receptionist=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='handled_stays'); checked_in_at=models.DateTimeField(null=True,blank=True); checked_out_at=models.DateTimeField(null=True,blank=True); notes=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: indexes=[models.Index(fields=['hotel','room','arrival_date','departure_date','status'])]
    def clean(self):
        if self.departure_date<=self.arrival_date: raise ValidationError('Departure must be after arrival.')
    def __str__(self): return f'{self.guest} · {self.room}'

class Folio(models.Model):
    class Status(models.TextChoices): OPEN='OPEN','Open'; SETTLED='SETTLED','Settled'; CLOSED='CLOSED','Closed'; VOID='VOID','Void'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); hotel=models.ForeignKey(Hotel,on_delete=models.PROTECT,related_name='folios'); stay=models.OneToOneField(Stay,on_delete=models.PROTECT,null=True,blank=True,related_name='folio'); guest=models.ForeignKey(GuestProfile,on_delete=models.PROTECT,related_name='folios'); reference=models.CharField(max_length=24,unique=True); status=models.CharField(max_length=12,choices=Status.choices,default=Status.OPEN,db_index=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    @property
    def total_charges(self): return sum((x.amount for x in self.charges.filter(is_void=False)),Decimal('0'))
    @property
    def total_payments(self): return sum((x.amount for x in self.payments.filter(status='CONFIRMED')),Decimal('0'))
    @property
    def balance(self): return self.total_charges-self.total_payments

class FolioCharge(models.Model):
    class Kind(models.TextChoices): ROOM='ROOM','Accommodation'; OUTLET='OUTLET','Outlet'; EVENT='EVENT','Event'; SERVICE='SERVICE','Service'; ADJUSTMENT='ADJUSTMENT','Adjustment'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); folio=models.ForeignKey(Folio,on_delete=models.PROTECT,related_name='charges'); kind=models.CharField(max_length=16,choices=Kind.choices); description=models.CharField(max_length=240); quantity=models.DecimalField(max_digits=10,decimal_places=2,default=1); unit_price=models.DecimalField(max_digits=12,decimal_places=2); amount=models.DecimalField(max_digits=12,decimal_places=2); source_type=models.CharField(max_length=60,blank=True); source_id=models.CharField(max_length=64,blank=True); is_void=models.BooleanField(default=False); void_reason=models.TextField(blank=True); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,related_name='created_folio_charges'); created_at=models.DateTimeField(auto_now_add=True)

class Payment(models.Model):
    class Method(models.TextChoices): CASH='CASH','Cash'; CARD='CARD','Card'; MOBILE_MONEY='MOBILE_MONEY','Mobile money'; BANK='BANK','Bank'; CREDIT='CREDIT','Credit'; OTHER='OTHER','Other'
    class Status(models.TextChoices): PENDING='PENDING','Pending'; CONFIRMED='CONFIRMED','Confirmed'; FAILED='FAILED','Failed'; REVERSED='REVERSED','Reversed'; REFUNDED='REFUNDED','Refunded'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); folio=models.ForeignKey(Folio,on_delete=models.PROTECT,related_name='payments'); receipt_number=models.CharField(max_length=30,unique=True); amount=models.DecimalField(max_digits=12,decimal_places=2); method=models.CharField(max_length=20,choices=Method.choices); status=models.CharField(max_length=16,choices=Status.choices,default=Status.PENDING,db_index=True); provider_reference=models.CharField(max_length=120,blank=True); proof_url=models.URLField(blank=True); notes=models.TextField(blank=True); received_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='received_hotel_payments'); received_at=models.DateTimeField(); reversed_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='reversed_hotel_payments'); reversed_at=models.DateTimeField(null=True,blank=True); reversal_reason=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True)
    def clean(self):
        if self.amount<=0: raise ValidationError('Payment amount must be greater than zero.')

class Invoice(models.Model):
    class Status(models.TextChoices): DRAFT='DRAFT','Draft'; ISSUED='ISSUED','Issued'; PARTIAL='PARTIAL','Partially paid'; PAID='PAID','Paid'; VOID='VOID','Void'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); folio=models.ForeignKey(Folio,on_delete=models.PROTECT,related_name='invoices'); number=models.CharField(max_length=30,unique=True); status=models.CharField(max_length=12,choices=Status.choices,default=Status.DRAFT); total=models.DecimalField(max_digits=12,decimal_places=2); due_date=models.DateField(null=True,blank=True); issued_at=models.DateTimeField(null=True,blank=True); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='created_hotel_invoices'); created_at=models.DateTimeField(auto_now_add=True)

class Refund(models.Model):
    class Status(models.TextChoices): REQUESTED='REQUESTED','Requested'; APPROVED='APPROVED','Approved'; PAID='PAID','Paid'; REJECTED='REJECTED','Rejected'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); payment=models.ForeignKey(Payment,on_delete=models.PROTECT,related_name='refunds'); amount=models.DecimalField(max_digits=12,decimal_places=2); reason=models.TextField(); status=models.CharField(max_length=16,choices=Status.choices,default=Status.REQUESTED); requested_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='requested_refunds'); approved_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='approved_refunds'); paid_at=models.DateTimeField(null=True,blank=True); proof_url=models.URLField(blank=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    def clean(self):
        if self.amount<=0 or self.amount>self.payment.amount: raise ValidationError('Refund must be greater than zero and cannot exceed the original payment.')

class InstallmentSchedule(models.Model):
    class Status(models.TextChoices): PENDING='PENDING','Pending'; PAID='PAID','Paid'; OVERDUE='OVERDUE','Overdue'; WAIVED='WAIVED','Waived'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); invoice=models.ForeignKey(Invoice,on_delete=models.PROTECT,related_name='installments'); due_date=models.DateField(); amount=models.DecimalField(max_digits=12,decimal_places=2); status=models.CharField(max_length=12,choices=Status.choices,default=Status.PENDING); notes=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True)

class Expense(models.Model):
    class Status(models.TextChoices): DRAFT='DRAFT','Draft'; PENDING='PENDING','Pending approval'; APPROVED='APPROVED','Approved'; PAID='PAID','Paid'; REJECTED='REJECTED','Rejected'; CANCELLED='CANCELLED','Cancelled'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); hotel=models.ForeignKey(Hotel,on_delete=models.PROTECT,related_name='expenses'); category=models.CharField(max_length=100); payee=models.CharField(max_length=180); amount=models.DecimalField(max_digits=12,decimal_places=2); payment_method=models.CharField(max_length=30,blank=True); reference=models.CharField(max_length=100,blank=True); expense_date=models.DateField(); description=models.TextField(blank=True); proof_url=models.URLField(blank=True); status=models.CharField(max_length=16,choices=Status.choices,default=Status.DRAFT); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='created_hotel_expenses'); approved_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='approved_hotel_expenses'); decision_reason=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)

class Quotation(models.Model):
    class Status(models.TextChoices): DRAFT='DRAFT','Draft'; SENT='SENT','Sent'; ACCEPTED='ACCEPTED','Accepted'; REJECTED='REJECTED','Rejected'; EXPIRED='EXPIRED','Expired'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); hotel=models.ForeignKey(Hotel,on_delete=models.PROTECT,related_name='quotations'); guest=models.ForeignKey(GuestProfile,on_delete=models.PROTECT,related_name='quotations'); number=models.CharField(max_length=30,unique=True); description=models.TextField(); total=models.DecimalField(max_digits=12,decimal_places=2); valid_until=models.DateField(); status=models.CharField(max_length=12,choices=Status.choices,default=Status.DRAFT); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='created_quotations'); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)

import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from finance.models import Folio
from hotels.models import Hotel
from rooms.models import Room

class Outlet(models.Model):
    class Kind(models.TextChoices): BAR='BAR','Bar'; RESTAURANT='RESTAURANT','Restaurant'; CAFE='CAFE','Cafe'; ROOM_SERVICE='ROOM_SERVICE','Room service'; OTHER='OTHER','Other'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE,related_name='outlets'); name=models.CharField(max_length=100); kind=models.CharField(max_length=20,choices=Kind.choices); is_active=models.BooleanField(default=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['hotel','name'],name='unique_hotel_outlet')]
    def __str__(self): return self.name
class ProductCategory(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE,related_name='product_categories'); name=models.CharField(max_length=100); is_active=models.BooleanField(default=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['hotel','name'],name='unique_hotel_product_category')]
class Supplier(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE,related_name='suppliers'); name=models.CharField(max_length=160); phone=models.CharField(max_length=40,blank=True); email=models.EmailField(blank=True); address=models.TextField(blank=True); is_active=models.BooleanField(default=True); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['hotel','name'],name='unique_hotel_supplier')]
class Product(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE,related_name='products'); category=models.ForeignKey(ProductCategory,on_delete=models.PROTECT,related_name='products'); name=models.CharField(max_length=140); sku=models.CharField(max_length=60); unit=models.CharField(max_length=30); purchase_cost=models.DecimalField(max_digits=12,decimal_places=2,default=0); selling_price=models.DecimalField(max_digits=12,decimal_places=2,default=0); reorder_level=models.DecimalField(max_digits=12,decimal_places=2,default=0); is_active=models.BooleanField(default=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['hotel','sku'],name='unique_hotel_product_sku')]
class StockLocation(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE,related_name='stock_locations'); outlet=models.OneToOneField(Outlet,on_delete=models.SET_NULL,null=True,blank=True,related_name='stock_location'); name=models.CharField(max_length=100); is_active=models.BooleanField(default=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['hotel','name'],name='unique_hotel_stock_location')]
class StockMovement(models.Model):
    class Kind(models.TextChoices): OPENING='OPENING','Opening'; RECEIVED='RECEIVED','Received'; TRANSFER_IN='TRANSFER_IN','Transfer in'; TRANSFER_OUT='TRANSFER_OUT','Transfer out'; SALE='SALE','Sale'; CONSUMPTION='CONSUMPTION','Consumption'; BREAKAGE='BREAKAGE','Breakage'; EXPIRY='EXPIRY','Expiry'; DEFECT='DEFECT','Factory defect'; WASTAGE='WASTAGE','Wastage'; RETURN='RETURN','Return'; ADJUSTMENT='ADJUSTMENT','Adjustment'; COUNT='COUNT','Physical count'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); product=models.ForeignKey(Product,on_delete=models.PROTECT,related_name='movements'); location=models.ForeignKey(StockLocation,on_delete=models.PROTECT,related_name='movements'); kind=models.CharField(max_length=20,choices=Kind.choices); quantity=models.DecimalField(max_digits=12,decimal_places=2); unit_cost=models.DecimalField(max_digits=12,decimal_places=2,default=0); batch_number=models.CharField(max_length=80,blank=True); expiry_date=models.DateField(null=True,blank=True); reference=models.CharField(max_length=100,blank=True); reason=models.TextField(blank=True); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='stock_movements'); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: indexes=[models.Index(fields=['product','location','created_at'])]
    def clean(self):
        if self.quantity<=0: raise ValidationError('Movement quantity must be positive.')
class OutletSale(models.Model):
    class Status(models.TextChoices): DRAFT='DRAFT','Draft'; CONFIRMED='CONFIRMED','Confirmed'; VOID='VOID','Void'
    class Settlement(models.TextChoices): CASH='CASH','Cash'; CREDIT='CREDIT','Credit'; ROOM='ROOM','Room charge'; ELECTRONIC='ELECTRONIC','Electronic'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); outlet=models.ForeignKey(Outlet,on_delete=models.PROTECT,related_name='sales'); receipt_number=models.CharField(max_length=32,unique=True); folio=models.ForeignKey(Folio,on_delete=models.PROTECT,null=True,blank=True,related_name='outlet_sales'); room=models.ForeignKey(Room,on_delete=models.PROTECT,null=True,blank=True,related_name='outlet_sales'); settlement=models.CharField(max_length=16,choices=Settlement.choices); status=models.CharField(max_length=12,choices=Status.choices,default=Status.DRAFT); total=models.DecimalField(max_digits=12,decimal_places=2,default=0); remarks=models.TextField(blank=True); sold_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='outlet_sales'); sold_at=models.DateTimeField(); void_reason=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True)
class SaleLine(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); sale=models.ForeignKey(OutletSale,on_delete=models.PROTECT,related_name='lines'); product=models.ForeignKey(Product,on_delete=models.PROTECT,related_name='sale_lines'); description=models.CharField(max_length=160); quantity=models.DecimalField(max_digits=12,decimal_places=2); unit_price=models.DecimalField(max_digits=12,decimal_places=2); amount=models.DecimalField(max_digits=12,decimal_places=2)
class CashReconciliation(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); outlet=models.ForeignKey(Outlet,on_delete=models.PROTECT,related_name='reconciliations'); business_date=models.DateField(); expected_cash=models.DecimalField(max_digits=12,decimal_places=2); actual_cash=models.DecimalField(max_digits=12,decimal_places=2); credit_total=models.DecimalField(max_digits=12,decimal_places=2,default=0); room_charge_total=models.DecimalField(max_digits=12,decimal_places=2,default=0); notes=models.TextField(blank=True); prepared_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='prepared_reconciliations'); approved_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='approved_reconciliations'); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['outlet','business_date'],name='unique_outlet_business_date')]

class PurchaseReceipt(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); hotel=models.ForeignKey(Hotel,on_delete=models.PROTECT,related_name='purchase_receipts'); supplier=models.ForeignKey(Supplier,on_delete=models.PROTECT,related_name='receipts'); location=models.ForeignKey(StockLocation,on_delete=models.PROTECT,related_name='purchase_receipts'); reference=models.CharField(max_length=100); invoice_url=models.URLField(blank=True); received_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='received_purchases'); received_at=models.DateTimeField(); notes=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['hotel','reference'],name='unique_hotel_purchase_reference')]
class PurchaseReceiptLine(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); receipt=models.ForeignKey(PurchaseReceipt,on_delete=models.PROTECT,related_name='lines'); product=models.ForeignKey(Product,on_delete=models.PROTECT,related_name='purchase_lines'); quantity=models.DecimalField(max_digits=12,decimal_places=2); unit_cost=models.DecimalField(max_digits=12,decimal_places=2); batch_number=models.CharField(max_length=80,blank=True); expiry_date=models.DateField(null=True,blank=True)
class StockCount(models.Model):
    class Status(models.TextChoices): OPEN='OPEN','Open'; SUBMITTED='SUBMITTED','Submitted'; APPROVED='APPROVED','Approved'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); location=models.ForeignKey(StockLocation,on_delete=models.PROTECT,related_name='stock_counts'); business_date=models.DateField(); status=models.CharField(max_length=12,choices=Status.choices,default=Status.OPEN); counted_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='stock_counts'); approved_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='approved_stock_counts'); created_at=models.DateTimeField(auto_now_add=True)
class StockCountLine(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); stock_count=models.ForeignKey(StockCount,on_delete=models.PROTECT,related_name='lines'); product=models.ForeignKey(Product,on_delete=models.PROTECT,related_name='count_lines'); expected_quantity=models.DecimalField(max_digits=12,decimal_places=2); counted_quantity=models.DecimalField(max_digits=12,decimal_places=2); reason=models.TextField(blank=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['stock_count','product'],name='unique_count_product')]

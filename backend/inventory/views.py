import secrets
from decimal import Decimal
from django.db import transaction
from django.db.models import Case,DecimalField,F,Sum,Value,When
from rest_framework import serializers,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from finance.models import FolioCharge
from users.permissions import IsHotelStaff,IsManagement
from hotels.audit import record_audit
from .models import CashReconciliation,Outlet,OutletSale,Product,ProductCategory,PurchaseReceipt,PurchaseReceiptLine,SaleLine,StockCount,StockCountLine,StockLocation,StockMovement,Supplier
from .serializers import CashReconciliationSerializer,OutletSaleSerializer,OutletSerializer,ProductCategorySerializer,ProductSerializer,PurchaseReceiptSerializer,StockCountSerializer,StockLocationSerializer,StockMovementSerializer,SupplierSerializer
from .services import ensure_stock

class ManagedViewSet(viewsets.ModelViewSet):
    def get_permissions(self):return [IsHotelStaff()] if self.action in ('list','retrieve') else [IsManagement()]
class OutletViewSet(ManagedViewSet): queryset=Outlet.objects.all();serializer_class=OutletSerializer
class ProductCategoryViewSet(ManagedViewSet): queryset=ProductCategory.objects.all();serializer_class=ProductCategorySerializer
class ProductViewSet(ManagedViewSet): queryset=Product.objects.select_related('category').all();serializer_class=ProductSerializer
class SupplierViewSet(ManagedViewSet): queryset=Supplier.objects.all();serializer_class=SupplierSerializer
class StockLocationViewSet(ManagedViewSet): queryset=StockLocation.objects.select_related('outlet').all();serializer_class=StockLocationSerializer
class StockMovementViewSet(viewsets.ModelViewSet):
    permission_classes=[IsHotelStaff];serializer_class=StockMovementSerializer;queryset=StockMovement.objects.select_related('product','location','created_by').all()
    def perform_create(self,serializer):serializer.save(created_by=self.request.user)
    def perform_destroy(self,instance):raise serializers.ValidationError('Stock movements cannot be deleted; create a correcting movement.')
    @action(detail=False,methods=['get'])
    def balances(self,request):
        incoming=[StockMovement.Kind.OPENING,StockMovement.Kind.RECEIVED,StockMovement.Kind.TRANSFER_IN,StockMovement.Kind.RETURN,StockMovement.Kind.ADJUSTMENT,StockMovement.Kind.COUNT]
        rows=StockMovement.objects.values('product_id','product__name','product__reorder_level','location_id','location__name').annotate(balance=Sum(Case(When(kind__in=incoming,then=F('quantity')),default=-F('quantity'),output_field=DecimalField()))).order_by('product__name')
        return Response(list(rows))
    @action(detail=False,methods=['post'])
    @transaction.atomic
    def transfer(self,request):
        try:product=Product.objects.get(id=request.data.get('product'));source=StockLocation.objects.select_for_update().get(id=request.data.get('source'));destination=StockLocation.objects.select_for_update().get(id=request.data.get('destination'));quantity=Decimal(str(request.data.get('quantity')))
        except (Product.DoesNotExist,StockLocation.DoesNotExist,TypeError,ValueError):return Response({'detail':'Select a valid product, source, destination and quantity.'},status=400)
        if source==destination or quantity<=0:return Response({'detail':'Transfer locations must differ and quantity must be positive.'},status=400)
        ensure_stock(product,source,quantity);reference=request.data.get('reference') or f'TRF-{secrets.token_hex(4).upper()}';reason=request.data.get('reason','')
        outgoing=StockMovement.objects.create(product=product,location=source,kind=StockMovement.Kind.TRANSFER_OUT,quantity=quantity,unit_cost=product.purchase_cost,reference=reference,reason=reason,created_by=request.user)
        incoming=StockMovement.objects.create(product=product,location=destination,kind=StockMovement.Kind.TRANSFER_IN,quantity=quantity,unit_cost=product.purchase_cost,reference=reference,reason=reason,created_by=request.user)
        return Response({'reference':reference,'transfer_out':str(outgoing.id),'transfer_in':str(incoming.id)},status=201)
class OutletSaleViewSet(viewsets.ModelViewSet):
    permission_classes=[IsHotelStaff];serializer_class=OutletSaleSerializer;queryset=OutletSale.objects.prefetch_related('lines').select_related('outlet','folio','room','sold_by').all()
    @transaction.atomic
    def perform_create(self,serializer):
        lines=serializer.validated_data.pop('lines');outlet=serializer.validated_data['outlet'];location=StockLocation.objects.select_for_update().filter(outlet=outlet).first()
        if not location:raise serializers.ValidationError('This outlet has no stock location.')
        if serializer.validated_data.get('settlement')==OutletSale.Settlement.ELECTRONIC:raise serializers.ValidationError('Electronic settlement requires a verified payment-provider integration. Use cash, authorized credit or a room charge for now.')
        total=sum((line['quantity']*line['product'].selling_price for line in lines),Decimal('0'));sale=serializer.save(receipt_number=f'POS-{secrets.token_hex(5).upper()}',total=total,sold_by=self.request.user,status=OutletSale.Status.CONFIRMED)
        for line in lines:
            product=line['product'];ensure_stock(product,location,line['quantity']);unit_price=product.selling_price;amount=line['quantity']*unit_price;SaleLine.objects.create(sale=sale,product=product,description=line.get('description') or product.name,quantity=line['quantity'],unit_price=unit_price,amount=amount);StockMovement.objects.create(product=product,location=location,kind=StockMovement.Kind.SALE,quantity=line['quantity'],unit_cost=product.purchase_cost,reference=sale.receipt_number,created_by=self.request.user)
        if sale.settlement==OutletSale.Settlement.ROOM:
            if not sale.folio:raise serializers.ValidationError('A folio is required for a room charge.')
            FolioCharge.objects.create(folio=sale.folio,kind=FolioCharge.Kind.OUTLET,description=f'{outlet.name} · {sale.receipt_number}',amount=total,unit_price=total,source_type='OutletSale',source_id=str(sale.id),created_by=self.request.user)
    def perform_destroy(self,instance):raise serializers.ValidationError('Confirmed sales cannot be deleted; void them with a reason.')
    @action(detail=True,methods=['post'])
    @transaction.atomic
    def void(self,request,pk=None):
        sale=self.get_object();reason=request.data.get('reason','').strip()
        if not reason:return Response({'detail':'A void reason is required.'},status=400)
        if sale.status==OutletSale.Status.VOID:return Response({'detail':'Sale is already void.'},status=409)
        location=StockLocation.objects.select_for_update().get(outlet=sale.outlet)
        for line in sale.lines.select_related('product'):
            StockMovement.objects.create(product=line.product,location=location,kind=StockMovement.Kind.RETURN,quantity=line.quantity,unit_cost=line.product.purchase_cost,reference=sale.receipt_number,reason=f'Voided sale: {reason}',created_by=request.user)
        if sale.folio_id:FolioCharge.objects.filter(folio=sale.folio,source_type='OutletSale',source_id=str(sale.id),is_void=False).update(is_void=True,void_reason=reason)
        sale.status=OutletSale.Status.VOID;sale.void_reason=reason;sale.save(update_fields=['status','void_reason']);record_audit(actor=request.user,action='OUTLET_SALE_VOIDED',instance=sale,reason=reason);return Response(self.get_serializer(sale).data)
class CashReconciliationViewSet(viewsets.ModelViewSet):
    permission_classes=[IsHotelStaff];serializer_class=CashReconciliationSerializer;queryset=CashReconciliation.objects.select_related('outlet','prepared_by','approved_by').all()
    def perform_create(self,serializer):
        outlet=serializer.validated_data['outlet'];business_date=serializer.validated_data['business_date'];qs=OutletSale.objects.filter(outlet=outlet,sold_at__date=business_date,status=OutletSale.Status.CONFIRMED);grouped={row['settlement']:row['total'] or Decimal('0') for row in qs.values('settlement').annotate(total=Sum('total'))};serializer.save(prepared_by=self.request.user,expected_cash=grouped.get(OutletSale.Settlement.CASH,0),credit_total=grouped.get(OutletSale.Settlement.CREDIT,0)+grouped.get(OutletSale.Settlement.ELECTRONIC,0),room_charge_total=grouped.get(OutletSale.Settlement.ROOM,0))
    @action(detail=False,methods=['get'])
    def expected(self,request):
        outlet=request.query_params.get('outlet');business_date=request.query_params.get('business_date') or __import__('django.utils.timezone',fromlist=['localdate']).localdate()
        qs=OutletSale.objects.filter(outlet_id=outlet,sold_at__date=business_date,status=OutletSale.Status.CONFIRMED)
        grouped={row['settlement']:row['total'] or Decimal('0') for row in qs.values('settlement').annotate(total=Sum('total'))}
        return Response({'business_date':business_date,'expected_cash':grouped.get(OutletSale.Settlement.CASH,0),'credit_total':grouped.get(OutletSale.Settlement.CREDIT,0)+grouped.get(OutletSale.Settlement.ELECTRONIC,0),'room_charge_total':grouped.get(OutletSale.Settlement.ROOM,0),'transactions':qs.count()})
    @action(detail=True,methods=['post'],permission_classes=[IsManagement])
    def approve(self,request,pk=None):obj=self.get_object();obj.approved_by=request.user;obj.save(update_fields=['approved_by']);return Response(self.get_serializer(obj).data)
class PurchaseReceiptViewSet(viewsets.ModelViewSet):
    permission_classes=[IsHotelStaff];serializer_class=PurchaseReceiptSerializer;queryset=PurchaseReceipt.objects.prefetch_related('lines').select_related('supplier','location','received_by').all()
    @transaction.atomic
    def perform_create(self,serializer):
        lines=serializer.validated_data.pop('lines'); receipt=serializer.save(received_by=self.request.user)
        for line in lines:
            PurchaseReceiptLine.objects.create(receipt=receipt,**line);StockMovement.objects.create(product=line['product'],location=receipt.location,kind=StockMovement.Kind.RECEIVED,quantity=line['quantity'],unit_cost=line['unit_cost'],batch_number=line.get('batch_number',''),expiry_date=line.get('expiry_date'),reference=receipt.reference,created_by=self.request.user)
class StockCountViewSet(viewsets.ModelViewSet):
    permission_classes=[IsHotelStaff];serializer_class=StockCountSerializer;queryset=StockCount.objects.prefetch_related('lines').select_related('location','counted_by','approved_by').all()
    @transaction.atomic
    def perform_create(self,serializer):
        from .services import stock_balance
        lines=serializer.validated_data.pop('lines'); count=serializer.save(counted_by=self.request.user)
        for line in lines:
            StockCountLine.objects.create(stock_count=count,expected_quantity=stock_balance(line['product'],count.location),**line)
    @action(detail=True,methods=['post'],permission_classes=[IsManagement])
    @transaction.atomic
    def approve(self,request,pk=None):
        count=self.get_object()
        if count.status==StockCount.Status.APPROVED:return Response({'detail':'Stock count is already approved.'},status=409)
        for line in count.lines.select_related('product'):
            difference=line.counted_quantity-line.expected_quantity
            if difference: StockMovement.objects.create(product=line.product,location=count.location,kind=StockMovement.Kind.ADJUSTMENT if difference>0 else StockMovement.Kind.CONSUMPTION,quantity=abs(difference),unit_cost=line.product.purchase_cost,reference=f'COUNT-{count.id}',reason=line.reason or 'Approved physical stock count',created_by=request.user)
        count.status=StockCount.Status.APPROVED;count.approved_by=request.user;count.save(update_fields=['status','approved_by']);record_audit(actor=request.user,action='STOCK_COUNT_APPROVED',instance=count);return Response(self.get_serializer(count).data)

from rest_framework import serializers
from .models import CashReconciliation,Outlet,OutletSale,Product,ProductCategory,PurchaseReceipt,PurchaseReceiptLine,SaleLine,StockCount,StockCountLine,StockLocation,StockMovement,Supplier
class OutletSerializer(serializers.ModelSerializer):
    class Meta:model=Outlet;fields='__all__'
class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:model=ProductCategory;fields='__all__'
class ProductSerializer(serializers.ModelSerializer):
    category_name=serializers.CharField(source='category.name',read_only=True)
    class Meta:model=Product;fields='__all__'
class StockLocationSerializer(serializers.ModelSerializer):
    outlet_name=serializers.CharField(source='outlet.name',read_only=True)
    class Meta:model=StockLocation;fields='__all__'
class StockMovementSerializer(serializers.ModelSerializer):
    product_name=serializers.CharField(source='product.name',read_only=True);location_name=serializers.CharField(source='location.name',read_only=True)
    class Meta:model=StockMovement;fields='__all__';read_only_fields=('created_by',)
    def validate(self,data):
        from .services import ensure_stock
        outgoing=[StockMovement.Kind.TRANSFER_OUT,StockMovement.Kind.SALE,StockMovement.Kind.CONSUMPTION,StockMovement.Kind.BREAKAGE,StockMovement.Kind.EXPIRY,StockMovement.Kind.DEFECT,StockMovement.Kind.WASTAGE]
        if data.get('kind') in outgoing:ensure_stock(data['product'],data['location'],data['quantity'])
        return data
class SaleLineSerializer(serializers.ModelSerializer):
    class Meta:model=SaleLine;fields=('product','description','quantity','unit_price','amount');read_only_fields=('amount',)
class OutletSaleSerializer(serializers.ModelSerializer):
    lines=SaleLineSerializer(many=True)
    outlet_name=serializers.CharField(source='outlet.name',read_only=True);room_number=serializers.CharField(source='room.number',read_only=True);sold_by_name=serializers.CharField(source='sold_by.__str__',read_only=True)
    class Meta:model=OutletSale;fields='__all__';read_only_fields=('receipt_number','total','sold_by','status','void_reason')
class CashReconciliationSerializer(serializers.ModelSerializer):
    variance=serializers.SerializerMethodField()
    outlet_name=serializers.CharField(source='outlet.name',read_only=True)
    class Meta:model=CashReconciliation;fields='__all__';read_only_fields=('prepared_by','approved_by')
    def get_variance(self,obj):return obj.actual_cash-obj.expected_cash
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:model=Supplier;fields='__all__'
class PurchaseReceiptLineSerializer(serializers.ModelSerializer):
    class Meta:model=PurchaseReceiptLine;fields=('product','quantity','unit_cost','batch_number','expiry_date')
class PurchaseReceiptSerializer(serializers.ModelSerializer):
    lines=PurchaseReceiptLineSerializer(many=True)
    supplier_name=serializers.CharField(source='supplier.name',read_only=True);location_name=serializers.CharField(source='location.name',read_only=True)
    class Meta:model=PurchaseReceipt;fields='__all__';read_only_fields=('received_by',)
class StockCountLineSerializer(serializers.ModelSerializer):
    variance=serializers.SerializerMethodField()
    class Meta:model=StockCountLine;fields='__all__';read_only_fields=('stock_count','expected_quantity')
    def get_variance(self,obj):return obj.counted_quantity-obj.expected_quantity
class StockCountSerializer(serializers.ModelSerializer):
    lines=StockCountLineSerializer(many=True)
    class Meta:model=StockCount;fields='__all__';read_only_fields=('counted_by','approved_by')

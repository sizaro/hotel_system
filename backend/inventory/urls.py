from rest_framework.routers import DefaultRouter
from .views import CashReconciliationViewSet,OutletSaleViewSet,OutletViewSet,ProductCategoryViewSet,ProductViewSet,PurchaseReceiptViewSet,StockCountViewSet,StockLocationViewSet,StockMovementViewSet,SupplierViewSet
router=DefaultRouter();router.register('outlets',OutletViewSet);router.register('categories',ProductCategoryViewSet);router.register('products',ProductViewSet);router.register('suppliers',SupplierViewSet);router.register('locations',StockLocationViewSet);router.register('movements',StockMovementViewSet);router.register('purchases',PurchaseReceiptViewSet);router.register('stock-counts',StockCountViewSet);router.register('sales',OutletSaleViewSet);router.register('reconciliations',CashReconciliationViewSet)
urlpatterns=router.urls

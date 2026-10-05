from datetime import date
from decimal import Decimal
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient
from hotels.models import Hotel
from users.models import User
from .models import Outlet,OutletSale,Product,ProductCategory,StockLocation,StockMovement
from .services import ensure_stock,stock_balance

class StockLedgerTests(TestCase):
    def setUp(self):
        hotel=Hotel.objects.create(name='Test Hotel',is_active=True);category=ProductCategory.objects.create(hotel=hotel,name='Drinks');self.location=StockLocation.objects.create(hotel=hotel,name='Main store');self.product=Product.objects.create(hotel=hotel,category=category,name='Water',sku='WATER',unit='bottle');self.user=User.objects.create_user(email='store@test.local',password='SafePassword123!',role=User.Role.MANAGER)
    def test_balance_and_negative_stock_protection(self):
        StockMovement.objects.create(product=self.product,location=self.location,kind=StockMovement.Kind.RECEIVED,quantity=Decimal('10'),created_by=self.user)
        self.assertEqual(stock_balance(self.product,self.location),Decimal('10'))
        ensure_stock(self.product,self.location,Decimal('10'))
        with self.assertRaises(ValidationError):ensure_stock(self.product,self.location,Decimal('11'))
    def test_confirmed_outlet_sale_uses_configured_price_and_reduces_stock(self):
        outlet=Outlet.objects.create(hotel=self.product.hotel,name='Bar',kind=Outlet.Kind.BAR);self.location.outlet=outlet;self.location.save(update_fields=['outlet']);self.product.selling_price=Decimal('3000');self.product.purchase_cost=Decimal('1000');self.product.save(update_fields=['selling_price','purchase_cost']);StockMovement.objects.create(product=self.product,location=self.location,kind=StockMovement.Kind.RECEIVED,quantity=Decimal('10'),created_by=self.user)
        client=APIClient();client.force_authenticate(self.user);response=client.post('/api/inventory/sales/',{'outlet':str(outlet.id),'settlement':'CASH','sold_at':f'{date.today()}T12:00:00+03:00','remarks':'Counter sale','lines':[{'product':str(self.product.id),'description':'Water','quantity':'2','unit_price':'1'}]},format='json')
        self.assertEqual(response.status_code,201,response.data);sale=OutletSale.objects.get(id=response.data['id']);self.assertEqual(sale.total,Decimal('6000'));self.assertEqual(stock_balance(self.product,self.location),Decimal('8'))

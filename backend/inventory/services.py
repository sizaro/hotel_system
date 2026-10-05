from decimal import Decimal
from django.db.models import Case,DecimalField,F,Sum,When
from rest_framework.exceptions import ValidationError
from .models import StockMovement
INCOMING=[StockMovement.Kind.OPENING,StockMovement.Kind.RECEIVED,StockMovement.Kind.TRANSFER_IN,StockMovement.Kind.RETURN,StockMovement.Kind.ADJUSTMENT,StockMovement.Kind.COUNT]
def stock_balance(product,location):return StockMovement.objects.filter(product=product,location=location).aggregate(value=Sum(Case(When(kind__in=INCOMING,then=F('quantity')),default=-F('quantity'),output_field=DecimalField())))['value'] or Decimal('0')
def ensure_stock(product,location,quantity):
    available=stock_balance(product,location)
    if available<quantity:raise ValidationError(f'Insufficient stock for {product.name}. Available: {available} {product.unit}.')

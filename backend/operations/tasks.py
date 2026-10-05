from celery import shared_task
from django.utils import timezone
from .models import Communication,Notification
from django.db.models import Case,DecimalField,F,Sum,When
from inventory.models import Product,StockMovement
from users.models import User

@shared_task
def deliver_due_communications():
    due=Communication.objects.filter(status=Communication.Status.QUEUED,scheduled_at__lte=timezone.now())
    count=due.update(status=Communication.Status.SENT,sent_at=timezone.now());return {'sent':count}
@shared_task
def create_low_stock_notifications():
    created=0
    for product in Product.objects.filter(is_active=True,reorder_level__gt=0):
        incoming=[StockMovement.Kind.OPENING,StockMovement.Kind.RECEIVED,StockMovement.Kind.TRANSFER_IN,StockMovement.Kind.RETURN,StockMovement.Kind.ADJUSTMENT,StockMovement.Kind.COUNT]
        balance=product.movements.aggregate(value=Sum(Case(When(kind__in=incoming,then=F('quantity')),default=-F('quantity'),output_field=DecimalField())))['value'] or 0
        if balance>product.reorder_level:continue
        for manager in User.objects.filter(role__in=[User.Role.OWNER,User.Role.ADMIN,User.Role.MANAGER],is_active=True):
            _,was_created=Notification.objects.get_or_create(user=manager,title=f'Low stock: {product.name}',is_read=False,defaults={'message':f'{product.name} has reached {balance} {product.unit}; reorder level is {product.reorder_level}.','kind':'LOW_STOCK','action_url':'/dashboard/inventory'})
            created+=int(was_created)
    return {'notifications_created':created}
@shared_task
def synchronization_health_summary():return {'pending':__import__('operations.models',fromlist=['SyncOperation']).SyncOperation.objects.filter(status='PENDING').count(),'at':timezone.now().isoformat()}

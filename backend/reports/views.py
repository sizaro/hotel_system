from django.db.models import Count,DecimalField,ExpressionWrapper,F,Sum
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from bookings.models import Booking
from events.models import EventBooking
from finance.models import Folio,Payment,Stay
from inventory.models import CashReconciliation,OutletSale,StockMovement
from operations.models import HousekeepingTask,MaintenanceTicket,SyncOperation
from rooms.models import Room
from users.permissions import IsManagement

class CommandCenterView(APIView):
    permission_classes=[IsManagement]
    def get(self,request):
        today=timezone.localdate();active_stays=Stay.objects.filter(status=Stay.Status.CHECKED_IN)
        confirmed_payments=Payment.objects.filter(status=Payment.Status.CONFIRMED);confirmed_sales=OutletSale.objects.filter(status=OutletSale.Status.CONFIRMED)
        return Response({'as_of':timezone.now(),'rooms':{'total':Room.objects.filter(is_active=True).count(),'available':Room.objects.filter(is_active=True,occupancy_status=Room.Occupancy.AVAILABLE).count(),'occupied':Room.objects.filter(occupancy_status=Room.Occupancy.OCCUPIED).count(),'out_of_service':Room.objects.filter(occupancy_status=Room.Occupancy.OUT_OF_SERVICE).count()},'stays':{'active':active_stays.count(),'arrivals_today':Stay.objects.filter(arrival_date=today).count(),'departures_today':Stay.objects.filter(departure_date=today).count(),'booking_requests':Booking.objects.filter(status=Booking.Status.REQUESTED).count()},'finance':{'payments_today':confirmed_payments.filter(received_at__date=today).aggregate(v=Sum('amount'))['v'] or 0,'payments_total':confirmed_payments.aggregate(v=Sum('amount'))['v'] or 0,'outlet_sales_today':confirmed_sales.filter(sold_at__date=today).aggregate(v=Sum('total'))['v'] or 0,'open_folios':Folio.objects.filter(status=Folio.Status.OPEN).count()},'events':{'upcoming':EventBooking.objects.filter(start_at__gte=timezone.now(),status__in=[EventBooking.Status.CONFIRMED,EventBooking.Status.REQUESTED]).count()},'operations':{'housekeeping_open':HousekeepingTask.objects.exclude(status=HousekeepingTask.Status.DONE).count(),'maintenance_open':MaintenanceTicket.objects.exclude(status__in=[MaintenanceTicket.Status.RESOLVED,MaintenanceTicket.Status.CLOSED]).count(),'sync_conflicts':SyncOperation.objects.filter(status=SyncOperation.Status.CONFLICT).count()}})
class OutletReportView(APIView):
    permission_classes=[IsManagement]
    def get(self,request):
        start=request.query_params.get('start');end=request.query_params.get('end');qs=OutletSale.objects.filter(status=OutletSale.Status.CONFIRMED)
        if start:qs=qs.filter(sold_at__date__gte=start)
        if end:qs=qs.filter(sold_at__date__lte=end)
        return Response(list(qs.values('outlet__name','settlement').annotate(transactions=Count('id'),total=Sum('total')).order_by('outlet__name','settlement')))
class StockReportView(APIView):
    permission_classes=[IsManagement]
    def get(self,request):
        from django.db.models import Case,Value,When
        start=request.query_params.get('start');end=request.query_params.get('end');location=request.query_params.get('location');qs=StockMovement.objects.all()
        if start:qs=qs.filter(created_at__date__gte=start)
        if end:qs=qs.filter(created_at__date__lte=end)
        if location:qs=qs.filter(location_id=location)
        incoming=[StockMovement.Kind.OPENING,StockMovement.Kind.RECEIVED,StockMovement.Kind.TRANSFER_IN,StockMovement.Kind.RETURN,StockMovement.Kind.ADJUSTMENT,StockMovement.Kind.COUNT]
        return Response(list(qs.values('product_id','product__name','location_id','location__name').annotate(opening=Sum(Case(When(kind=StockMovement.Kind.OPENING,then=F('quantity')),default=Value(0),output_field=DecimalField())),received=Sum(Case(When(kind=StockMovement.Kind.RECEIVED,then=F('quantity')),default=Value(0),output_field=DecimalField())),sales=Sum(Case(When(kind=StockMovement.Kind.SALE,then=F('quantity')),default=Value(0),output_field=DecimalField())),breakage=Sum(Case(When(kind=StockMovement.Kind.BREAKAGE,then=F('quantity')),default=Value(0),output_field=DecimalField())),expiry=Sum(Case(When(kind=StockMovement.Kind.EXPIRY,then=F('quantity')),default=Value(0),output_field=DecimalField())),defect=Sum(Case(When(kind=StockMovement.Kind.DEFECT,then=F('quantity')),default=Value(0),output_field=DecimalField())),system_closing=Sum(Case(When(kind__in=incoming,then=F('quantity')),default=-F('quantity'),output_field=DecimalField()))).order_by('product__name')))
class CashControlReportView(APIView):
    permission_classes=[IsManagement]
    def get(self,request):
        qs=CashReconciliation.objects.all();start=request.query_params.get('start');end=request.query_params.get('end')
        if start:qs=qs.filter(business_date__gte=start)
        if end:qs=qs.filter(business_date__lte=end)
        return Response(list(qs.annotate(variance=F('actual_cash')-F('expected_cash')).values('outlet__name','business_date','expected_cash','actual_cash','credit_total','room_charge_total','variance').order_by('-business_date')))

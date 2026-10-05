from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.views import APIView
from bookings.models import Booking
from finance.models import Folio,Payment
from inventory.models import OutletSale,StockMovement
from rooms.models import RoomType

class HotelAssistantView(APIView):
    def post(self,request):
        question=request.data.get('question','').lower().strip()
        if not question:return Response({'detail':'Ask a question about hotel information or your account.'},status=400)
        if 'my' in question and ('balance' in question or 'folio' in question):
            folios=Folio.objects.prefetch_related('charges','payments').filter(guest__email__iexact=request.user.email);return Response({'answer':'Your account balances are calculated from confirmed hotel records.','data':[{'reference':x.reference,'balance':x.balance,'status':x.status} for x in folios]})
        if 'my booking' in question or 'my reservation' in question:
            rows=Booking.objects.filter(guest__email__iexact=request.user.email).values('reference','arrival_date','departure_date','status','room_type__name');return Response({'answer':'These are your reservation records.','data':list(rows)})
        if 'room' in question and ('available' in question or 'rate' in question):
            rows=RoomType.objects.filter(is_active=True,hotel__is_active=True).values('name','capacity','base_rate');return Response({'answer':'These are the currently configured room types and rates. Exact date availability must be confirmed by the booking service.','data':list(rows)})
        if request.user.is_staff or request.user.role in ['OWNER','ADMIN','MANAGER']:
            if 'revenue' in question or 'sales' in question:return Response({'answer':'Confirmed revenue records only.','data':{'payments':Payment.objects.filter(status='CONFIRMED').aggregate(v=Sum('amount'))['v'] or 0,'outlet_sales':OutletSale.objects.filter(status='CONFIRMED').aggregate(v=Sum('total'))['v'] or 0}})
            if 'breakage' in question:return Response({'answer':'Recorded inventory breakages only.','data':list(StockMovement.objects.filter(kind='BREAKAGE').values('product__name').annotate(quantity=Sum('quantity')))})
        return Response({'answer':'I can answer using configured hotel information and authorized transactional records. I will not guess unavailable financial, booking, or stock information.','data':None})

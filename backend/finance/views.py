import secrets
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework import permissions,serializers,status,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rooms.models import Room
from users.models import User
from users.permissions import IsFinanceStaff,IsHotelStaff,IsManagement
from hotels.audit import record_audit
from .models import Expense,Folio,FolioCharge,InstallmentSchedule,Invoice,Payment,Quotation,Refund,Stay
from .serializers import ExpenseSerializer,FolioChargeSerializer,FolioSerializer,InstallmentScheduleSerializer,InvoiceSerializer,PaymentSerializer,QuotationSerializer,RefundSerializer,StaySerializer

class StayViewSet(viewsets.ModelViewSet):
    serializer_class=StaySerializer; permission_classes=[IsHotelStaff]
    def get_queryset(self): return Stay.objects.select_related('guest','room','booking','receptionist').all()
    @transaction.atomic
    def perform_create(self,serializer):
        room=serializer.validated_data['room']; arrival=serializer.validated_data['arrival_date']; departure=serializer.validated_data['departure_date']
        if Stay.objects.select_for_update().filter(room=room,status__in=[Stay.Status.RESERVED,Stay.Status.CHECKED_IN],arrival_date__lt=departure,departure_date__gt=arrival).exists(): raise serializers.ValidationError('This room is unavailable for those dates.')
        stay=serializer.save(receptionist=self.request.user); folio=Folio.objects.create(hotel=stay.hotel,stay=stay,guest=stay.guest,reference=f'FOL-{secrets.token_hex(4).upper()}')
        nights=max((departure-arrival).days,1); FolioCharge.objects.create(folio=folio,kind=FolioCharge.Kind.ROOM,description=f'{nights} night accommodation',quantity=nights,unit_price=stay.rate,amount=stay.rate*nights,created_by=self.request.user)
    @action(detail=True,methods=['post'])
    @transaction.atomic
    def check_in(self,request,pk=None):
        stay=self.get_object()
        if stay.status!=Stay.Status.RESERVED:return Response({'detail':'Only a reserved stay can be checked in.'},status=409)
        previous={'status':stay.status}; stay.status=Stay.Status.CHECKED_IN; stay.checked_in_at=timezone.now(); stay.room.occupancy_status=Room.Occupancy.OCCUPIED; stay.room.save(update_fields=['occupancy_status','updated_at']); stay.save(update_fields=['status','checked_in_at','updated_at'])
        if stay.booking_id:stay.booking.status=stay.booking.Status.CHECKED_IN;stay.booking.save(update_fields=['status','updated_at'])
        record_audit(actor=request.user,action='STAY_CHECK_IN',instance=stay,previous=previous,new={'status':stay.status}); return Response(self.get_serializer(stay).data)
    @action(detail=True,methods=['post'])
    @transaction.atomic
    def check_out(self,request,pk=None):
        stay=self.get_object()
        if stay.status!=Stay.Status.CHECKED_IN:return Response({'detail':'Only a checked-in stay can be checked out.'},status=409)
        if stay.folio.balance>0: return Response({'detail':'The folio has an outstanding balance. Settle or authorize it before checkout.'},status=409)
        previous={'status':stay.status}; stay.status=Stay.Status.CHECKED_OUT; stay.checked_out_at=timezone.now(); stay.room.occupancy_status=Room.Occupancy.AVAILABLE; stay.room.cleaning_status=Room.Cleaning.DIRTY; stay.room.save(update_fields=['occupancy_status','cleaning_status','updated_at']); stay.folio.status=Folio.Status.CLOSED; stay.folio.save(update_fields=['status','updated_at']); stay.save(update_fields=['status','checked_out_at','updated_at'])
        if stay.booking_id:stay.booking.status=stay.booking.Status.CHECKED_OUT;stay.booking.save(update_fields=['status','updated_at'])
        record_audit(actor=request.user,action='STAY_CHECK_OUT',instance=stay,previous=previous,new={'status':stay.status}); return Response(self.get_serializer(stay).data)
    @action(detail=True,methods=['post'])
    @transaction.atomic
    def extend(self,request,pk=None):
        from datetime import date
        stay=self.get_object()
        try:new_departure=date.fromisoformat(request.data.get('departure_date',''))
        except ValueError:return Response({'detail':'Provide a valid departure date.'},status=400)
        if new_departure<=stay.departure_date:return Response({'detail':'The new departure must be later than the current departure.'},status=400)
        if Stay.objects.select_for_update().filter(room=stay.room,status__in=[Stay.Status.RESERVED,Stay.Status.CHECKED_IN],arrival_date__lt=new_departure,departure_date__gt=stay.departure_date).exclude(id=stay.id).exists():return Response({'detail':'The room is already reserved during the requested extension.'},status=409)
        extra=(new_departure-stay.departure_date).days;previous={'departure_date':str(stay.departure_date)};stay.departure_date=new_departure;stay.save(update_fields=['departure_date','updated_at']);FolioCharge.objects.create(folio=stay.folio,kind=FolioCharge.Kind.ROOM,description=f'{extra} night stay extension',quantity=extra,unit_price=stay.rate,amount=stay.rate*extra,created_by=request.user);record_audit(actor=request.user,action='STAY_EXTENDED',instance=stay,previous=previous,new={'departure_date':str(new_departure)});return Response(self.get_serializer(stay).data)
    @action(detail=True,methods=['post'])
    @transaction.atomic
    def transfer(self,request,pk=None):
        stay=self.get_object()
        try:new_room=Room.objects.select_for_update().get(id=request.data.get('room_id'),is_active=True)
        except Room.DoesNotExist:return Response({'detail':'Select an active destination room.'},status=400)
        if Stay.objects.filter(room=new_room,status__in=[Stay.Status.RESERVED,Stay.Status.CHECKED_IN],arrival_date__lt=stay.departure_date,departure_date__gt=stay.arrival_date).exclude(id=stay.id).exists():return Response({'detail':'The destination room is unavailable.'},status=409)
        old_room=stay.room;previous={'room':str(old_room.id)};stay.room=new_room;stay.save(update_fields=['room','updated_at'])
        if stay.status==Stay.Status.CHECKED_IN:new_room.occupancy_status=Room.Occupancy.OCCUPIED;new_room.save(update_fields=['occupancy_status','updated_at']);old_room.occupancy_status=Room.Occupancy.AVAILABLE;old_room.cleaning_status=Room.Cleaning.DIRTY;old_room.save(update_fields=['occupancy_status','cleaning_status','updated_at'])
        record_audit(actor=request.user,action='STAY_ROOM_TRANSFER',instance=stay,reason=request.data.get('reason',''),previous=previous,new={'room':str(new_room.id)});return Response(self.get_serializer(stay).data)
class FolioViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class=FolioSerializer
    def get_queryset(self):
        qs=Folio.objects.prefetch_related('charges','payments').select_related('guest','stay')
        return qs.filter(guest__email__iexact=self.request.user.email) if self.request.user.role==User.Role.CUSTOMER else qs
class FolioChargeViewSet(viewsets.ModelViewSet):
    serializer_class=FolioChargeSerializer; permission_classes=[IsFinanceStaff]; queryset=FolioCharge.objects.all()
    def perform_create(self,serializer): serializer.save(created_by=self.request.user)
    def perform_destroy(self,instance): raise serializers.ValidationError('Financial charges cannot be deleted; void them with an audit reason.')
class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class=PaymentSerializer; permission_classes=[IsFinanceStaff]
    def get_queryset(self): return Payment.objects.select_related('folio','received_by').all()
    def perform_create(self,serializer): serializer.save(received_by=self.request.user,receipt_number=serializer.validated_data.get('receipt_number') or f'RCT-{secrets.token_hex(5).upper()}')
    def perform_destroy(self,instance): raise serializers.ValidationError('Payments cannot be deleted. Use reversal.')
    @action(detail=True,methods=['post'])
    def reverse(self,request,pk=None):
        payment=self.get_object(); reason=request.data.get('reason','').strip()
        if not reason:return Response({'detail':'A reversal reason is required.'},status=400)
        if payment.status==Payment.Status.REVERSED:return Response({'detail':'Payment is already reversed.'},status=409)
        previous={'status':payment.status,'amount':str(payment.amount)}; payment.status=Payment.Status.REVERSED;payment.reversed_by=request.user;payment.reversed_at=timezone.now();payment.reversal_reason=reason;payment.save(update_fields=['status','reversed_by','reversed_at','reversal_reason']);record_audit(actor=request.user,action='PAYMENT_REVERSED',instance=payment,reason=reason,previous=previous,new={'status':payment.status});return Response(self.get_serializer(payment).data)
class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class=InvoiceSerializer; permission_classes=[IsFinanceStaff]; queryset=Invoice.objects.select_related('folio').all()
    def perform_create(self,serializer): serializer.save(created_by=self.request.user)
class RefundViewSet(viewsets.ModelViewSet):
    serializer_class=RefundSerializer; permission_classes=[IsFinanceStaff]; queryset=Refund.objects.select_related('payment','requested_by','approved_by').all()
    def perform_create(self,serializer): serializer.save(requested_by=self.request.user)
    @action(detail=True,methods=['post'],permission_classes=[IsManagement])
    def decide(self,request,pk=None):
        refund=self.get_object(); decision=request.data.get('decision'); reason=request.data.get('reason','')
        if decision not in [Refund.Status.APPROVED,Refund.Status.REJECTED]: return Response({'detail':'Decision must be APPROVED or REJECTED.'},status=400)
        refund.status=decision; refund.approved_by=request.user; refund.save(update_fields=['status','approved_by','updated_at']); record_audit(actor=request.user,action=f'REFUND_{decision}',instance=refund,reason=reason); return Response(self.get_serializer(refund).data)
    @action(detail=True,methods=['post'],permission_classes=[IsFinanceStaff])
    @transaction.atomic
    def mark_paid(self,request,pk=None):
        refund=self.get_object()
        if refund.status!=Refund.Status.APPROVED:return Response({'detail':'Only an approved refund can be paid.'},status=409)
        paid=sum((x.amount for x in refund.payment.refunds.filter(status=Refund.Status.PAID)),Decimal('0'))
        if paid+refund.amount>refund.payment.amount:return Response({'detail':'Total refunds cannot exceed the original payment.'},status=409)
        refund.status=Refund.Status.PAID;refund.paid_at=timezone.now();refund.proof_url=request.data.get('proof_url','');refund.save(update_fields=['status','paid_at','proof_url','updated_at'])
        if paid+refund.amount==refund.payment.amount:refund.payment.status=Payment.Status.REFUNDED;refund.payment.save(update_fields=['status'])
        record_audit(actor=request.user,action='REFUND_PAID',instance=refund,new={'amount':str(refund.amount),'status':refund.status});return Response(self.get_serializer(refund).data)
class InstallmentScheduleViewSet(viewsets.ModelViewSet):
    serializer_class=InstallmentScheduleSerializer; permission_classes=[IsFinanceStaff]; queryset=InstallmentSchedule.objects.select_related('invoice').all()
class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class=ExpenseSerializer; permission_classes=[IsFinanceStaff]; queryset=Expense.objects.select_related('created_by','approved_by').all()
    def perform_create(self,serializer): serializer.save(created_by=self.request.user)
    def perform_destroy(self,instance):
        if instance.status!=Expense.Status.DRAFT:raise serializers.ValidationError('Only draft expenses may be deleted; use cancel for submitted records.')
        instance.delete()
    @action(detail=True,methods=['post'],permission_classes=[IsManagement])
    def decide(self,request,pk=None):
        expense=self.get_object(); decision=request.data.get('decision'); reason=request.data.get('reason','').strip(); allowed=[Expense.Status.APPROVED,Expense.Status.REJECTED,Expense.Status.PAID,Expense.Status.CANCELLED]
        if decision not in allowed:return Response({'detail':'Invalid expense decision.'},status=400)
        expense.status=decision;expense.approved_by=request.user;expense.decision_reason=reason;expense.save(update_fields=['status','approved_by','decision_reason','updated_at']);record_audit(actor=request.user,action=f'EXPENSE_{decision}',instance=expense,reason=reason);return Response(self.get_serializer(expense).data)
class QuotationViewSet(viewsets.ModelViewSet):
    serializer_class=QuotationSerializer; permission_classes=[IsFinanceStaff]; queryset=Quotation.objects.select_related('guest','created_by').all()
    def perform_create(self,serializer): serializer.save(number=f'QUO-{secrets.token_hex(5).upper()}',created_by=self.request.user)

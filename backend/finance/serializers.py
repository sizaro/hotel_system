from rest_framework import serializers
from .models import Expense,Folio,FolioCharge,InstallmentSchedule,Invoice,Payment,Quotation,Refund,Stay

class StaySerializer(serializers.ModelSerializer):
    guest_name=serializers.CharField(source='guest.__str__',read_only=True); room_number=serializers.CharField(source='room.number',read_only=True)
    class Meta: model=Stay; fields='__all__'; read_only_fields=('receptionist','checked_in_at','checked_out_at')
class FolioChargeSerializer(serializers.ModelSerializer):
    class Meta: model=FolioCharge; fields='__all__'; read_only_fields=('created_by',)
class PaymentSerializer(serializers.ModelSerializer):
    class Meta: model=Payment; fields='__all__'; read_only_fields=('receipt_number','received_by','reversed_by','reversed_at','reversal_reason')
    def validate(self,data):
        folio=data.get('folio',getattr(self.instance,'folio',None));amount=data.get('amount',getattr(self.instance,'amount',0));method=data.get('method',getattr(self.instance,'method',None));status=data.get('status',getattr(self.instance,'status',Payment.Status.PENDING))
        if amount<=0:raise serializers.ValidationError({'amount':'Payment must be greater than zero.'})
        if folio and amount>folio.balance:raise serializers.ValidationError({'amount':f'Payment cannot exceed the outstanding folio balance of {folio.balance}.'})
        if method!=Payment.Method.CASH and status==Payment.Status.CONFIRMED and not data.get('provider_reference'):raise serializers.ValidationError({'provider_reference':'A verified provider reference is required before a non-cash payment can be confirmed.'})
        return data
class InvoiceSerializer(serializers.ModelSerializer):
    class Meta: model=Invoice; fields='__all__'; read_only_fields=('created_by',)
class FolioSerializer(serializers.ModelSerializer):
    charges=FolioChargeSerializer(many=True,read_only=True); payments=PaymentSerializer(many=True,read_only=True); total_charges=serializers.DecimalField(max_digits=12,decimal_places=2,read_only=True); total_payments=serializers.DecimalField(max_digits=12,decimal_places=2,read_only=True); balance=serializers.DecimalField(max_digits=12,decimal_places=2,read_only=True)
    guest_name=serializers.CharField(source='guest.__str__',read_only=True);room_number=serializers.CharField(source='stay.room.number',read_only=True)
    class Meta: model=Folio; fields='__all__'
class RefundSerializer(serializers.ModelSerializer):
    class Meta: model=Refund; fields='__all__'; read_only_fields=('requested_by','approved_by','paid_at')
    def validate(self,data):
        payment=data.get('payment',getattr(self.instance,'payment',None)); amount=data.get('amount',getattr(self.instance,'amount',0))
        if payment and amount>payment.amount: raise serializers.ValidationError('A refund cannot exceed the original payment.')
        return data
class InstallmentScheduleSerializer(serializers.ModelSerializer):
    class Meta: model=InstallmentSchedule; fields='__all__'
class ExpenseSerializer(serializers.ModelSerializer):
    class Meta: model=Expense; fields='__all__'; read_only_fields=('created_by','approved_by','decision_reason')
class QuotationSerializer(serializers.ModelSerializer):
    class Meta: model=Quotation; fields='__all__'; read_only_fields=('number','created_by')

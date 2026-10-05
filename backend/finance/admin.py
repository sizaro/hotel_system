from django.contrib import admin
from .models import Expense,Folio,FolioCharge,InstallmentSchedule,Invoice,Payment,Quotation,Refund,Stay
admin.site.register([Stay,Folio,FolioCharge,Payment,Invoice,Refund,InstallmentSchedule,Expense,Quotation])

from django.urls import path
from .views import CashControlReportView,CommandCenterView,OutletReportView,StockReportView
urlpatterns=[path('command-center/',CommandCenterView.as_view()),path('outlets/',OutletReportView.as_view()),path('stock/',StockReportView.as_view()),path('cash-control/',CashControlReportView.as_view())]

from django.urls import path
from .views import HotelAssistantView
urlpatterns=[path('ask/',HotelAssistantView.as_view())]

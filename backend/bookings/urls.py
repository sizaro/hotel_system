from django.urls import include,path
from rest_framework.routers import DefaultRouter
from .views import BookingRequestView,BookingViewSet,GuestProfileViewSet,MyBookingsView
router=DefaultRouter();router.register('guests',GuestProfileViewSet,basename='guests');router.register('',BookingViewSet,basename='staff-bookings')
urlpatterns=[path("request/",BookingRequestView.as_view()),path("mine/",MyBookingsView.as_view()),path('',include(router.urls))]

from rest_framework.routers import DefaultRouter
from .views import EventBookingViewSet,EventServiceViewSet,EventTaskViewSet,EventTypeViewSet,VenueViewSet
router=DefaultRouter();router.register('venues',VenueViewSet);router.register('types',EventTypeViewSet);router.register('bookings',EventBookingViewSet,basename='event-bookings');router.register('services',EventServiceViewSet);router.register('tasks',EventTaskViewSet)
urlpatterns=router.urls

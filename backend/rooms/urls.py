from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AvailabilityView,PublicRoomTypesView, RoomViewSet
router=DefaultRouter(); router.register("manage",RoomViewSet,basename="room")
urlpatterns=[path("types/",PublicRoomTypesView.as_view()),path("availability/",AvailabilityView.as_view()),path("",include(router.urls))]

from django.urls import path
from .views import room_list_create, room_detail

urlpatterns = [
    path('', room_list_create),
    path('<int:pk>/', room_detail),
]
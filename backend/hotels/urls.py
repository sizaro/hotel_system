from django.urls import path
from .views import HotelSettingsView,MediaUploadView
urlpatterns=[path("settings/",HotelSettingsView.as_view()),path("media/upload/",MediaUploadView.as_view())]

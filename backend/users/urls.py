from django.urls import include,path
from rest_framework.routers import DefaultRouter
from .views import ChangePasswordView,MeView,RegisterView,StaffUserViewSet
router=DefaultRouter();router.register('staff',StaffUserViewSet,basename='staff')
urlpatterns=[path("register/",RegisterView.as_view()),path("me/",MeView.as_view()),path("change-password/",ChangePasswordView.as_view()),path('',include(router.urls))]

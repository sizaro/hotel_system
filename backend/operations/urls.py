from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet,CommunicationViewSet,HousekeepingViewSet,MaintenanceViewSet,NotificationViewSet,SyncViewSet
router=DefaultRouter();router.register('housekeeping',HousekeepingViewSet);router.register('maintenance',MaintenanceViewSet);router.register('notifications',NotificationViewSet,basename='notifications');router.register('communications',CommunicationViewSet);router.register('campaigns',CampaignViewSet);router.register('sync',SyncViewSet,basename='sync')
urlpatterns=router.urls

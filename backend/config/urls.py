from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from strawberry.django.views import GraphQLView
from .schema import schema

def health(_request): return JsonResponse({"status":"healthy","service":"hotel-platform-api"})

urlpatterns=[
    path("admin/",admin.site.urls), path("api/health/",health),
    path("api/auth/token/",TokenObtainPairView.as_view(permission_classes=[AllowAny])), path("api/auth/token/refresh/",TokenRefreshView.as_view(permission_classes=[AllowAny])),
    path("api/auth/",include("users.urls")), path("api/hotel/",include("hotels.urls")), path("api/rooms/",include("rooms.urls")), path("api/bookings/",include("bookings.urls")),
    path("api/finance/",include("finance.urls")), path("api/inventory/",include("inventory.urls")), path("api/events/",include("events.urls")), path("api/operations/",include("operations.urls")), path("api/reports/",include("reports.urls")), path("api/ai/",include("ai.urls")),
    path("graphql/",GraphQLView.as_view(schema=schema,graphql_ide="graphiql")),
]

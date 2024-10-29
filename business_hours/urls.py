# business_hours/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessHoursViewSet

router = DefaultRouter()
router.register('', BusinessHoursViewSet)

app_name = 'business_hours'

urlpatterns = [
    path('', include(router.urls)),
]
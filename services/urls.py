# services/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, ServicePriceViewSet

router = DefaultRouter()
router.register('services', ServiceViewSet)
router.register('prices', ServicePriceViewSet)

app_name = 'services'

urlpatterns = [
    path('', include(router.urls)),
]
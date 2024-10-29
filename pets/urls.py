# pets/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PetViewSet, PetHealthRecordViewSet

router = DefaultRouter()
router.register('pets', PetViewSet, basename='pet')
router.register('health-records', PetHealthRecordViewSet, 
                basename='health-record')

app_name = 'pets'

urlpatterns = [
    path('', include(router.urls)),
]
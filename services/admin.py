# services/admin.py

from django.contrib import admin
from .models import Service, ServicePrice

class ServicePriceInline(admin.TabularInline):
    model = ServicePrice
    extra = 1

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    inlines = [ServicePriceInline]

@admin.register(ServicePrice)
class ServicePriceAdmin(admin.ModelAdmin):
    list_display = ('service', 'dog_size', 'price')
    list_filter = ('dog_size', 'service')
    search_fields = ('service__name',)
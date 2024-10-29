# business_hours/admin.py

from django.contrib import admin
from .models import BusinessHours

@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ('weekday', 'start_time', 'end_time', 'is_open')
    list_filter = ('is_open', 'weekday')
    ordering = ['weekday']
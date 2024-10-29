 
# business_hours/serializers.py

from rest_framework import serializers
from .models import BusinessHours

class BusinessHoursSerializer(serializers.ModelSerializer):
    weekday_display = serializers.CharField(source='get_weekday_display', 
                                          read_only=True)
    
    class Meta:
        model = BusinessHours
        fields = ['id', 'weekday', 'weekday_display', 'start_time', 
                 'end_time', 'is_open']
        read_only_fields = ['id']
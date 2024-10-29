# holidays/serializers.py

from rest_framework import serializers
from .models import Holiday

class HolidaySerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Holiday
        fields = ['id', 'name', 'start_date', 'end_date', 
                 'description', 'duration']
        read_only_fields = ['id']
    
    def get_duration(self, obj):
        return (obj.end_date - obj.start_date).days + 1
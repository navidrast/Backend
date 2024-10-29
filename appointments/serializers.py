# appointments/serializers.py

from rest_framework import serializers
from django.utils import timezone
from .models import Appointment, AppointmentNote
from .utils import is_valid_appointment_time, AppointmentStatus
from services.models import ServicePrice
from datetime import datetime, timedelta

class AppointmentNoteSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.username', read_only=True)
    
    class Meta:
        model = AppointmentNote
        fields = ['id', 'note', 'staff_name', 'created_at']
        read_only_fields = ['id', 'created_at']

class AppointmentSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    pet_name = serializers.CharField(source='pet.name', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', 
        read_only=True
    )
    notes = AppointmentNoteSerializer(
        source='staff_notes', 
        many=True, 
        read_only=True
    )
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'pet', 'pet_name', 'service', 'service_name',
            'date', 'start_time', 'end_time', 'status', 'status_display',
            'total_price', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'end_time', 'total_price', 'created_at']

    def validate(self, data):
        # 验证预约时间
        is_valid, message = is_valid_appointment_time(
            data['date'],
            data['start_time'],
            data['service'].duration
        )
        if not is_valid:
            raise serializers.ValidationError(message)
            
        # 计算结束时间
        start_datetime = datetime.combine(
            data['date'], 
            data['start_time']
        )
        end_datetime = start_datetime + timedelta(
            minutes=data['service'].duration
        )
        data['end_time'] = end_datetime.time()
        
        # 验证宠物属于当前用户
        if data['pet'].owner != self.context['request'].user:
            raise serializers.ValidationError("只能为自己的宠物预约")
        
        # 计算价格
        try:
            price = ServicePrice.objects.get(
                service=data['service'],
                dog_size=data['pet'].size
            ).price
            data['total_price'] = price
        except ServicePrice.DoesNotExist:
            raise serializers.ValidationError("该服务未设置对应体型的价格")
        
        return data

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data)

class AppointmentDetailSerializer(AppointmentSerializer):
    class Meta(AppointmentSerializer.Meta):
        fields = AppointmentSerializer.Meta.fields + ['notes']
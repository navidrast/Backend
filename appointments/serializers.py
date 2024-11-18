from rest_framework import serializers
from django.utils import timezone
from .models import Appointment, AppointmentNote
from .utils import is_valid_appointment_time, AppointmentStatus
from services.models import ServicePrice
from datetime import datetime, timedelta

class AppointmentNoteSerializer(serializers.ModelSerializer):
    """预约备注序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    is_staff_note = serializers.SerializerMethodField()
    
    class Meta:
        model = AppointmentNote
        fields = [
            'id', 'note', 'note_type', 'user_name',
            'is_staff_note', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'note_type', 'user_name',
            'is_staff_note', 'created_at', 'updated_at'
        ]
    
    def get_is_staff_note(self, obj):
        """判断是否是工作人员备注"""
        return obj.note_type == 'staff'

    def validate(self, attrs):
        """验证备注内容"""
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("No request found in context")

        # 根据用户类型设置备注类型
        attrs['note_type'] = 'staff' if request.user.is_staff else 'customer'
        attrs['user'] = request.user
        
        return attrs

class AppointmentSerializer(serializers.ModelSerializer):
    """预约序列化器"""
    service_name = serializers.CharField(source='service.name', read_only=True)
    pet_name = serializers.CharField(source='pet.name', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', 
        read_only=True
    )
    notes = AppointmentNoteSerializer(
        many=True, 
        read_only=True
    )
    customer_name = serializers.CharField(
        source='customer.username',
        read_only=True
    )
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'customer_name', 'pet', 'pet_name', 
            'service', 'service_name', 'date', 'start_time', 
            'end_time', 'status', 'status_display',
            'total_price', 'notes', 'created_at'
        ]
        read_only_fields = [
            'id', 'customer_name', 'end_time', 
            'total_price', 'created_at'
        ]

    def validate(self, data):
        """验证预约数据"""
        # 验证预约时间
        is_valid, message = is_valid_appointment_time(
            data['date'],
            data['start_time'],
            data['service'].duration
        )
        if not is_valid:
            raise serializers.ValidationError({"time": message})
            
        # 计算结束时间
        start_datetime = timezone.make_aware(
            datetime.combine(data['date'], data['start_time']),
            timezone.get_current_timezone()
        )
        end_datetime = start_datetime + timedelta(
            minutes=data['service'].duration
        )
        data['end_time'] = end_datetime.time()
        
        # 验证宠物归属
        if data['pet'].owner != self.context['request'].user:
            raise serializers.ValidationError(
                {"pet": "Can only make appointments for your own pets"}
            )
        
        # 计算服务价格
        try:
            price = ServicePrice.objects.get(
                service=data['service'],
                dog_size=data['pet'].size
            ).price
            data['total_price'] = price
        except ServicePrice.DoesNotExist:
            raise serializers.ValidationError(
                {"service": "No price set for this service and pet size"}
            )
        
        # 检查时间段是否已被预约
        overlapping_appointments = Appointment.objects.filter(
            date=data['date'],
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
        ).exclude(id=self.instance.id if self.instance else None)
        
        for existing_appointment in overlapping_appointments:
            # 检查时间重叠
            new_start = data['start_time']
            new_end = data['end_time']
            existing_start = existing_appointment.start_time
            existing_end = existing_appointment.end_time
            
            if not (new_end <= existing_start or new_start >= existing_end):
                raise serializers.ValidationError(
                    {"time": "This time slot is already booked"}
                )
        
        return data

    def create(self, validated_data):
        """创建预约时设置客户信息"""
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data)

class AppointmentDetailSerializer(AppointmentSerializer):
    """预约详情序列化器"""
    class Meta(AppointmentSerializer.Meta):
        fields = AppointmentSerializer.Meta.fields + ['notes']
# pets/serializers.py

from rest_framework import serializers
from .models import Pet, PetHealthRecord
from django.utils import timezone
from dateutil.relativedelta import relativedelta

class PetHealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetHealthRecord
        fields = ['id', 'date', 'title', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

class PetSerializer(serializers.ModelSerializer):
    size = serializers.CharField(read_only=True)
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    age = serializers.SerializerMethodField()
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    
    class Meta:
        model = Pet
        fields = [
            'id', 'name', 'breed', 'birthday', 'gender',
            'gender_display', 'is_sterilized', 'notes', 'photo',
            'size', 'size_display', 'age', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_age(self, obj):
        """计算宠物年龄"""
        if not obj.birthday:
            return None
        
        today = timezone.now().date()
        age = relativedelta(today, obj.birthday)
        
        years = age.years
        months = age.months
        
        if years > 0:
            return f"{years}岁{months}个月" if months > 0 else f"{years}岁"
        return f"{months}个月"

class PetDetailSerializer(PetSerializer):
    """详细的宠物信息序列化器，包含健康记录"""
    health_records = PetHealthRecordSerializer(many=True, read_only=True)
    
    class Meta(PetSerializer.Meta):
        fields = PetSerializer.Meta.fields + ['health_records']
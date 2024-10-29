 
# services/serializers.py

from rest_framework import serializers
from .models import Service, ServicePrice, DogSize

class ServicePriceSerializer(serializers.ModelSerializer):
    dog_size_display = serializers.CharField(
        source='get_dog_size_display',
        read_only=True
    )
    
    class Meta:
        model = ServicePrice
        fields = ['id', 'dog_size', 'dog_size_display', 'price']
        read_only_fields = ['id']

class ServiceSerializer(serializers.ModelSerializer):
    prices = ServicePriceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'duration', 
                 'image', 'is_active', 'prices']
        read_only_fields = ['id']

class ServicePriceCreateSerializer(serializers.ModelSerializer):
    """用于创建服务价格的序列化器"""
    class Meta:
        model = ServicePrice
        fields = ['service', 'dog_size', 'price']

    def validate(self, attrs):
        # 检查该服务和狗狗体型的组合是否已存在
        if ServicePrice.objects.filter(
            service=attrs['service'],
            dog_size=attrs['dog_size']
        ).exists():
            raise serializers.ValidationError(
                "该服务的这个体型价格已存在"
            )
        return attrs

class ServiceDetailSerializer(ServiceSerializer):
    """详细的服务信息序列化器"""
    class Meta(ServiceSerializer.Meta):
        fields = ServiceSerializer.Meta.fields + ['created_at', 'updated_at']
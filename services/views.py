# services/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from .models import Service, ServicePrice, DogSize
from .serializers import (
    ServiceSerializer,
    ServiceDetailSerializer,
    ServicePriceSerializer,
    ServicePriceCreateSerializer
)

class ServiceViewSet(viewsets.ModelViewSet):
    """服务项目视图集"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    
    def get_permissions(self):
        """普通用户只能查看，管理员可以进行所有操作"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ServiceDetailSerializer
        return ServiceSerializer

    def get_queryset(self):
        """支持按名称搜索和按是否启用筛选"""
        queryset = Service.objects.all()
        search = self.request.query_params.get('search', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def set_price(self, request, pk=None):
        """设置服务价格"""
        service = self.get_object()
        serializer = ServicePriceCreateSerializer(data={
            'service': service.id,
            **request.data
        })
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def prices(self, request, pk=None):
        """获取服务的所有价格"""
        service = self.get_object()
        prices = service.prices.all()
        serializer = ServicePriceSerializer(prices, many=True)
        return Response(serializer.data)

class ServicePriceViewSet(viewsets.ModelViewSet):
    """服务价格视图集"""
    queryset = ServicePrice.objects.all()
    serializer_class = ServicePriceSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def dog_sizes(self, request):
        """获取所有狗狗体型选项"""
        return Response(dict(DogSize.choices))
# business_hours/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, timedelta
from .models import BusinessHours
from .serializers import BusinessHoursSerializer

class BusinessHoursViewSet(viewsets.ModelViewSet):
    queryset = BusinessHours.objects.all()
    serializer_class = BusinessHoursSerializer
    
    def get_permissions(self):
        """仅管理员可以修改营业时间，其他用户可以查看"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def current_week(self, request):
        """获取本周的营业时间"""
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        business_hours = self.get_queryset()
        serializer = self.get_serializer(business_hours, many=True)
        
        return Response({
            'start_date': start_of_week.date(),
            'end_date': end_of_week.date(),
            'business_hours': serializer.data
        })
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
        """
        - 查看营业时间：允许所有人访问
        - 修改营业时间：仅管理员可操作
        """
        if self.action in ['list', 'retrieve', 'current_week']:
            return []  # 空列表表示允许所有人访问
        return [IsAdminUser()]  # 其他操作需要管理员权限
    
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
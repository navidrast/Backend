# holidays/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime
from django.utils import timezone
from .models import Holiday
from .serializers import HolidaySerializer

class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    
    def get_permissions(self):
        """仅管理员可以修改假期，其他用户可以查看"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """获取即将到来的假期"""
        today = timezone.now().date()
        upcoming_holidays = Holiday.objects.filter(
            end_date__gte=today
        ).order_by('start_date')[:5]
        
        serializer = self.get_serializer(upcoming_holidays, many=True)
        return Response(serializer.data)
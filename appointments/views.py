# appointments/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from .models import Appointment, AppointmentNote
from .serializers import (
    AppointmentSerializer,
    AppointmentDetailSerializer,
    AppointmentNoteSerializer
)
from .utils import AppointmentStatus, get_available_time_slots
from services.models import Service

class AppointmentViewSet(viewsets.ModelViewSet):
    """预约管理视图集"""
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        获取预约列表
        - 管理员可以看到所有预约
        - 普通用户只能看到自己的预约
        """
        user = self.request.user
        queryset = Appointment.objects.all()
        
        # 如果不是管理员，只能看到自己的预约
        if not user.is_staff:
            queryset = queryset.filter(customer=user)
            
        # 获取查询参数
        date = self.request.query_params.get('date')
        status = self.request.query_params.get('status')
        
        # 按日期筛选
        if date:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(date=date_obj)
            except ValueError:
                pass
                
        # 按状态筛选
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.order_by('-date', '-start_time')

    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action == 'retrieve':
            return AppointmentDetailSerializer
        return AppointmentSerializer

    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """
        获取可用的预约时间段
        参数:
        - date: 日期 (YYYY-MM-DD)
        - service_id: 服务ID
        """
        # 获取参数
        date_str = request.query_params.get('date')
        service_id = request.query_params.get('service')
        
        # 验证参数
        if not date_str or not service_id:
            return Response(
                {"error": "必须提供日期和服务ID"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 转换日期格式
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            # 获取服务信息
            service = Service.objects.get(id=service_id)
        except ValueError:
            return Response(
                {"error": "无效的日期格式"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Service.DoesNotExist:
            return Response(
                {"error": "服务不存在"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 检查日期是否是过去的日期
        if date < timezone.now().date():
            return Response(
                {"error": "不能选择过去的日期"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取可用时间段
        available_slots = get_available_time_slots(date, service.duration)
        
        # 获取已存在的预约
        existing_appointments = Appointment.objects.filter(
            date=date,
            status__in=[
                AppointmentStatus.PENDING,
                AppointmentStatus.CONFIRMED
            ]
        )
        
        # 从可用时间段中移除已被预约的时间
        filtered_slots = []
        for slot in available_slots:
            is_available = True
            slot_start = datetime.combine(date, slot['start_time'])
            slot_end = datetime.combine(date, slot['end_time'])
            
            for appointment in existing_appointments:
                appt_start = datetime.combine(
                    date, 
                    appointment.start_time
                )
                appt_end = datetime.combine(
                    date, 
                    appointment.end_time
                )
                
                # 检查是否有重叠
                if not (slot_end <= appt_start or slot_start >= appt_end):
                    is_available = False
                    break
            
            if is_available:
                filtered_slots.append(slot)
        
        return Response({
            'date': date_str,
            'service_id': service_id,
            'service_name': service.name,
            'service_duration': service.duration,
            'available_slots': filtered_slots
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消预约"""
        appointment = self.get_object()
        
        # 检查是否可以取消
        if appointment.status not in [
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED
        ]:
            return Response(
                {"error": "该预约状态无法取消"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否有权限取消
        if not request.user.is_staff and appointment.customer != request.user:
            return Response(
                {"error": "没有权限取消此预约"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # 取消预约
        appointment.status = AppointmentStatus.CANCELLED
        appointment.save()
        
        return Response({
            "message": "预约已成功取消",
            "appointment_id": appointment.id
        })

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """确认预约（仅限管理员）"""
        if not request.user.is_staff:
            return Response(
                {"error": "只有工作人员能确认预约"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        appointment = self.get_object()
        
        # 检查预约状态
        if appointment.status != AppointmentStatus.PENDING:
            return Response(
                {"error": "只能确认待确认状态的预约"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 确认预约
        appointment.status = AppointmentStatus.CONFIRMED
        appointment.save()
        
        return Response({
            "message": "预约已确认",
            "appointment_id": appointment.id
        })

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """完成预约（仅限管理员）"""
        if not request.user.is_staff:
            return Response(
                {"error": "只有工作人员能完成预约"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        appointment = self.get_object()
        
        # 检查预约状态
        if appointment.status != AppointmentStatus.CONFIRMED:
            return Response(
                {"error": "只能完成已确认状态的预约"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 完成预约
        appointment.status = AppointmentStatus.COMPLETED
        appointment.save()
        
        return Response({
            "message": "预约已完成",
            "appointment_id": appointment.id
        })

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """添加预约备注（仅限管理员）"""
        if not request.user.is_staff:
            return Response(
                {"error": "只有工作人员能添加备注"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        appointment = self.get_object()
        serializer = AppointmentNoteSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(
                appointment=appointment,
                staff=request.user
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
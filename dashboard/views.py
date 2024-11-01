from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from django.utils import timezone
from django.db.models import Count, Sum
from datetime import timedelta
from decimal import Decimal
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from typing import Dict, List, Union, Any

from appointments.models import Appointment
from accounts.models import Customer
from appointments.utils import AppointmentStatus

class DashboardViewSet(ViewSet):
    """
    后台仪表盘数据接口，提供统计数据和分析图表所需的数据
    
    所有接口都需要管理员权限
    """
    permission_classes = [IsAdminUser]

    def _calculate_growth_rate(self, current: Union[int, Decimal], previous: Union[int, Decimal]) -> float:
        """计算增长率
        
        Args:
            current: 当前值
            previous: 前期值
            
        Returns:
            float: 增长率，以百分比表示
        """
        if not previous:
            return 0.0
        return round(((float(current) - float(previous)) / float(previous) * 100), 1)

    @swagger_auto_schema(
        operation_description="获取仪表盘统计数据，包括今日预约数、营收和新增客户等关键指标",
        responses={
            200: openapi.Response(
                description="统计数据",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'todayAppointments': openapi.Schema(type=openapi.TYPE_INTEGER, description='今日预约数'),
                        'appointmentGrowth': openapi.Schema(type=openapi.TYPE_NUMBER, description='预约增长率'),
                        'todayRevenue': openapi.Schema(type=openapi.TYPE_NUMBER, description='今日营收'),
                        'revenueGrowth': openapi.Schema(type=openapi.TYPE_NUMBER, description='营收增长率'),
                        'newCustomers': openapi.Schema(type=openapi.TYPE_INTEGER, description='新增客户数'),
                        'customerGrowth': openapi.Schema(type=openapi.TYPE_NUMBER, description='客户增长率'),
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request) -> Response:
        """
        获取仪表盘统计数据，包括：
        1. 今日预约数及增长率
        2. 今日营收及增长率
        3. 新增客户数及增长率
        """
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # 今日预约统计
        today_appointments = Appointment.objects.filter(
            created_at__date=today
        ).count()
        
        yesterday_appointments = Appointment.objects.filter(
            created_at__date=yesterday
        ).count()
        
        # 今日营收（已完成的预约）
        today_revenue = Appointment.objects.filter(
            created_at__date=today,
            status=AppointmentStatus.COMPLETED
        ).aggregate(
            total=Sum('total_price')
        )['total'] or Decimal('0')
        
        yesterday_revenue = Appointment.objects.filter(
            created_at__date=yesterday,
            status=AppointmentStatus.COMPLETED
        ).aggregate(
            total=Sum('total_price')
        )['total'] or Decimal('0')

        # 新增客户统计
        new_customers_today = Customer.objects.filter(
            created_at__date=today
        ).count()
        
        new_customers_yesterday = Customer.objects.filter(
            created_at__date=yesterday
        ).count()

        return Response({
            'todayAppointments': today_appointments,
            'appointmentGrowth': self._calculate_growth_rate(today_appointments, yesterday_appointments),
            'todayRevenue': float(today_revenue),
            'revenueGrowth': self._calculate_growth_rate(today_revenue, yesterday_revenue),
            'newCustomers': new_customers_today,
            'customerGrowth': self._calculate_growth_rate(new_customers_today, new_customers_yesterday)
        })

    @swagger_auto_schema(
        operation_description="获取预约趋势数据，支持按周或月查看",
        manual_parameters=[
            openapi.Parameter(
                'period',
                openapi.IN_QUERY,
                description="统计周期（week: 本周, month: 本月）",
                type=openapi.TYPE_STRING,
                enum=['week', 'month'],
                default='week'
            )
        ],
        responses={
            200: openapi.Response(
                description="预约趋势数据",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'dates': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description='日期列表'
                        ),
                        'values': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_INTEGER),
                            description='每日预约数量'
                        ),
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def appointment_trend(self, request) -> Response:
        """获取预约趋势数据，支持周/月两种时间范围"""
        period = request.query_params.get('period', 'week')
        today = timezone.now().date()
        
        # 确定日期范围
        if period == 'week':
            start_date = today - timedelta(days=6)
            dates = [(start_date + timedelta(days=i)) for i in range(7)]
        else:  # month
            start_date = today - timedelta(days=29)
            dates = [(start_date + timedelta(days=i)) for i in range(30)]

        # 查询预约数据
        appointments_by_date = Appointment.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=today
        ).values('created_at__date').annotate(
            count=Count('id')
        ).order_by('created_at__date')

        # 将查询结果转换为字典
        count_dict = {
            item['created_at__date']: item['count']
            for item in appointments_by_date
        }

        # 构建数据列表，确保每天都有数据
        values = [count_dict.get(date, 0) for date in dates]

        return Response({
            'dates': [date.strftime('%Y-%m-%d') for date in dates],
            'values': values
        })

    @swagger_auto_schema(
        operation_description="获取收入趋势数据，支持按周或月查看",
        manual_parameters=[
            openapi.Parameter(
                'period',
                openapi.IN_QUERY,
                description="统计周期（week: 本周, month: 本月）",
                type=openapi.TYPE_STRING,
                enum=['week', 'month'],
                default='week'
            )
        ],
        responses={
            200: openapi.Response(
                description="收入趋势数据",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'dates': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description='日期列表'
                        ),
                        'values': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_NUMBER),
                            description='每日收入金额'
                        ),
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def revenue_trend(self, request) -> Response:
        """获取收入趋势数据，支持周/月两种时间范围"""
        period = request.query_params.get('period', 'week')
        today = timezone.now().date()
        
        if period == 'week':
            start_date = today - timedelta(days=6)
            dates = [(start_date + timedelta(days=i)) for i in range(7)]
        else:  # month
            start_date = today - timedelta(days=29)
            dates = [(start_date + timedelta(days=i)) for i in range(30)]

        revenue_by_date = Appointment.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=today,
            status=AppointmentStatus.COMPLETED
        ).values('created_at__date').annotate(
            total=Sum('total_price')
        ).order_by('created_at__date')

        # 将查询结果转换为字典
        revenue_dict = {
            item['created_at__date']: float(item['total'])
            for item in revenue_by_date
        }

        # 构建数据列表，确保每天都有数据
        values = [revenue_dict.get(date, 0) for date in dates]

        return Response({
            'dates': [date.strftime('%Y-%m-%d') for date in dates],
            'values': values
        })

    @swagger_auto_schema(
        operation_description="获取最近预约列表",
        manual_parameters=[
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="返回数量限制",
                type=openapi.TYPE_INTEGER,
                default=10
            )
        ],
        responses={
            200: openapi.Response(
                description="最近预约列表",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_STRING, description='预约ID'),
                            'time': openapi.Schema(type=openapi.TYPE_STRING, description='预约时间'),
                            'customerName': openapi.Schema(type=openapi.TYPE_STRING, description='客户名称'),
                            'petName': openapi.Schema(type=openapi.TYPE_STRING, description='宠物名称'),
                            'service': openapi.Schema(type=openapi.TYPE_STRING, description='服务项目'),
                            'status': openapi.Schema(type=openapi.TYPE_STRING, description='预约状态'),
                        }
                    )
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def recent_appointments(self, request) -> Response:
        """获取最近预约列表，支持通过limit参数限制返回数量"""
        limit = int(request.query_params.get('limit', 10))
        appointments = (
            Appointment.objects.select_related('customer', 'pet', 'service')
            .order_by('-created_at')[:limit]
        )
        
        return Response([{
            'id': str(appointment.id),
            'time': appointment.created_at.strftime('%Y-%m-%d %H:%M'),
            'customerName': appointment.customer.username,
            'petName': appointment.pet.name,
            'service': appointment.service.name,
            'status': dict(AppointmentStatus.CHOICES)[appointment.status]
        } for appointment in appointments])
# appointments/views_admin.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from datetime import timedelta
from accounts.models import Customer
from services.models import Service
from .models import Appointment

class AdminDashboardViewSet(viewsets.ViewSet):
    """管理员仪表盘视图集"""
    permission_classes = [IsAdminUser]

    @method_decorator(cache_page(60 * 5))  # 缓存5分钟
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取仪表盘统计数据
        包括：
        - 今日预约数及同比变化
        - 今日收入及同比变化
        - 本月预约数及完成率
        - 客户总数及本月新增
        """
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        first_day_of_month = today.replace(day=1)
        
        # 今日预约统计
        today_appointments = Appointment.objects.filter(date=today).count()
        yesterday_appointments = Appointment.objects.filter(date=yesterday).count()
        appointments_change = (
            ((today_appointments - yesterday_appointments) / yesterday_appointments * 100)
            if yesterday_appointments > 0 else 0
        )
        
        # 收入统计
        today_income = Appointment.objects.filter(
            date=today,
            status__in=['completed', 'confirmed']
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        yesterday_income = Appointment.objects.filter(
            date=yesterday,
            status__in=['completed', 'confirmed']
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        income_change = (
            ((today_income - yesterday_income) / yesterday_income * 100)
            if yesterday_income > 0 else 0
        )
        
        # 本月预约统计
        month_appointments = Appointment.objects.filter(
            date__gte=first_day_of_month
        ).count()
        
        completed_appointments = Appointment.objects.filter(
            date__gte=first_day_of_month,
            status='completed'
        ).count()
        
        completion_rate = (
            (completed_appointments / month_appointments * 100)
            if month_appointments > 0 else 0
        )
        
        # 客户统计
        total_customers = Customer.objects.count()
        new_customers = Customer.objects.filter(
            created_at__gte=first_day_of_month
        ).count()
        
        return Response({
            'todayAppointments': today_appointments,
            'appointmentsChange': round(appointments_change, 2),
            'todayIncome': float(today_income),
            'incomeChange': round(income_change, 2),
            'monthAppointments': month_appointments,
            'completionRate': round(completion_rate, 2),
            'totalCustomers': total_customers,
            'newCustomers': new_customers
        })

    @method_decorator(cache_page(60 * 5))
    @action(detail=False, methods=['get'])
    def appointments_chart(self, request):
        """
        获取预约趋势图数据
        参数：
        - type: week/month 统计周期
        """
        chart_type = request.query_params.get('type', 'week')
        today = timezone.now().date()
        
        if chart_type == 'week':
            start_date = today - timedelta(days=6)
            appointments = (
                Appointment.objects.filter(date__gte=start_date)
                .annotate(day=TruncDate('date'))
                .values('day')
                .annotate(count=Count('id'))
                .order_by('day')
            )
        else:  # month
            start_date = today.replace(day=1)
            appointments = (
                Appointment.objects.filter(date__gte=start_date)
                .annotate(day=TruncDate('date'))
                .values('day')
                .annotate(count=Count('id'))
                .order_by('day')
            )
            
        return Response([{
            'date': item['day'].strftime('%Y-%m-%d'),
            'count': item['count']
        } for item in appointments])

    @method_decorator(cache_page(60 * 5))
    @action(detail=False, methods=['get'])
    def services_chart(self, request):
        """
        获取服务分布图数据
        参数：
        - type: count/income 统计类型（数量/收入）
        """
        chart_type = request.query_params.get('type', 'count')
        
        if chart_type == 'count':
            services = (
                Service.objects.filter(is_active=True)
                .annotate(
                    value=Count('appointments', 
                              filter=Q(appointments__status__in=['completed', 'confirmed']))
                )
            )
        else:  # income
            services = (
                Service.objects.filter(is_active=True)
                .annotate(
                    value=Sum('appointments__total_price',
                             filter=Q(appointments__status__in=['completed', 'confirmed']))
                )
            )
            
        return Response([{
            'name': service.name,
            'value': float(service.value) if chart_type == 'income' else service.value
        } for service in services])

    @action(detail=False, methods=['get'])
    def pending_appointments(self, request):
        """获取待处理的预约列表"""
        appointments = (
            Appointment.objects.filter(status='pending')
            .order_by('date', 'start_time')
            .select_related('customer', 'pet', 'service')
        )
        
        return Response([{
            'id': appointment.id,
            'customer_name': appointment.customer.username,
            'pet_name': appointment.pet.name,
            'service_name': appointment.service.name,
            'date': appointment.date,
            'start_time': appointment.start_time,
            'total_price': float(appointment.total_price),
            'status': appointment.status
        } for appointment in appointments])
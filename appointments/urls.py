# appointments/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet
from .views_admin import AdminDashboardViewSet

router = DefaultRouter()
router.register('appointments', AppointmentViewSet, basename='appointment')
router.register(r'admin/dashboard', AdminDashboardViewSet, basename='admin-dashboard')

app_name = 'appointments'

urlpatterns = [
    path('', include(router.urls)),
]

# 这个配置会自动生成以下URL模式:
# GET/POST          /api/appointments/appointments/          - 列表和创建
# GET/PUT/DELETE    /api/appointments/appointments/{id}/    - 详情、更新和删除
# GET              /api/appointments/appointments/available_slots/ - 获取可用时间段
# POST             /api/appointments/appointments/{id}/cancel/    - 取消预约
# POST             /api/appointments/appointments/{id}/confirm/   - 确认预约
# POST             /api/appointments/appointments/{id}/complete/  - 完成预约
# POST             /api/appointments/appointments/{id}/add_note/  - 添加备注
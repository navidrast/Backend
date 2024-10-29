# appointments/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Appointment, AppointmentNote
from .utils import AppointmentStatus

class AppointmentNoteInline(admin.TabularInline):
    """预约备注内联管理"""
    model = AppointmentNote
    extra = 0
    readonly_fields = ('staff', 'created_at')
    fields = ('staff', 'note', 'created_at')

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """预约管理"""
    list_display = (
        'id', 
        'customer_info', 
        'pet_info', 
        'service_info', 
        'appointment_time', 
        'status_colored', 
        'total_price',
        'created_at'
    )
    list_filter = (
        'status', 
        'date', 
        'service', 
        'created_at'
    )
    search_fields = (
        'customer__username', 
        'customer__email',
        'pet__name', 
        'service__name'
    )
    readonly_fields = (
        'created_at', 
        'updated_at'
    )
    inlines = [AppointmentNoteInline]
    date_hierarchy = 'date'
    
    fieldsets = (
        ('预约信息', {
            'fields': (
                'customer', 
                'pet', 
                'service', 
                'total_price'
            )
        }),
        ('时间信息', {
            'fields': (
                'date', 
                'start_time', 
                'end_time'
            )
        }),
        ('状态信息', {
            'fields': (
                'status', 
                'notes'
            )
        }),
        ('系统信息', {
            'fields': (
                'created_at', 
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    def customer_info(self, obj):
        """客户信息显示"""
        return format_html(
            '<div><strong>{}</strong><br/>{}</div>',
            obj.customer.username,
            obj.customer.email
        )
    customer_info.short_description = '客户信息'

    def pet_info(self, obj):
        """宠物信息显示"""
        return format_html(
            '<div><strong>{}</strong><br/>{}</div>',
            obj.pet.name,
            obj.pet.get_size_display()
        )
    pet_info.short_description = '宠物信息'

    def service_info(self, obj):
        """服务信息显示"""
        return format_html(
            '<div><strong>{}</strong><br/>{}分钟</div>',
            obj.service.name,
            obj.service.duration
        )
    service_info.short_description = '服务信息'

    def appointment_time(self, obj):
        """预约时间显示"""
        return format_html(
            '<div><strong>{}</strong><br/>{} - {}</div>',
            obj.date.strftime('%Y-%m-%d'),
            obj.start_time.strftime('%H:%M'),
            obj.end_time.strftime('%H:%M')
        )
    appointment_time.short_description = '预约时间'

    def status_colored(self, obj):
        """状态彩色显示"""
        colors = {
            AppointmentStatus.PENDING: '#FFA500',    # 橙色
            AppointmentStatus.CONFIRMED: '#007BFF',   # 蓝色
            AppointmentStatus.COMPLETED: '#28A745',   # 绿色
            AppointmentStatus.CANCELLED: '#DC3545'    # 红色
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colored.short_description = '状态'

    def save_model(self, request, obj, form, change):
        """保存模型时的额外操作"""
        if not change:  # 如果是新建预约
            if not obj.customer:
                obj.customer = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """保存内联模型时的额外操作"""
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, AppointmentNote):
                if not instance.staff_id:
                    instance.staff = request.user
            instance.save()
        formset.save_m2m()

@admin.register(AppointmentNote)
class AppointmentNoteAdmin(admin.ModelAdmin):
    """预约备注管理"""
    list_display = (
        'appointment', 
        'staff', 
        'note', 
        'created_at'
    )
    list_filter = (
        'staff', 
        'created_at'
    )
    search_fields = (
        'appointment__customer__username',
        'staff__username',
        'note'
    )
    readonly_fields = ('created_at',)

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.staff == request.user

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.staff == request.user
# appointments/utils.py

from datetime import datetime, timedelta
from django.utils import timezone
from business_hours.models import BusinessHours
from holidays.models import Holiday

class AppointmentStatus:
    PENDING = 'pending'      # 待确认
    CONFIRMED = 'confirmed'  # 已确认
    COMPLETED = 'completed'  # 已完成
    CANCELLED = 'cancelled'  # 已取消
    
    CHOICES = [
        (PENDING, '待确认'),
        (CONFIRMED, '已确认'),
        (COMPLETED, '已完成'),
        (CANCELLED, '已取消'),
    ]

def get_available_time_slots(date, service_duration):
    """获取指定日期的可用时间段"""
    # 检查是否是假期
    if Holiday.objects.filter(
        start_date__lte=date,
        end_date__gte=date
    ).exists():
        return []
    
    # 获取营业时间
    weekday = date.isoweekday()
    try:
        business_hours = BusinessHours.objects.get(weekday=weekday)
        if not business_hours.is_open:
            return []
    except BusinessHours.DoesNotExist:
        return []
    
    # 生成时间段
    slots = []
    current_time = datetime.combine(date, business_hours.start_time)
    end_time = datetime.combine(date, business_hours.end_time)
    
    while current_time + timedelta(minutes=service_duration) <= end_time:
        slots.append({
            'start_time': current_time.time(),
            'end_time': (current_time + timedelta(minutes=service_duration)).time()
        })
        current_time += timedelta(minutes=30)  # 30分钟为一个时间单位
    
    return slots

def is_valid_appointment_time(date, start_time, service_duration):
    """验证预约时间是否有效"""
    # 检查是否是过去的时间
    now = timezone.now()
    appointment_datetime = datetime.combine(date, start_time)
    if appointment_datetime < now:
        return False, "不能预约过去的时间"
    
    # 检查是否是假期
    if Holiday.objects.filter(
        start_date__lte=date,
        end_date__gte=date
    ).exists():
        return False, "该日期为假期，不接受预约"
    
    # 检查是否在营业时间内
    weekday = date.isoweekday()
    try:
        business_hours = BusinessHours.objects.get(weekday=weekday)
        if not business_hours.is_open:
            return False, "该日期不营业"
            
        end_time = (datetime.combine(date, start_time) + 
                   timedelta(minutes=service_duration)).time()
        
        if (start_time < business_hours.start_time or 
            end_time > business_hours.end_time):
            return False, "预约时间超出营业时间范围"
    except BusinessHours.DoesNotExist:
        return False, "该日期没有设置营业时间"
    
    return True, "预约时间有效"
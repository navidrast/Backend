from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from services.models import Service
from pets.models import Pet
from .utils import AppointmentStatus, is_valid_appointment_time
import uuid

class Appointment(models.Model):
    """预约模型"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('Customer')
    )
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('Pet')
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='appointments',
        verbose_name=_('Service')
    )
    date = models.DateField(_('Date'))
    start_time = models.TimeField(_('Start Time'))
    end_time = models.TimeField(_('End Time'))
    status = models.CharField(
        _('Status'),
        max_length=10,
        choices=AppointmentStatus.CHOICES,
        default=AppointmentStatus.PENDING
    )
    total_price = models.DecimalField(
        _('Total Price'),
        max_digits=10,
        decimal_places=2
    )
    customer_notes = models.TextField(_('Notes'), blank=True)
    
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Appointment')
        verbose_name_plural = _('Appointments')
        ordering = ['-date', '-start_time']
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'start_time', 'end_time'],
                condition=~models.Q(status=AppointmentStatus.CANCELLED),
                name='unique_appointment_time'
            )
        ]

    def __str__(self):
        return f"{self.customer.username} - {self.pet.name} - {self.service.name}"

    def clean(self):
        if self.status != AppointmentStatus.CANCELLED:
            is_valid, message = is_valid_appointment_time(
                self.date, 
                self.start_time, 
                self.service.duration
            )
            if not is_valid:
                raise ValidationError(message)

    def can_cancel(self, user):
        """
        检查用户是否可以取消预约
        
        Args:
            user: 尝试取消预约的用户
            
        Returns:
            tuple: (是否可以取消, 提示消息)
        """
        # 检查预约状态
        if self.status not in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]:
            return False, "Can only cancel pending or confirmed appointments"
            
        # 检查权限
        if not user.is_staff and self.customer != user:
            return False, "No permission to cancel this appointment"
            
        # 检查是否是过去的预约
        appointment_time = timezone.make_aware(
            datetime.combine(self.date, self.start_time),
            timezone.get_current_timezone()
        )
        if appointment_time < timezone.now():
            return False, "Cannot cancel past appointments"
            
        return True, "Appointment can be cancelled"
    
    def is_cancellation_within_24h(self):
        """
        检查当前是否在预约时间24小时内
        
        Returns:
            bool: 是否在24小时内
        """
        appointment_time = timezone.make_aware(
            datetime.combine(self.date, self.start_time),
            timezone.get_current_timezone()
        )
        time_diff = appointment_time - timezone.now()
        return time_diff.total_seconds() < 24 * 3600

class AppointmentNote(models.Model):
    """预约备注模型"""
    TYPE_CHOICES = [
        ('staff', 'Staff Note'),    # 工作人员备注
        ('customer', 'Customer Note')  # 客户备注
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('Appointment')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointment_notes',
        verbose_name=_('User')
    )
    note = models.TextField(_('Note Content'))
    note_type = models.CharField(
        _('Note Type'),
        max_length=10,
        choices=TYPE_CHOICES,
        default='customer'
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Appointment Note')
        verbose_name_plural = _('Appointment Notes')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.appointment} - {self.note_type} - {self.created_at}"

    def clean(self):
        """验证备注类型和用户身份是否匹配"""
        if self.note_type == 'staff' and not self.user.is_staff:
            raise ValidationError("Only staff can add staff notes")
        if self.note_type == 'customer' and self.user.is_staff:
            raise ValidationError("Staff should use staff notes")
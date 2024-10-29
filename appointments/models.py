# appointments/models.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
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
        verbose_name=_('客户')
    )
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('宠物')
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='appointments',
        verbose_name=_('服务项目')
    )
    date = models.DateField(_('预约日期'))
    start_time = models.TimeField(_('开始时间'))
    end_time = models.TimeField(_('结束时间'))
    status = models.CharField(
        _('状态'),
        max_length=10,
        choices=AppointmentStatus.CHOICES,
        default=AppointmentStatus.PENDING
    )
    total_price = models.DecimalField(
        _('总价'),
        max_digits=10,
        decimal_places=2
    )
    notes = models.TextField(_('备注'), blank=True)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('预约')
        verbose_name_plural = _('预约')
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

class AppointmentNote(models.Model):
    """预约备注模型（用于工作人员添加备注）"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='staff_notes',
        verbose_name=_('预约')
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointment_notes',
        verbose_name=_('工作人员')
    )
    note = models.TextField(_('备注内容'))
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)

    class Meta:
        verbose_name = _('预约备注')
        verbose_name_plural = _('预约备注')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.appointment} - {self.created_at}"
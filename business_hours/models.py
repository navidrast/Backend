# business_hours/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class BusinessHours(models.Model):
    """营业时间模型"""
    WEEKDAY_CHOICES = [
        (1, '星期一'),
        (2, '星期二'),
        (3, '星期三'),
        (4, '星期四'),
        (5, '星期五'),
        (6, '星期六'),
        (7, '星期日'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    weekday = models.IntegerField(
        _('星期'),
        choices=WEEKDAY_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        unique=True
    )
    start_time = models.TimeField(_('开始时间'))
    end_time = models.TimeField(_('结束时间'))
    is_open = models.BooleanField(_('是否营业'), default=True)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('营业时间')
        verbose_name_plural = _('营业时间')
        ordering = ['weekday']

    def __str__(self):
        return f"{self.get_weekday_display()} {self.start_time} - {self.end_time}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time >= self.end_time:
            raise ValidationError(_('开始时间必须早于结束时间'))
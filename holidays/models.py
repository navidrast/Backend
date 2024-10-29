# holidays/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class Holiday(models.Model):
    """假期模型"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(_('假期名称'), max_length=100)
    start_date = models.DateField(_('开始日期'))
    end_date = models.DateField(_('结束日期'))
    description = models.TextField(_('描述'), blank=True)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('假期')
        verbose_name_plural = _('假期')
        ordering = ['start_date']

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date > self.end_date:
            raise ValidationError(_('开始日期必须早于或等于结束日期'))
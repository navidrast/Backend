# services/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
import uuid

class DogSize(models.TextChoices):
    """狗狗体型枚举"""
    SMALL = 'S', _('小型犬 (8kg以下)')
    MEDIUM = 'M', _('中型犬 (8-15kg)')
    LARGE = 'L', _('大型犬 (16-25kg)')

class Service(models.Model):
    """服务项目模型"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(_('服务名称'), max_length=100)
    description = models.TextField(_('服务描述'))
    duration = models.PositiveIntegerField(
        _('服务时长'),
        help_text=_('以分钟为单位'),
        validators=[MinValueValidator(1)]
    )
    image = models.ImageField(
        _('服务图片'), 
        upload_to='services/',
        null=True,
        blank=True
    )
    is_active = models.BooleanField(_('是否启用'), default=True)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('服务项目')
        verbose_name_plural = _('服务项目')
        ordering = ['name']

    def __str__(self):
        return self.name

class ServicePrice(models.Model):
    """服务价格模型"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='prices',
        verbose_name=_('服务项目')
    )
    dog_size = models.CharField(
        _('狗狗体型'),
        max_length=1,
        choices=DogSize.choices
    )
    price = models.DecimalField(
        _('价格'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('服务价格')
        verbose_name_plural = _('服务价格')
        unique_together = ['service', 'dog_size']
        ordering = ['service', 'dog_size']

    def __str__(self):
        return f"{self.service.name} - {self.get_dog_size_display()}: ${self.price}"
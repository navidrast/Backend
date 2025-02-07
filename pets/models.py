# pets/models.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from services.models import DogSize
import uuid

class Pet(models.Model):
    """宠物模型"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pets',
        verbose_name=_('主人')
    )
    name = models.CharField(_('宠物名称'), max_length=50)
    breed = models.CharField(_('品种'), max_length=50, blank=True)
    weight = models.DecimalField(
        _('体重(kg)'),
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0.1),
            MaxValueValidator(100)
        ]
    )
    birthday = models.DateField(_('出生日期'), null=True, blank=True)
    gender = models.CharField(
        _('性别'),
        max_length=1,
        choices=[
            ('M', '公'),
            ('F', '母')
        ]
    )
    is_sterilized = models.BooleanField(_('是否绝育'), default=False)
    notes = models.TextField(_('备注'), blank=True)
    photo = models.ImageField(
        _('照片'),
        upload_to='pets/',
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('宠物')
        verbose_name_plural = _('宠物')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_size_display()})"

    @property
    def size(self):
        """根据体重自动计算体型"""
        weight = float(self.weight)
        if weight <= 8:
            return DogSize.SMALL
        elif weight <= 15:
            return DogSize.MEDIUM
        else:
            return DogSize.LARGE

    def get_size_display(self):
        """获取体型显示名称"""
        return dict(DogSize.choices)[self.size]

class PetHealthRecord(models.Model):
    """宠物健康记录"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name='health_records',
        verbose_name=_('宠物')
    )
    date = models.DateField(_('记录日期'))
    title = models.CharField(_('标题'), max_length=100)
    description = models.TextField(_('详细描述'))
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)

    class Meta:
        verbose_name = _('健康记录')
        verbose_name_plural = _('健康记录')
        ordering = ['-date']

    def __str__(self):
        return f"{self.pet.name} - {self.title} ({self.date})"
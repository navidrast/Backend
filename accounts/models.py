# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
import uuid

class CustomUserManager(BaseUserManager):
    """自定义用户管理器"""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('用户必须有邮箱地址')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级用户必须设置 is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级用户必须设置 is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)

class Customer(AbstractUser):
    """客户模型"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    username = models.CharField(
        _('用户名'),
        max_length=150,
        unique=True,
        help_text=_('必填。150个字符或更少。只能包含字母、数字和 @/./+/-/_ '),
        validators=[AbstractUser.username_validator],
        error_messages={
            'unique': _("该用户名已被使用。"),
        },
    )
    email = models.EmailField(_('邮箱地址'), unique=True)
    phone = models.CharField(_('手机号'), max_length=15, blank=True)
    address = models.CharField(_('地址'), max_length=255, blank=True)
    avatar = models.ImageField(_('头像'), upload_to='avatars/', null=True, blank=True)
    
    # 状态字段
    is_active = models.BooleanField(
        _('账户状态'),
        default=True,
        help_text=_('指示用户是否应被视为活动用户。'),
    )
    
    # 时间字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('客户')
        verbose_name_plural = _('客户')
        ordering = ['-created_at']

    def __str__(self):
        return self.username
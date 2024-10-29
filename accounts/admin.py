# accounts/admin.py

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

Customer = get_user_model()

@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_staff', 'created_at')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('个人信息', {'fields': ('phone', 'address', 'avatar')}),
        ('权限', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 
                      'user_permissions'),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
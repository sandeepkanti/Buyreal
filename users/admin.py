"""
Admin configuration for users app
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin with enhanced features
    """
    list_display = ['username', 'email', 'full_name', 'role_badge', 'phone', 'city', 'is_active', 'date_joined']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active', 'city']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']
    list_per_page = 25
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone', 'address', 'city', 'state', 'pincode', 
                      'latitude', 'longitude', 'profile_picture'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone', 'email', 'first_name', 'last_name')
        }),
    )
    
    def full_name(self, obj):
        return obj.get_full_name() or '-'
    full_name.short_description = 'Name'
    
    def role_badge(self, obj):
        colors = {
            'customer': '#28a745',
            'retailer': '#ffc107',
        }
        if obj.is_superuser:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Admin</span>'
            )
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            'black' if obj.role == 'retailer' else 'white',
            obj.get_role_display()
        )
    role_badge.short_description = 'Role'
    
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} users activated.')
    make_active.short_description = "Activate selected users"
    
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} users deactivated.')
    make_inactive.short_description = "Deactivate selected users"
"""
Admin configuration for shops app
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Shop, ShopTiming


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_display', 'shop_count', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    list_editable = ['is_active']
    
    def icon_display(self, obj):
        if obj.icon:
            return format_html('<i class="{}"></i> {}', obj.icon, obj.icon)
        return '-'
    icon_display.short_description = 'Icon'
    
    def shop_count(self, obj):
        return obj.shops.count()
    shop_count.short_description = 'Shops'


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'city', 'category', 'status_badge', 'product_count', 
                   'order_count', 'rating_display', 'created_at']
    list_filter = ['status', 'category', 'city', 'offers_delivery', 'created_at']
    search_fields = ['name', 'owner__username', 'city', 'email']
    readonly_fields = ['created_at', 'updated_at', 'rating', 'total_reviews']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('owner', 'name', 'description', 'category', 'image')
        }),
        ('Contact', {
            'fields': ('email', 'phone')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'pincode', 'latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Business Settings', {
            'fields': ('gst_number', 'offers_delivery', 'delivery_radius', 'minimum_order')
        }),
        ('Status & Approval', {
            'fields': ('status', 'rejection_reason')
        }),
        ('Statistics', {
            'fields': ('rating', 'total_reviews'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545',
            'suspended': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        text_color = 'black' if obj.status == 'pending' else 'white'
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, text_color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def product_count(self, obj):
        count = obj.products.count()
        return format_html('<a href="/admin/products/product/?shop__id={}">📦 {}</a>', obj.id, count)
    product_count.short_description = 'Products'
    
    def order_count(self, obj):
        count = obj.orders.count()
        return format_html('<a href="/admin/orders/order/?shop__id={}">🛒 {}</a>', obj.id, count)
    order_count.short_description = 'Orders'
    
    def rating_display(self, obj):
        if obj.rating > 0:
            stars = '⭐' * int(obj.rating)
            return f'{stars} ({obj.rating})'
        return '-'
    rating_display.short_description = 'Rating'
    
    actions = ['approve_shops', 'reject_shops', 'suspend_shops']
    
    def approve_shops(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f'{queryset.count()} shops approved.')
    approve_shops.short_description = "✅ Approve selected shops"
    
    def reject_shops(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f'{queryset.count()} shops rejected.')
    reject_shops.short_description = "❌ Reject selected shops"
    
    def suspend_shops(self, request, queryset):
        queryset.update(status='suspended')
        self.message_user(request, f'{queryset.count()} shops suspended.')
    suspend_shops.short_description = "⚠️ Suspend selected shops"


@admin.register(ShopTiming)
class ShopTimingAdmin(admin.ModelAdmin):
    list_display = ['shop', 'day', 'opening_time', 'closing_time', 'is_closed']
    list_filter = ['day', 'is_closed', 'shop']
    list_editable = ['opening_time', 'closing_time', 'is_closed']
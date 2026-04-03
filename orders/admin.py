"""
Admin configuration for orders app
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Cart, CartItem, Order, OrderItem, OrderStatusHistory


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'subtotal_display', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    inlines = [CartItemInline]
    
    def subtotal_display(self, obj):
        return f'₹{obj.subtotal}'
    subtotal_display.short_description = 'Subtotal'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_price', 'total_price']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['status', 'note', 'created_by', 'created_at']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'shop', 'total_display', 'status_badge', 
                   'payment_badge', 'delivery_type', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method', 'delivery_type', 'created_at']
    search_fields = ['order_number', 'customer__username', 'shop__name', 'delivery_phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'confirmed_at', 
                      'shipped_at', 'delivered_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'customer', 'shop', 'status')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_status', 'transaction_id')
        }),
        ('Delivery', {
            'fields': ('delivery_type', 'delivery_address', 'delivery_city', 
                      'delivery_state', 'delivery_pincode', 'delivery_phone')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'delivery_charge', 'discount', 'tax', 'total')
        }),
        ('Notes', {
            'fields': ('customer_note', 'retailer_note'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_display(self, obj):
        return format_html('<strong>₹{}</strong>', obj.total)
    total_display.short_description = 'Total'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'confirmed': '#17a2b8',
            'processing': '#6f42c1',
            'shipped': '#007bff',
            'out_for_delivery': '#fd7e14',
            'delivered': '#28a745',
            'cancelled': '#dc3545',
            'refunded': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        text_color = 'black' if obj.status == 'pending' else 'white'
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, text_color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_badge(self, obj):
        if obj.payment_status == 'paid':
            return format_html('<span style="color: green;">✅ Paid</span>')
        elif obj.payment_status == 'failed':
            return format_html('<span style="color: red;">❌ Failed</span>')
        elif obj.payment_status == 'refunded':
            return format_html('<span style="color: blue;">↩️ Refunded</span>')
        return format_html('<span style="color: orange;">⏳ Pending</span>')
    payment_badge.short_description = 'Payment'
    
    actions = ['mark_confirmed', 'mark_shipped', 'mark_delivered', 'mark_cancelled']
    
    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f'{queryset.count()} orders confirmed.')
    mark_confirmed.short_description = "✅ Mark as Confirmed"
    
    def mark_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, f'{queryset.count()} orders marked as shipped.')
    mark_shipped.short_description = "📦 Mark as Shipped"
    
    def mark_delivered(self, request, queryset):
        queryset.update(status='delivered', payment_status='paid')
        self.message_user(request, f'{queryset.count()} orders marked as delivered.')
    mark_delivered.short_description = "✅ Mark as Delivered"
    
    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f'{queryset.count()} orders cancelled.')
    mark_cancelled.short_description = "❌ Cancel orders"
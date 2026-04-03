"""
Admin configuration for products app
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ProductCategory, Product, ProductImage


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'product_count', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    list_editable = ['is_active']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'name', 'shop', 'price_display', 'stock_display', 
                   'availability_badge', 'is_featured', 'created_at']
    list_filter = ['is_available', 'is_featured', 'category', 'shop', 'created_at']
    search_fields = ['name', 'sku', 'shop__name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large']
    list_editable = ['is_featured']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('shop', 'name', 'description', 'category')
        }),
        ('Media', {
            'fields': ('image', 'image_preview_large')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price')
        }),
        ('Inventory', {
            'fields': ('stock', 'low_stock_threshold', 'sku', 'barcode', 'weight')
        }),
        ('Status', {
            'fields': ('is_available', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;"/>',
                obj.image.url
            )
        return format_html(
            '<div style="width: 50px; height: 50px; background: #eee; border-radius: 5px; display: flex; align-items: center; justify-content: center;">📷</div>'
        )
    image_preview.short_description = 'Image'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 10px;"/>',
                obj.image.url
            )
        return 'No image'
    image_preview_large.short_description = 'Image Preview'
    
    def price_display(self, obj):
        if obj.compare_price and obj.compare_price > obj.price:
            return format_html(
                '₹{} <del style="color: #999;">₹{}</del> <span style="color: green;">(-{}%)</span>',
                obj.price, obj.compare_price, obj.discount_percentage
            )
        return f'₹{obj.price}'
    price_display.short_description = 'Price'
    
    def stock_display(self, obj):
        if obj.stock == 0:
            return format_html('<span style="color: red;">Out of Stock</span>')
        elif obj.is_low_stock:
            return format_html('<span style="color: orange;">⚠️ {} (Low)</span>', obj.stock)
        return obj.stock
    stock_display.short_description = 'Stock'
    
    def availability_badge(self, obj):
        if obj.is_available and obj.stock > 0:
            return format_html('<span style="color: green;">✅ Available</span>')
        return format_html('<span style="color: red;">❌ Unavailable</span>')
    availability_badge.short_description = 'Status'
    
    actions = ['make_available', 'make_unavailable', 'feature_products', 'unfeature_products']
    
    def make_available(self, request, queryset):
        queryset.update(is_available=True)
        self.message_user(request, f'{queryset.count()} products made available.')
    make_available.short_description = "✅ Make available"
    
    def make_unavailable(self, request, queryset):
        queryset.update(is_available=False)
        self.message_user(request, f'{queryset.count()} products made unavailable.')
    make_unavailable.short_description = "❌ Make unavailable"
    
    def feature_products(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} products featured.')
    feature_products.short_description = "⭐ Feature selected"
    
    def unfeature_products(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f'{queryset.count()} products unfeatured.')
    unfeature_products.short_description = "Remove from featured"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'product', 'is_primary', 'order']
    list_filter = ['is_primary']
    list_editable = ['is_primary', 'order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;"/>',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Preview'
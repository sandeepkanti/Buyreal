"""
Shop Models for BuyReal
Handles shop creation, management, and approval system
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import math


class Category(models.Model):
    """
    Shop categories (Electronics, Grocery, Clothing, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Bootstrap icon class, e.g., 'bi-laptop'"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Shop(models.Model):
    """
    Shop Model - Represents a retailer's shop
    """
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    )
    
    # Shop owner
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shop'
    )
    
    # Basic information
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shops'
    )
    
    # Contact information
    email = models.EmailField()
    phone = models.CharField(max_length=17)
    
    # Address & Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    
    # Shop image
    image = models.ImageField(upload_to='shop_images/', blank=True, null=True)
    
    # Business details
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Shop status
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Delivery options
    offers_delivery = models.BooleanField(default=True)
    delivery_radius = models.PositiveIntegerField(
        default=10,
        help_text="Delivery radius in kilometers"
    )
    minimum_order = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Minimum order amount for delivery"
    )
    
    # Ratings
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.city})"
    
    @property
    def is_approved(self):
        return self.status == 'approved'
    
    @property
    def full_address(self):
        """Return complete address"""
        return f"{self.address}, {self.city}, {self.state} - {self.pincode}"
    
    def calculate_distance(self, user_lat, user_lng):
        """
        Calculate distance between shop and user using Haversine formula
        Returns distance in kilometers
        """
        if not self.latitude or not self.longitude:
            return None
        if not user_lat or not user_lng:
            return None
        
        try:
            R = 6371  # Earth's radius in kilometers
            
            lat1 = math.radians(float(self.latitude))
            lat2 = math.radians(float(user_lat))
            delta_lat = math.radians(float(user_lat) - float(self.latitude))
            delta_lng = math.radians(float(user_lng) - float(self.longitude))
            
            a = math.sin(delta_lat / 2) ** 2 + \
                math.cos(lat1) * math.cos(lat2) * math.sin(delta_lng / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            
            distance = R * c
            return round(distance, 2)
        except (ValueError, TypeError):
            return None
    
    def is_within_delivery_range(self, user_lat, user_lng):
        """Check if user is within delivery range"""
        distance = self.calculate_distance(user_lat, user_lng)
        if distance is None:
            return False
        return distance <= self.delivery_radius


class ShopTiming(models.Model):
    """
    Shop operating hours
    """
    DAYS = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='timings')
    day = models.IntegerField(choices=DAYS)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_closed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['shop', 'day']
        ordering = ['day']
    
    def __str__(self):
        if self.is_closed:
            return f"{self.shop.name} - {self.get_day_display()}: Closed"
        return f"{self.shop.name} - {self.get_day_display()}: {self.opening_time} - {self.closing_time}"
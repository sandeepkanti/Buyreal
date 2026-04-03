"""
User Models for BuyReal
Handles custom user with roles: Customer, Retailer, Admin
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Phone number validator
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)


class CustomUser(AbstractUser):
    """
    Custom User Model with role-based access
    """
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('retailer', 'Retailer'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    
    # Location for distance calculation
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # Profile picture
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_customer(self):
        return self.role == 'customer'
    
    @property
    def is_retailer(self):
        return self.role == 'retailer'
    
    @property
    def full_address(self):
        """Return complete address"""
        parts = [self.address, self.city, self.state, self.pincode]
        return ', '.join(filter(None, parts))
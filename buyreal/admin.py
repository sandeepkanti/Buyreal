"""
Custom Admin Site Configuration for BuyReal
"""

from django.contrib import admin
from django.contrib.admin import AdminSite


class BuyRealAdminSite(AdminSite):
    """
    Custom Admin Site for BuyReal
    """
    site_header = 'BuyReal Administration'
    site_title = 'BuyReal Admin'
    index_title = 'Welcome to BuyReal Admin Panel'


# Create instance of custom admin site
buyreal_admin = BuyRealAdminSite(name='buyreal_admin')
"""
URL patterns for users app
"""

from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'users'

urlpatterns = [
    # Registration
    path('register/', views.register_customer, name='register'),
    path('register/retailer/', views.register_retailer, name='register_retailer'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
    path('admin/shops/', views.admin_shops, name='admin_shops'),
    path('admin/shops/<int:shop_id>/approve/', views.admin_approve_shop, name='admin_approve_shop'),
    path('admin/shops/<int:shop_id>/reject/', views.admin_reject_shop, name='admin_reject_shop'),
    path('admin/shops/<int:shop_id>/delete/', views.admin_delete_shop, name='admin_delete_shop'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
]
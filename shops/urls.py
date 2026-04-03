"""
URL patterns for shops app
"""

from django.urls import path
from . import views

app_name = 'shops'

urlpatterns = [
    # Public views
    path('', views.shop_list, name='shop_list'),
    path('<int:shop_id>/', views.shop_detail, name='shop_detail'),
    
    # Retailer views
    path('dashboard/', views.retailer_dashboard, name='retailer_dashboard'),
    path('create/', views.create_shop, name='create_shop'),
    path('my-shop/', views.my_shop, name='my_shop'),
]
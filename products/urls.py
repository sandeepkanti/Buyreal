"""
URL patterns for products app
"""

from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Public views
    path('', views.product_list, name='product_list'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    
    # Retailer views
    path('my-products/', views.my_products, name='my_products'),
    path('add/', views.add_product, name='add_product'),
    path('<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('<int:product_id>/toggle/', views.toggle_product_availability, name='toggle_availability'),
]
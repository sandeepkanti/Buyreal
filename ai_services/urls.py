"""
URL patterns for AI services
"""

from django.urls import path
from . import views

app_name = 'ai_services'

urlpatterns = [
    # Recommendations
    path('recommendations/', views.product_recommendations, name='recommendations'),
    path('recommendations/<int:product_id>/', views.product_recommendations, name='product_recommendations'),
    
    # Smart Search
    path('search/', views.smart_search_api, name='smart_search'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    
    # Chatbot
    path('chatbot/', views.chatbot_page, name='chatbot_page'),
    path('chatbot/api/', views.chatbot_api, name='chatbot_api'),
    
    # Status/Debug
    path('status/', views.ai_status, name='ai_status'),
    path('models/', views.list_available_models, name='list_models'),
]
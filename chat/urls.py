"""
URL patterns for chat app
"""

from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.conversations, name='conversations'),
    path('start/<int:shop_id>/', views.start_chat, name='start_chat'),
    path('room/<int:conversation_id>/', views.chat_room, name='chat_room'),
    path('send/<int:conversation_id>/', views.send_message, name='send_message'),
    path('messages/<int:conversation_id>/', views.get_messages, name='get_messages'),
    path('delete/<int:conversation_id>/', views.delete_conversation, name='delete_conversation'),
]
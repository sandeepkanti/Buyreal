"""
Chat Models for BuyReal
Handles messaging between customers and retailers
"""

from django.db import models
from django.conf import settings
from shops.models import Shop


class Conversation(models.Model):
    """
    Conversation between customer and shop owner
    """
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_conversations'
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Track if there are unread messages
    customer_unread = models.PositiveIntegerField(default=0)
    retailer_unread = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['customer', 'shop']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat: {self.customer.username} - {self.shop.name}"
    
    @property
    def last_message(self):
        """Get the last message in conversation"""
        return self.messages.order_by('-created_at').first()


class Message(models.Model):
    """
    Individual messages in a conversation
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"
    
    @property
    def is_from_customer(self):
        """Check if message is from customer"""
        return self.sender == self.conversation.customer
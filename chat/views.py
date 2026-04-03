"""
Chat Views for BuyReal
Handles messaging between customers and retailers
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Conversation, Message
from shops.models import Shop


@login_required
def conversations(request):
    """
    List all conversations for the user
    """
    if request.user.role == 'customer':
        convos = Conversation.objects.filter(customer=request.user).select_related('shop')
    elif request.user.role == 'retailer':
        try:
            shop = request.user.shop
            convos = Conversation.objects.filter(shop=shop).select_related('customer')
        except Shop.DoesNotExist:
            convos = Conversation.objects.none()
    else:
        convos = Conversation.objects.none()
    
    return render(request, 'chat/conversations.html', {'conversations': convos})


@login_required
def start_chat(request, shop_id):
    """
    Start or continue a chat with a shop
    """
    if request.user.role != 'customer':
        messages.error(request, 'Only customers can start chats.')
        return redirect('home')
    
    shop = get_object_or_404(Shop, id=shop_id, status='approved')
    
    # Get or create conversation
    conversation, created = Conversation.objects.get_or_create(
        customer=request.user,
        shop=shop
    )
    
    return redirect('chat:chat_room', conversation_id=conversation.id)


@login_required
def chat_room(request, conversation_id):
    """
    Chat room view
    """
    # Get conversation based on user role
    if request.user.role == 'customer':
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            customer=request.user
        )
        # Mark retailer messages as read
        conversation.messages.filter(is_read=False).exclude(
            sender=request.user
        ).update(is_read=True)
        conversation.customer_unread = 0
        conversation.save()
        other_party = conversation.shop.name
    elif request.user.role == 'retailer':
        try:
            shop = request.user.shop
            conversation = get_object_or_404(
                Conversation, 
                id=conversation_id, 
                shop=shop
            )
            # Mark customer messages as read
            conversation.messages.filter(is_read=False).exclude(
                sender=request.user
            ).update(is_read=True)
            conversation.retailer_unread = 0
            conversation.save()
            other_party = conversation.customer.get_full_name() or conversation.customer.username
        except Shop.DoesNotExist:
            messages.error(request, 'Shop not found.')
            return redirect('home')
    else:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get all messages
    chat_messages = conversation.messages.all().order_by('created_at')
    
    return render(request, 'chat/chat_room.html', {
        'conversation': conversation,
        'messages': chat_messages,
        'other_party': other_party
    })


@login_required
@require_POST
def send_message(request, conversation_id):
    """
    Send a message in a conversation
    """
    content = request.POST.get('content', '').strip()
    
    if not content:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Message cannot be empty'})
        messages.error(request, 'Message cannot be empty.')
        return redirect('chat:chat_room', conversation_id=conversation_id)
    
    # Get conversation based on user role
    if request.user.role == 'customer':
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            customer=request.user
        )
        # Increment retailer unread count
        conversation.retailer_unread += 1
    elif request.user.role == 'retailer':
        try:
            shop = request.user.shop
            conversation = get_object_or_404(
                Conversation, 
                id=conversation_id, 
                shop=shop
            )
            # Increment customer unread count
            conversation.customer_unread += 1
        except Shop.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Shop not found'})
            messages.error(request, 'Shop not found.')
            return redirect('home')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Access denied'})
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Create message
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content
    )
    
    # Update conversation timestamp
    conversation.save()  # This updates the updated_at field
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'sender': request.user.username,
                'created_at': message.created_at.strftime('%H:%M'),
                'is_mine': True
            }
        })
    
    return redirect('chat:chat_room', conversation_id=conversation_id)


@login_required
def get_messages(request, conversation_id):
    """
    Get new messages (for AJAX polling)
    """
    last_id = request.GET.get('last_id', 0)
    
    # Get conversation based on user role
    if request.user.role == 'customer':
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            customer=request.user
        )
    elif request.user.role == 'retailer':
        try:
            shop = request.user.shop
            conversation = get_object_or_404(
                Conversation, 
                id=conversation_id, 
                shop=shop
            )
        except Shop.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Shop not found'})
    else:
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    # Get new messages
    new_messages = conversation.messages.filter(id__gt=last_id).order_by('created_at')
    
    # Mark as read
    new_messages.exclude(sender=request.user).update(is_read=True)
    
    messages_data = []
    for msg in new_messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'sender': msg.sender.username,
            'created_at': msg.created_at.strftime('%H:%M'),
            'is_mine': msg.sender == request.user
        })
    
    return JsonResponse({
        'success': True,
        'messages': messages_data
    })


@login_required
def delete_conversation(request, conversation_id):
    """
    Delete a conversation
    """
    if request.user.role == 'customer':
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            customer=request.user
        )
    elif request.user.role == 'retailer':
        try:
            shop = request.user.shop
            conversation = get_object_or_404(
                Conversation, 
                id=conversation_id, 
                shop=shop
            )
        except Shop.DoesNotExist:
            messages.error(request, 'Shop not found.')
            return redirect('home')
    else:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    conversation.delete()
    messages.success(request, 'Conversation deleted.')
    return redirect('chat:conversations')
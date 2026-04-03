"""
Order Views for BuyReal
Handles cart and order operations
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal

from .models import Cart, CartItem, Order, OrderItem, OrderStatusHistory
from .forms import CheckoutForm, OrderStatusForm
from products.models import Product
from shops.models import Shop


@login_required
def cart(request):
    """
    View shopping cart
    """
    if request.user.role != 'customer':
        messages.error(request, 'Only customers can access the cart.')
        return redirect('home')
    
    # Get or create cart
    cart_obj, created = Cart.objects.get_or_create(user=request.user)
    
    # Group items by shop
    cart_items = cart_obj.items.select_related('product__shop', 'product__category').all()
    shops_items = {}
    
    for item in cart_items:
        shop = item.product.shop
        if shop.id not in shops_items:
            shops_items[shop.id] = {
                'shop': shop,
                'items': [],
                'subtotal': Decimal('0.00')
            }
        shops_items[shop.id]['items'].append(item)
        shops_items[shop.id]['subtotal'] += item.total_price
    
    return render(request, 'orders/cart.html', {
        'cart': cart_obj,
        'shops_items': shops_items.values()
    })


@login_required
@require_POST
def add_to_cart(request, product_id):
    """
    Add product to cart
    """
    if request.user.role != 'customer':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Only customers can add items to cart.'})
        messages.error(request, 'Only customers can add items to cart.')
        return redirect('home')
    
    product = get_object_or_404(
        Product, 
        id=product_id, 
        is_available=True, 
        shop__status='approved'
    )
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1
    
    # Check stock
    if quantity > product.stock:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'message': f'Only {product.stock} items available in stock.'
            })
        messages.error(request, f'Only {product.stock} items available in stock.')
        return redirect('products:product_detail', product_id=product_id)
    
    # Get or create cart
    cart_obj, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if item already in cart
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart_obj,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not item_created:
        # Update quantity
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'message': f'Cannot add more. Only {product.stock} items available.'
                })
            messages.error(request, f'Cannot add more. Only {product.stock} items available.')
            return redirect('orders:cart')
        cart_item.quantity = new_quantity
        cart_item.save()
        msg = f'Updated {product.name} quantity in cart.'
    else:
        msg = f'Added {product.name} to cart.'
    
    # Check if AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': msg,
            'cart_count': cart_obj.total_items
        })
    
    messages.success(request, msg)
    return redirect('orders:cart')


@login_required
@require_POST
def update_cart_item(request, item_id):
    """
    Update cart item quantity
    """
    if request.user.role != 'customer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1
    
    if quantity > cart_item.product.stock:
        messages.error(request, f'Only {cart_item.product.stock} items available.')
    elif quantity < 1:
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated.')
    
    return redirect('orders:cart')


@login_required
def remove_from_cart(request, item_id):
    """
    Remove item from cart
    """
    if request.user.role != 'customer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'Removed {product_name} from cart.')
    return redirect('orders:cart')


@login_required
def checkout(request, shop_id):
    """
    Checkout for a specific shop
    """
    if request.user.role != 'customer':
        messages.error(request, 'Only customers can checkout.')
        return redirect('home')
    
    shop = get_object_or_404(Shop, id=shop_id, status='approved')
    
    try:
        cart_obj = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('orders:cart')
    
    # Get cart items for this shop
    cart_items = cart_obj.items.filter(product__shop=shop).select_related('product')
    
    if not cart_items.exists():
        messages.error(request, 'No items from this shop in your cart.')
        return redirect('orders:cart')
    
    # Verify stock availability
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(
                request, 
                f'"{item.product.name}" only has {item.product.stock} items in stock.'
            )
            return redirect('orders:cart')
    
    # Calculate totals
    subtotal = sum(item.total_price for item in cart_items)
    delivery_charge = Decimal('0.00') if subtotal >= shop.minimum_order else Decimal('40.00')
    total = subtotal + delivery_charge
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = Order.objects.create(
                customer=request.user,
                shop=shop,
                payment_method=form.cleaned_data['payment_method'],
                delivery_type=form.cleaned_data['delivery_type'],
                delivery_address=form.cleaned_data['delivery_address'],
                delivery_city=form.cleaned_data['delivery_city'],
                delivery_state=form.cleaned_data['delivery_state'],
                delivery_pincode=form.cleaned_data['delivery_pincode'],
                delivery_phone=form.cleaned_data['delivery_phone'],
                subtotal=subtotal,
                delivery_charge=delivery_charge,
                total=total,
                customer_note=form.cleaned_data.get('customer_note', '')
            )
            
            # Create order items and reduce stock
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity
                )
                # Reduce stock
                cart_item.product.reduce_stock(cart_item.quantity)
            
            # Clear these items from cart
            cart_items.delete()
            
            # Handle UPI payment (mock)
            if form.cleaned_data['payment_method'] == 'upi':
                order.transaction_id = f"UPI{order.order_number}"
                order.payment_status = 'paid'  # Mock payment success
                order.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status='pending',
                note='Order placed successfully',
                created_by=request.user
            )
            
            messages.success(request, f'Order #{order.order_number} placed successfully!')
            return redirect('orders:order_confirmation', order_id=order.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill with user's address
        initial_data = {
            'delivery_address': request.user.address or '',
            'delivery_city': request.user.city or '',
            'delivery_state': request.user.state or '',
            'delivery_pincode': request.user.pincode or '',
            'delivery_phone': request.user.phone or '',
        }
        form = CheckoutForm(initial=initial_data)
    
    return render(request, 'orders/checkout.html', {
        'form': form,
        'shop': shop,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'total': total
    })


@login_required
def order_confirmation(request, order_id):
    """
    Order confirmation page
    """
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'orders/order_confirmation.html', {'order': order})


@login_required
def order_history(request):
    """
    Customer's order history
    """
    if request.user.role != 'customer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    return render(request, 'orders/order_history.html', {
        'orders': orders,
        'status_filter': status_filter
    })


@login_required
def order_detail(request, order_id):
    """
    View order details
    """
    if request.user.role == 'customer':
        order = get_object_or_404(Order, id=order_id, customer=request.user)
    elif request.user.role == 'retailer':
        order = get_object_or_404(Order, id=order_id, shop__owner=request.user)
    elif request.user.is_superuser:
        order = get_object_or_404(Order, id=order_id)
    else:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    return render(request, 'orders/order_detail.html', {'order': order})


# Retailer Order Management
@login_required
def retailer_orders(request):
    """
    Retailer's order management
    """
    if request.user.role != 'retailer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        shop = request.user.shop
    except Shop.DoesNotExist:
        return redirect('shops:create_shop')
    
    orders = Order.objects.filter(shop=shop).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    return render(request, 'orders/retailer_orders.html', {
        'orders': orders,
        'shop': shop,
        'status_filter': status_filter
    })


@login_required
@require_POST
def update_order_status(request, order_id):
    """
    Update order status (retailer only)
    """
    if request.user.role != 'retailer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id, shop__owner=request.user)
    form = OrderStatusForm(request.POST)
    
    if form.is_valid():
        new_status = form.cleaned_data['status']
        note = form.cleaned_data.get('note', '')
        
        # Update order status
        order.status = new_status
        
        # Update timestamps
        if new_status == 'confirmed':
            order.confirmed_at = timezone.now()
        elif new_status == 'shipped':
            order.shipped_at = timezone.now()
        elif new_status == 'delivered':
            order.delivered_at = timezone.now()
            if order.payment_method == 'cod':
                order.payment_status = 'paid'
        
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            note=note,
            created_by=request.user
        )
        
        messages.success(
            request, 
            f'Order #{order.order_number} status updated to {order.get_status_display()}.'
        )
    else:
        messages.error(request, 'Invalid form data.')
    
    return redirect('orders:order_detail', order_id=order.id)


@login_required
def cancel_order(request, order_id):
    """
    Cancel an order
    """
    if request.user.role == 'customer':
        order = get_object_or_404(Order, id=order_id, customer=request.user)
    elif request.user.role == 'retailer':
        order = get_object_or_404(Order, id=order_id, shop__owner=request.user)
    else:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Can only cancel pending or confirmed orders
    if order.status not in ['pending', 'confirmed']:
        messages.error(request, 'This order cannot be cancelled.')
        return redirect('orders:order_detail', order_id=order.id)
    
    # Restore stock
    for item in order.items.all():
        if item.product:
            item.product.stock += item.quantity
            item.product.save()
    
    order.status = 'cancelled'
    order.save()
    
    OrderStatusHistory.objects.create(
        order=order,
        status='cancelled',
        note=f'Order cancelled by {request.user.username}',
        created_by=request.user
    )
    
    messages.success(request, f'Order #{order.order_number} has been cancelled.')
    
    if request.user.role == 'customer':
        return redirect('orders:order_history')
    return redirect('orders:retailer_orders')
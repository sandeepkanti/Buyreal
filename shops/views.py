"""
Shop Views for BuyReal
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal

from .models import Shop, Category
from .forms import ShopForm, ShopSearchForm
from products.models import Product
from orders.models import Order


def shop_list(request):
    """
    List all approved shops with filtering
    """
    shops = Shop.objects.filter(status='approved').select_related('category')
    form = ShopSearchForm(request.GET)
    
    # Get user location from request or session
    user_lat = request.GET.get('latitude') or request.session.get('user_lat')
    user_lng = request.GET.get('longitude') or request.session.get('user_lng')
    
    if user_lat and user_lng:
        try:
            request.session['user_lat'] = float(user_lat)
            request.session['user_lng'] = float(user_lng)
        except (ValueError, TypeError):
            user_lat = None
            user_lng = None
    
    # Apply filters
    city = request.GET.get('city', '').strip()
    category_id = request.GET.get('category', '')
    radius = request.GET.get('radius', '')
    
    if city:
        shops = shops.filter(city__icontains=city)
    
    if category_id:
        try:
            shops = shops.filter(category_id=int(category_id))
        except (ValueError, TypeError):
            pass
    
    # Calculate distance for each shop
    shops_with_distance = []
    for shop in shops:
        if user_lat and user_lng:
            try:
                distance = shop.calculate_distance(float(user_lat), float(user_lng))
                shop.distance = distance
                
                # Filter by radius if specified
                if radius:
                    try:
                        radius_km = int(radius)
                        if distance and distance <= radius_km:
                            shops_with_distance.append(shop)
                    except (ValueError, TypeError):
                        shops_with_distance.append(shop)
                else:
                    shops_with_distance.append(shop)
            except (ValueError, TypeError):
                shop.distance = None
                shops_with_distance.append(shop)
        else:
            shop.distance = None
            shops_with_distance.append(shop)
    
    # Sort by distance if available
    if user_lat and user_lng:
        shops_with_distance.sort(key=lambda x: x.distance if x.distance is not None else float('inf'))
    
    categories = Category.objects.filter(is_active=True)
    
    return render(request, 'shops/shop_list.html', {
        'shops': shops_with_distance,
        'form': form,
        'categories': categories,
        'city_filter': city,
        'category_filter': category_id,
        'user_lat': user_lat,
        'user_lng': user_lng
    })


def shop_detail(request, shop_id):
    """
    View shop details and products
    """
    shop = get_object_or_404(Shop.objects.select_related('category'), id=shop_id, status='approved')
    products = shop.products.filter(is_available=True).select_related('category')
    
    # Get user location for distance
    user_lat = request.session.get('user_lat')
    user_lng = request.session.get('user_lng')
    
    if user_lat and user_lng:
        try:
            shop.distance = shop.calculate_distance(float(user_lat), float(user_lng))
        except (ValueError, TypeError):
            shop.distance = None
    else:
        shop.distance = None
    
    # Filter products
    category = request.GET.get('category', '')
    search = request.GET.get('search', '').strip()
    
    if category:
        try:
            products = products.filter(category_id=int(category))
        except (ValueError, TypeError):
            pass
    
    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    # Get product categories for this shop
    product_categories = shop.products.filter(
        is_available=True, 
        category__isnull=False
    ).values_list('category__id', 'category__name').distinct()
    
    return render(request, 'shops/shop_detail.html', {
        'shop': shop,
        'products': products,
        'category_filter': category,
        'search_query': search,
        'product_categories': product_categories
    })


# Retailer Views
def is_retailer(user):
    """Check if user is a retailer"""
    return user.is_authenticated and user.role == 'retailer'


@login_required
def retailer_dashboard(request):
    """
    Retailer dashboard
    """
    if request.user.role != 'retailer':
        messages.error(request, 'Access denied. Retailer account required.')
        return redirect('home')
    
    # Check if retailer has a shop
    try:
        shop = request.user.shop
    except Shop.DoesNotExist:
        messages.info(request, 'Please create your shop first.')
        return redirect('shops:create_shop')
    
    # Get statistics
    total_products = shop.products.count()
    total_orders = shop.orders.count()
    pending_orders = shop.orders.filter(status='pending').count()
    recent_orders = shop.orders.order_by('-created_at')[:5]
    low_stock_products = shop.products.filter(
        stock__lte=5, 
        is_available=True
    ).order_by('stock')[:5]
    
    # Calculate revenue
    from django.db.models import Sum
    total_revenue = shop.orders.filter(
        status__in=['delivered', 'shipped']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    return render(request, 'shops/retailer_dashboard.html', {
        'shop': shop,
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'total_revenue': total_revenue
    })


@login_required
def create_shop(request):
    """
    Create a new shop (for retailers)
    """
    if request.user.role != 'retailer':
        messages.error(request, 'Only retailers can create shops.')
        return redirect('home')
    
    # Check if shop already exists
    try:
        if hasattr(request.user, 'shop') and request.user.shop:
            messages.info(request, 'You already have a shop.')
            return redirect('shops:my_shop')
    except Shop.DoesNotExist:
        pass
    
    # Check if categories exist
    categories_exist = Category.objects.filter(is_active=True).exists()
    if not categories_exist:
        messages.warning(request, 'No categories available. Please contact admin.')
    
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.owner = request.user
            shop.status = 'pending'
            shop.save()
            messages.success(request, 'Your shop has been created and is pending approval.')
            return redirect('shops:my_shop')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ShopForm()
    
    return render(request, 'shops/create_shop.html', {
        'form': form,
        'categories_exist': categories_exist
    })


@login_required
def my_shop(request):
    """
    View and edit retailer's shop
    """
    if request.user.role != 'retailer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        shop = request.user.shop
    except Shop.DoesNotExist:
        return redirect('shops:create_shop')
    
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shop details updated successfully.')
            return redirect('shops:my_shop')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ShopForm(instance=shop)
    
    return render(request, 'shops/my_shop.html', {
        'shop': shop,
        'form': form
    })
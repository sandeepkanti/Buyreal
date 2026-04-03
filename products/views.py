"""
Product Views for BuyReal
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import ValidationError

from .models import Product, ProductCategory
from .forms import ProductForm
from shops.models import Shop


def product_list(request):
    """
    List all available products from approved shops
    """
    products = Product.objects.filter(
        is_available=True,
        shop__status='approved'
    ).select_related('shop', 'category')
    
    # Filters
    search = request.GET.get('search', '').strip()
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    if search:
        products = products.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) |
            Q(shop__name__icontains=search)
        )
    
    if category:
        try:
            products = products.filter(category_id=int(category))
        except (ValueError, TypeError):
            pass
    
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except (ValueError, TypeError):
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except (ValueError, TypeError):
            pass
    
    categories = ProductCategory.objects.filter(is_active=True)
    
    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'search_query': search,
        'category_filter': category,
        'min_price': min_price,
        'max_price': max_price
    })


def product_detail(request, product_id):
    """
    View product details
    """
    product = get_object_or_404(
        Product.objects.select_related('shop', 'category'),
        id=product_id,
        is_available=True,
        shop__status='approved'
    )
    
    # Related products from same shop
    related_products = Product.objects.filter(
        shop=product.shop,
        is_available=True
    ).exclude(id=product.id).select_related('category')[:4]
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products
    })


# Retailer Product Management
@login_required
def my_products(request):
    """
    List retailer's products
    """
    if request.user.role != 'retailer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        shop = request.user.shop
    except Shop.DoesNotExist:
        messages.info(request, 'Please create your shop first.')
        return redirect('shops:create_shop')
    
    products = shop.products.all().select_related('category')
    
    # Filters
    search = request.GET.get('search', '').strip()
    availability = request.GET.get('availability', '')
    
    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(sku__icontains=search)
        )
    
    if availability == 'available':
        products = products.filter(is_available=True, stock__gt=0)
    elif availability == 'out_of_stock':
        products = products.filter(Q(is_available=False) | Q(stock=0))
    
    return render(request, 'products/my_products.html', {
        'products': products,
        'shop': shop,
        'search_query': search,
        'availability_filter': availability
    })


@login_required
def add_product(request):
    """
    Add a new product
    """
    if request.user.role != 'retailer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        shop = request.user.shop
    except Shop.DoesNotExist:
        messages.info(request, 'Please create your shop first.')
        return redirect('shops:create_shop')
    
    if shop.status != 'approved':
        messages.warning(request, 'Your shop must be approved before adding products.')
        return redirect('shops:my_shop')
    
    # Check if product categories exist
    categories_exist = ProductCategory.objects.filter(is_active=True).exists()
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                product = form.save(commit=False)
                product.shop = shop
                product.save()
                messages.success(request, f'Product "{product.name}" added successfully.')
                return redirect('products:my_products')
            except Exception as e:
                messages.error(request, f'Error saving product: {str(e)}')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm()
    
    return render(request, 'products/add_product.html', {
        'form': form,
        'shop': shop,
        'categories_exist': categories_exist
    })


@login_required
def edit_product(request, product_id):
    """
    Edit a product
    """
    if request.user.role != 'retailer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id, shop__owner=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Product "{product.name}" updated successfully.')
                return redirect('products:my_products')
            except Exception as e:
                messages.error(request, f'Error updating product: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/edit_product.html', {
        'form': form,
        'product': product
    })


@login_required
def delete_product(request, product_id):
    """
    Delete a product
    """
    if request.user.role != 'retailer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id, shop__owner=request.user)
    product_name = product.name
    
    try:
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting product: {str(e)}')
    
    return redirect('products:my_products')


@login_required
def toggle_product_availability(request, product_id):
    """
    Toggle product availability
    """
    if request.user.role != 'retailer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id, shop__owner=request.user)
    product.is_available = not product.is_available
    product.save()
    
    status = "available" if product.is_available else "unavailable"
    messages.success(request, f'Product "{product.name}" is now {status}.')
    return redirect('products:my_products')
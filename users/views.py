"""
User Views for BuyReal
Handles registration, login, profile, and admin functions
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone

from .forms import (
    CustomerRegistrationForm, 
    RetailerRegistrationForm, 
    CustomLoginForm,
    ProfileUpdateForm,
    CustomPasswordChangeForm
)
from .models import CustomUser
from shops.models import Shop
from orders.models import Order


def register_customer(request):
    """
    Customer registration view
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your account has been created successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'users/register.html', {
        'form': form,
        'user_type': 'customer'
    })


def register_retailer(request):
    """
    Retailer registration view
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RetailerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Please create your shop profile to get started.')
            return redirect('shops:create_shop')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RetailerRegistrationForm()
    
    return render(request, 'users/register.html', {
        'form': form,
        'user_type': 'retailer'
    })


class CustomLoginView(LoginView):
    """
    Custom login view
    """
    form_class = CustomLoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().first_name}!')
        return super().form_valid(form)
    
    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return '/users/admin-dashboard/'
        elif user.role == 'retailer':
            return '/shops/dashboard/'
        return '/'


class CustomLogoutView(LogoutView):
    """
    Custom logout view
    """
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


@login_required
def profile(request):
    """
    User profile view
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('users:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})


@login_required
def change_password(request):
    """
    Change password view
    """
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('users:profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})


# Admin Views
def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    Admin dashboard view
    """
    context = {
        'total_users': CustomUser.objects.count(),
        'total_customers': CustomUser.objects.filter(role='customer').count(),
        'total_retailers': CustomUser.objects.filter(role='retailer').count(),
        'total_shops': Shop.objects.count(),
        'pending_shops': Shop.objects.filter(status='pending').count(),
        'approved_shops': Shop.objects.filter(status='approved').count(),
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'recent_users': CustomUser.objects.order_by('-date_joined')[:5],
        'pending_shop_list': Shop.objects.filter(status='pending')[:5],
        'recent_orders': Order.objects.order_by('-created_at')[:5],
    }
    return render(request, 'users/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_users(request):
    """
    Admin view - list all users
    """
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'users/admin_users.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def admin_delete_user(request, user_id):
    """
    Admin view - delete a user
    """
    user = get_object_or_404(CustomUser, id=user_id)
    if user.is_superuser:
        messages.error(request, 'Cannot delete admin users.')
    else:
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" has been deleted.')
    return redirect('users:admin_users')


@login_required
@user_passes_test(is_admin)
def admin_shops(request):
    """
    Admin view - list all shops
    """
    status_filter = request.GET.get('status', '')
    shops = Shop.objects.all()
    
    if status_filter:
        shops = shops.filter(status=status_filter)
    
    return render(request, 'users/admin_shops.html', {
        'shops': shops,
        'status_filter': status_filter
    })


@login_required
@user_passes_test(is_admin)
def admin_approve_shop(request, shop_id):
    """
    Admin view - approve a shop
    """
    shop = get_object_or_404(Shop, id=shop_id)
    shop.status = 'approved'
    shop.save()
    messages.success(request, f'Shop "{shop.name}" has been approved.')
    return redirect('users:admin_shops')


@login_required
@user_passes_test(is_admin)
def admin_reject_shop(request, shop_id):
    """
    Admin view - reject a shop
    """
    shop = get_object_or_404(Shop, id=shop_id)
    reason = request.POST.get('reason', 'No reason provided')
    shop.status = 'rejected'
    shop.rejection_reason = reason
    shop.save()
    messages.success(request, f'Shop "{shop.name}" has been rejected.')
    return redirect('users:admin_shops')


@login_required
@user_passes_test(is_admin)
def admin_delete_shop(request, shop_id):
    """
    Admin view - delete a shop
    """
    shop = get_object_or_404(Shop, id=shop_id)
    shop_name = shop.name
    shop.delete()
    messages.success(request, f'Shop "{shop_name}" has been deleted.')
    return redirect('users:admin_shops')


@login_required
@user_passes_test(is_admin)
def admin_orders(request):
    """
    Admin view - list all orders
    """
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'users/admin_orders.html', {'orders': orders})
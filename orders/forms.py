"""
Order Forms for BuyReal
"""

from django import forms
from .models import Order


class CheckoutForm(forms.Form):
    """
    Checkout form for placing orders
    """
    PAYMENT_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('upi', 'UPI Payment'),
    )
    
    DELIVERY_CHOICES = (
        ('retailer', 'Retailer Delivery'),
        ('partner', 'Delivery Partner'),
        ('pickup', 'Self Pickup'),
    )
    
    # Delivery Address
    delivery_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Enter your delivery address'
        })
    )
    delivery_city = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    delivery_state = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State'
        })
    )
    delivery_pincode = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pincode'
        })
    )
    delivery_phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )
    
    # Payment & Delivery
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    delivery_type = forms.ChoiceField(
        choices=DELIVERY_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    # UPI ID (for UPI payment)
    upi_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'yourname@upi'
        })
    )
    
    # Customer note
    customer_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Any special instructions? (Optional)'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        upi_id = cleaned_data.get('upi_id')
        
        if payment_method == 'upi' and not upi_id:
            raise forms.ValidationError('Please enter your UPI ID for UPI payment.')
        
        return cleaned_data


class OrderStatusForm(forms.Form):
    """
    Form for updating order status (used by retailers)
    """
    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Add a note (optional)'
        })
    )
"""
Shop Forms for BuyReal
"""

from django import forms
from .models import Shop, Category


class ShopForm(forms.ModelForm):
    """
    Form for creating and updating shops
    """
    class Meta:
        model = Shop
        fields = [
            'name', 'description', 'category', 'email', 'phone',
            'address', 'city', 'state', 'pincode', 'latitude', 'longitude',
            'image', 'gst_number', 'offers_delivery', 'delivery_radius', 'minimum_order'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Shop Name',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Describe your shop...',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'shop@example.com',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+91 9876543210',
                'required': True
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Shop Address',
                'required': True
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'City',
                'required': True
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'State',
                'required': True
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Pincode',
                'required': True
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': 'any', 
                'placeholder': 'Latitude',
                'id': 'id_latitude'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': 'any', 
                'placeholder': 'Longitude',
                'id': 'id_longitude'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'gst_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'GST Number (Optional)'
            }),
            'offers_delivery': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'delivery_radius': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '10',
                'min': '1'
            }),
            'minimum_order': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'placeholder': '0.00',
                'min': '0'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load categories - handle case when no categories exist
        categories = Category.objects.filter(is_active=True)
        self.fields['category'].queryset = categories
        self.fields['category'].empty_label = "-- Select Category --"
        
        # Make latitude and longitude not required in form
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        self.fields['gst_number'].required = False
        self.fields['image'].required = False
    
    def clean_latitude(self):
        lat = self.cleaned_data.get('latitude')
        if lat is not None:
            if lat < -90 or lat > 90:
                raise forms.ValidationError("Latitude must be between -90 and 90")
        return lat
    
    def clean_longitude(self):
        lng = self.cleaned_data.get('longitude')
        if lng is not None:
            if lng < -180 or lng > 180:
                raise forms.ValidationError("Longitude must be between -180 and 180")
        return lng


class ShopSearchForm(forms.Form):
    """
    Form for searching shops
    """
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by city...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    radius = forms.IntegerField(
        required=False,
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Radius (km)',
            'min': '1'
        })
    )
"""
Product Forms for BuyReal
"""

from django import forms
from django.core.validators import FileExtensionValidator
from .models import Product, ProductCategory


class ProductForm(forms.ModelForm):
    """
    Form for creating and updating products
    """
    
    # Custom image field with validation
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'id_image'
        }),
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']
            )
        ],
        help_text='Allowed formats: JPG, JPEG, PNG, GIF, WEBP. Max size: 5MB'
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'price', 'compare_price',
            'stock', 'low_stock_threshold', 'sku', 'barcode', 'weight',
            'image', 'is_available', 'is_featured'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Product Name',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Product Description',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'placeholder': '0.00',
                'min': '0.01',
                'required': True
            }),
            'compare_price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'placeholder': 'Original Price (Optional)',
                'min': '0'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '0',
                'min': '0',
                'required': True
            }),
            'low_stock_threshold': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '5',
                'min': '0'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'SKU (Optional)'
            }),
            'barcode': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Barcode (Optional)'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'placeholder': 'Weight in grams',
                'min': '0'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Load categories
        categories = ProductCategory.objects.filter(is_active=True)
        self.fields['category'].queryset = categories
        self.fields['category'].empty_label = "-- Select Category --"
        self.fields['category'].required = False
        
        # Set optional fields
        self.fields['compare_price'].required = False
        self.fields['sku'].required = False
        self.fields['barcode'].required = False
        self.fields['weight'].required = False
        self.fields['low_stock_threshold'].initial = 5
        self.fields['is_available'].initial = True
    
    def clean_image(self):
        """Validate image file"""
        image = self.cleaned_data.get('image')
        
        if image:
            # Check file size (5MB max)
            if hasattr(image, 'size'):
                if image.size > 5 * 1024 * 1024:  # 5MB
                    raise forms.ValidationError("Image file too large. Maximum size is 5MB.")
            
            # Check content type
            if hasattr(image, 'content_type'):
                valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                if image.content_type not in valid_types:
                    raise forms.ValidationError("Invalid image type. Use JPG, PNG, GIF, or WEBP.")
        
        return image
    
    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        compare_price = cleaned_data.get('compare_price')
        
        if compare_price and price:
            if compare_price < price:
                raise forms.ValidationError(
                    "Compare price should be greater than selling price"
                )
        
        return cleaned_data
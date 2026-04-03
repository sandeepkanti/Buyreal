"""
Management command to set up initial data for BuyReal
"""

from django.core.management.base import BaseCommand
from shops.models import Category
from products.models import ProductCategory


class Command(BaseCommand):
    help = 'Sets up initial categories for shops and products'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Setting up initial data...'))
        self.stdout.write('')
        
        # Create Shop Categories
        shop_categories = [
            {'name': 'Electronics', 'icon': 'bi-laptop', 'description': 'Electronics and gadgets'},
            {'name': 'Grocery', 'icon': 'bi-basket', 'description': 'Grocery and daily needs'},
            {'name': 'Fashion', 'icon': 'bi-bag', 'description': 'Clothing and accessories'},
            {'name': 'Home & Living', 'icon': 'bi-house', 'description': 'Home decor and furniture'},
            {'name': 'Health & Beauty', 'icon': 'bi-heart', 'description': 'Health and beauty products'},
            {'name': 'Sports', 'icon': 'bi-bicycle', 'description': 'Sports and fitness'},
            {'name': 'Books & Stationery', 'icon': 'bi-book', 'description': 'Books and office supplies'},
            {'name': 'Toys & Games', 'icon': 'bi-controller', 'description': 'Toys and games'},
            {'name': 'Automotive', 'icon': 'bi-car-front', 'description': 'Auto parts and accessories'},
            {'name': 'Food & Beverages', 'icon': 'bi-cup-hot', 'description': 'Food and drinks'},
            {'name': 'Jewelry', 'icon': 'bi-gem', 'description': 'Jewelry and watches'},
            {'name': 'Pharmacy', 'icon': 'bi-capsule', 'description': 'Medicines and healthcare'},
        ]
        
        self.stdout.write('Creating Shop Categories:')
        shop_cat_created = 0
        for cat_data in shop_categories:
            obj, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon': cat_data['icon'],
                    'description': cat_data['description'],
                    'is_active': True
                }
            )
            if created:
                shop_cat_created += 1
                self.stdout.write(f'  ✓ Created: {cat_data["name"]}')
            else:
                self.stdout.write(f'  - Exists: {cat_data["name"]}')
        
        self.stdout.write('')
        
        # Create Product Categories
        product_categories = [
            'Smartphones',
            'Laptops',
            'Tablets',
            'Accessories',
            'Headphones',
            'Cameras',
            'Vegetables',
            'Fruits',
            'Dairy',
            'Snacks',
            'Beverages',
            'Men\'s Clothing',
            'Women\'s Clothing',
            'Kids Clothing',
            'Footwear',
            'Bags',
            'Watches',
            'Furniture',
            'Kitchen',
            'Bedding',
            'Decor',
            'Skincare',
            'Haircare',
            'Makeup',
            'Perfumes',
            'Fitness Equipment',
            'Outdoor Sports',
            'Indoor Games',
            'Books',
            'Stationery',
            'Office Supplies',
        ]
        
        self.stdout.write('Creating Product Categories:')
        prod_cat_created = 0
        for cat_name in product_categories:
            obj, created = ProductCategory.objects.get_or_create(
                name=cat_name,
                defaults={'is_active': True}
            )
            if created:
                prod_cat_created += 1
                self.stdout.write(f'  ✓ Created: {cat_name}')
            else:
                self.stdout.write(f'  - Exists: {cat_name}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('✅ Initial data setup complete!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(f'Shop categories: {shop_cat_created} created, {Category.objects.count()} total')
        self.stdout.write(f'Product categories: {prod_cat_created} created, {ProductCategory.objects.count()} total')
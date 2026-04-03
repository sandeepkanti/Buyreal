"""
Management command to create test data for BuyReal
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from shops.models import Shop, Category
from products.models import Product, ProductCategory
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates test users, shops, and products for development'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Creating test data...'))
        self.stdout.write('')
        
        # Create test customers
        self.stdout.write('Creating test customers:')
        for i in range(1, 4):
            user, created = User.objects.get_or_create(
                username=f'customer{i}',
                defaults={
                    'email': f'customer{i}@test.com',
                    'first_name': f'Customer',
                    'last_name': f'User{i}',
                    'role': 'customer',
                    'phone': f'+9198765432{i}0',
                    'city': 'Mumbai',
                    'state': 'Maharashtra',
                    'pincode': '400001',
                    'address': f'{i}23 Test Street, Mumbai',
                }
            )
            if created:
                user.set_password('test1234')
                user.save()
                self.stdout.write(f'  ✓ Created: customer{i}')
            else:
                self.stdout.write(f'  - Exists: customer{i}')
        
        self.stdout.write('')
        
        # Create test retailers with shops
        shop_data_list = [
            {
                'username': 'retailer1',
                'shop_name': 'Tech World Electronics',
                'category': 'Electronics',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'lat': '19.0760',
                'lng': '72.8777',
            },
            {
                'username': 'retailer2', 
                'shop_name': 'Fresh Mart Grocery',
                'category': 'Grocery',
                'city': 'Delhi',
                'state': 'Delhi',
                'lat': '28.6139',
                'lng': '77.2090',
            },
            {
                'username': 'retailer3',
                'shop_name': 'Fashion Hub Store',
                'category': 'Fashion',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'lat': '12.9716',
                'lng': '77.5946',
            },
        ]
        
        self.stdout.write('Creating test retailers and shops:')
        for data in shop_data_list:
            # Create retailer user
            user, user_created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': f'{data["username"]}@test.com',
                    'first_name': data['shop_name'].split()[0],
                    'last_name': 'Owner',
                    'role': 'retailer',
                    'phone': '+919876543210',
                    'city': data['city'],
                    'state': data['state'],
                    'pincode': '400001',
                }
            )
            if user_created:
                user.set_password('test1234')
                user.save()
                self.stdout.write(f'  ✓ Created retailer: {data["username"]}')
            else:
                self.stdout.write(f'  - Retailer exists: {data["username"]}')
            
            # Create shop
            category = Category.objects.filter(name=data['category']).first()
            if not category:
                self.stdout.write(self.style.ERROR(f'  ✗ Category not found: {data["category"]}'))
                self.stdout.write('  Run setup_initial_data first!')
                continue
            
            shop, shop_created = Shop.objects.get_or_create(
                owner=user,
                defaults={
                    'name': data['shop_name'],
                    'description': f'Welcome to {data["shop_name"]}! We offer the best products in {data["category"]}. Quality products at affordable prices with fast delivery.',
                    'category': category,
                    'email': f'{data["username"]}@shop.com',
                    'phone': '+919876543210',
                    'address': f'123 Main Street, {data["city"]}',
                    'city': data['city'],
                    'state': data['state'],
                    'pincode': '400001',
                    'latitude': Decimal(data['lat']),
                    'longitude': Decimal(data['lng']),
                    'status': 'approved',
                    'offers_delivery': True,
                    'delivery_radius': 15,
                    'minimum_order': Decimal('100.00'),
                }
            )
            
            if shop_created:
                self.stdout.write(f'  ✓ Created shop: {data["shop_name"]}')
                
                # Add products to shop
                product_categories = list(ProductCategory.objects.filter(is_active=True)[:5])
                
                for j in range(1, 8):
                    price = Decimal(str(random.randint(100, 5000)))
                    compare_price = price + Decimal(str(random.randint(50, 500))) if j % 2 == 0 else None
                    stock = random.randint(5, 50)
                    
                    prod_cat = random.choice(product_categories) if product_categories else None
                    
                    Product.objects.create(
                        shop=shop,
                        name=f'{data["shop_name"].split()[0]} Product {j}',
                        description=f'This is a high-quality product from {data["shop_name"]}. Best in class with great features and excellent value for money. Perfect for everyday use.',
                        category=prod_cat,
                        price=price,
                        compare_price=compare_price,
                        stock=stock,
                        low_stock_threshold=5,
                        is_available=True,
                        is_featured=(j == 1),
                    )
                
                self.stdout.write(f'    ✓ Created 7 products for {data["shop_name"]}')
            else:
                self.stdout.write(f'  - Shop exists: {data["shop_name"]}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('✅ Test data creation complete!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        self.stdout.write('Test Accounts:')
        self.stdout.write(self.style.WARNING('  Customers:'))
        self.stdout.write('    - customer1 / test1234')
        self.stdout.write('    - customer2 / test1234')
        self.stdout.write('    - customer3 / test1234')
        self.stdout.write(self.style.WARNING('  Retailers:'))
        self.stdout.write('    - retailer1 / test1234 (Tech World Electronics)')
        self.stdout.write('    - retailer2 / test1234 (Fresh Mart Grocery)')
        self.stdout.write('    - retailer3 / test1234 (Fashion Hub Store)')
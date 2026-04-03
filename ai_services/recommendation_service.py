"""
AI-Powered Product Recommendation Service
Uses Gemini AI + Collaborative Filtering
"""

from django.db.models import Count, Q
import logging

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Smart product recommendation engine
    """
    
    @staticmethod
    def get_personalized_recommendations(user, limit=8):
        """
        Get personalized product recommendations for a user
        """
        try:
            from products.models import Product
            from orders.models import Order
            
            if not user.is_authenticated:
                return RecommendationService.get_trending_products(limit)
            
            # Get user's order history
            user_orders = Order.objects.filter(customer=user).prefetch_related('items__product')
            
            if not user_orders.exists():
                return RecommendationService.get_trending_products(limit)
            
            # Get products user has bought
            bought_product_ids = []
            categories = set()
            shops = set()
            
            for order in user_orders:
                for item in order.items.all():
                    if item.product:
                        bought_product_ids.append(item.product.id)
                        if item.product.category:
                            categories.add(item.product.category.id)
                        shops.add(item.product.shop.id)
            
            # Recommend products from same categories/shops
            recommendations = Product.objects.filter(
                Q(category_id__in=categories) | Q(shop_id__in=shops),
                is_available=True,
                shop__status='approved'
            ).exclude(
                id__in=bought_product_ids
            ).select_related('shop', 'category').order_by('-created_at')[:limit]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation error: {e}")
            return []
    
    @staticmethod
    def get_similar_products(product, limit=6):
        """
        Get products similar to the given product
        """
        try:
            from products.models import Product
            
            # Same category, different product
            similar = Product.objects.filter(
                category=product.category,
                is_available=True,
                shop__status='approved'
            ).exclude(
                id=product.id
            ).select_related('shop', 'category')[:limit]
            
            if similar.count() < limit:
                # Fill with products from same shop
                shop_products = Product.objects.filter(
                    shop=product.shop,
                    is_available=True
                ).exclude(
                    id=product.id
                ).exclude(
                    id__in=[p.id for p in similar]
                ).select_related('shop', 'category')[:limit - similar.count()]
                
                similar = list(similar) + list(shop_products)
            
            return similar[:limit]
            
        except Exception as e:
            logger.error(f"Similar products error: {e}")
            return []
    
    @staticmethod
    def get_frequently_bought_together(product, limit=4):
        """
        Products frequently bought with this product
        """
        try:
            from products.models import Product
            from orders.models import OrderItem
            
            # Get orders containing this product
            orders_with_product = OrderItem.objects.filter(
                product=product
            ).values_list('order_id', flat=True)
            
            # Get other products in those orders
            other_products = OrderItem.objects.filter(
                order_id__in=orders_with_product
            ).exclude(
                product=product
            ).values('product').annotate(
                count=Count('product')
            ).order_by('-count')[:limit]
            
            product_ids = [item['product'] for item in other_products]
            
            products = Product.objects.filter(
                id__in=product_ids,
                is_available=True,
                shop__status='approved'
            ).select_related('shop', 'category')
            
            return products
            
        except Exception as e:
            logger.error(f"Frequently bought error: {e}")
            return []
    
    @staticmethod
    def get_trending_products(limit=8):
        """
        Get trending/popular products
        """
        try:
            from products.models import Product
            from django.utils import timezone
            from datetime import timedelta
            
            thirty_days_ago = timezone.now() - timedelta(days=30)
            
            trending = Product.objects.filter(
                is_available=True,
                shop__status='approved'
            ).annotate(
                order_count=Count('orderitem')
            ).order_by('-order_count', '-created_at').select_related('shop', 'category')[:limit]
            
            # If no orders, just return latest products
            if not trending.exists():
                trending = Product.objects.filter(
                    is_available=True,
                    shop__status='approved'
                ).order_by('-created_at').select_related('shop', 'category')[:limit]
            
            return trending
            
        except Exception as e:
            logger.error(f"Trending products error: {e}")
            return []
    
    @staticmethod
    def get_popular_in_area(user_city, limit=8):
        """
        Get popular products in user's city
        """
        try:
            from products.models import Product
            
            if not user_city:
                return RecommendationService.get_trending_products(limit)
            
            products = Product.objects.filter(
                shop__city__iexact=user_city,
                is_available=True,
                shop__status='approved'
            ).annotate(
                order_count=Count('orderitem')
            ).order_by('-order_count', '-created_at').select_related('shop', 'category')[:limit]
            
            # If not enough products in city, get from nearby
            if products.count() < limit:
                more_products = Product.objects.filter(
                    is_available=True,
                    shop__status='approved'
                ).exclude(
                    id__in=[p.id for p in products]
                ).order_by('-created_at').select_related('shop', 'category')[:limit - products.count()]
                
                products = list(products) + list(more_products)
            
            return products
            
        except Exception as e:
            logger.error(f"Popular in area error: {e}")
            return []


# Singleton instance
recommendation_service = RecommendationService()
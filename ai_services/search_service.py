"""
AI-Powered Smart Search Service
Enhanced search with AI understanding
"""

from django.db.models import Q
import logging

logger = logging.getLogger(__name__)


class SmartSearchService:
    """
    Intelligent search with AI enhancements
    """
    
    @staticmethod
    def search_products(query, filters=None):
        """
        Smart product search
        """
        try:
            from products.models import Product
            
            if not query or len(query.strip()) < 2:
                return Product.objects.none()
            
            # Clean query
            query = query.strip().lower()
            
            # Basic search
            products = Product.objects.filter(
                is_available=True,
                shop__status='approved'
            )
            
            # Apply filters
            if filters:
                if filters.get('category'):
                    products = products.filter(category_id=filters['category'])
                
                if filters.get('min_price'):
                    products = products.filter(price__gte=filters['min_price'])
                
                if filters.get('max_price'):
                    products = products.filter(price__lte=filters['max_price'])
                
                if filters.get('city'):
                    products = products.filter(shop__city__iexact=filters['city'])
            
            # Multi-field search
            search_filter = (
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query) |
                Q(shop__name__icontains=query) |
                Q(sku__icontains=query)
            )
            
            products = products.filter(search_filter).select_related(
                'shop', 'category'
            ).distinct()
            
            return products
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    @staticmethod
    def ai_enhanced_search(query, limit=20):
        """
        Use Gemini AI to understand and enhance search
        """
        try:
            from .gemini_service import gemini_service
            from products.models import Product
            import re
            import json
            
            if not gemini_service.is_available():
                return SmartSearchService.search_products(query)[:limit]
            
            # Extract search intent using AI
            prompt = f"""
            User search query: "{query}"
            
            Analyze this search query and extract:
            1. Main product type/category
            2. Any price range mentioned (if any)
            3. Any color/brand/specifications mentioned
            
            Return ONLY a JSON object like:
            {{
                "category": "product category",
                "price_range": {{"min": 0, "max": 10000}} or null,
                "keywords": ["keyword1", "keyword2"]
            }}
            """
            
            response = gemini_service.generate_response(prompt, max_tokens=200)
            
            if response:
                # Parse AI response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    search_intent = json.loads(json_match.group())
                    
                    # Build enhanced search
                    products = Product.objects.filter(
                        is_available=True,
                        shop__status='approved'
                    )
                    
                    # Apply AI-extracted filters
                    if search_intent.get('category'):
                        category = search_intent['category']
                        products = products.filter(
                            Q(name__icontains=category) |
                            Q(category__name__icontains=category) |
                            Q(description__icontains=category)
                        )
                    
                    if search_intent.get('price_range'):
                        pr = search_intent['price_range']
                        if pr and pr.get('min'):
                            products = products.filter(price__gte=pr['min'])
                        if pr and pr.get('max'):
                            products = products.filter(price__lte=pr['max'])
                    
                    if search_intent.get('keywords'):
                        for keyword in search_intent['keywords'][:3]:
                            products = products.filter(
                                Q(name__icontains=keyword) |
                                Q(description__icontains=keyword)
                            )
                    
                    return products.select_related('shop', 'category')[:limit]
                    
        except Exception as e:
            logger.error(f"AI search error: {e}")
        
        # Fallback to basic search
        return SmartSearchService.search_products(query)[:limit]
    
    @staticmethod
    def get_search_suggestions(query):
        """
        Get autocomplete suggestions
        """
        try:
            from products.models import Product, ProductCategory
            from shops.models import Shop
            
            if not query or len(query) < 2:
                return []
            
            suggestions = set()
            
            # Product name suggestions
            product_names = Product.objects.filter(
                name__icontains=query,
                is_available=True,
                shop__status='approved'
            ).values_list('name', flat=True).distinct()[:5]
            suggestions.update(product_names)
            
            # Category suggestions
            category_names = ProductCategory.objects.filter(
                name__icontains=query,
                is_active=True
            ).values_list('name', flat=True)[:3]
            suggestions.update(category_names)
            
            # Shop suggestions
            shop_names = Shop.objects.filter(
                name__icontains=query,
                status='approved'
            ).values_list('name', flat=True)[:3]
            suggestions.update(shop_names)
            
            return list(suggestions)[:10]
            
        except Exception as e:
            logger.error(f"Suggestions error: {e}")
            return []
    
    @staticmethod
    def search_with_typo_tolerance(query):
        """
        Handle typos in search (basic implementation)
        """
        # Common typo corrections
        typo_map = {
            'elctronics': 'electronics',
            'moblie': 'mobile',
            'loptop': 'laptop',
            'accesories': 'accessories',
            'grocry': 'grocery',
            'fahsion': 'fashion',
            'shooes': 'shoes',
            'phoen': 'phone',
        }
        
        corrected_query = query.lower()
        for typo, correct in typo_map.items():
            if typo in corrected_query:
                corrected_query = corrected_query.replace(typo, correct)
        
        return SmartSearchService.search_products(corrected_query)


# Singleton instance
smart_search = SmartSearchService()
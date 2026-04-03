"""
Views for AI Services
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)


@require_GET
def product_recommendations(request, product_id=None):
    """
    Get product recommendations
    """
    try:
        from .recommendation_service import recommendation_service
        
        rec_type = request.GET.get('type', 'personalized')
        limit = min(int(request.GET.get('limit', 8)), 20)  # Max 20
        
        products = []
        
        if rec_type == 'similar' and product_id:
            from products.models import Product
            try:
                product = Product.objects.get(id=product_id)
                products = recommendation_service.get_similar_products(product, limit)
            except Product.DoesNotExist:
                pass
        
        elif rec_type == 'frequently_bought' and product_id:
            from products.models import Product
            try:
                product = Product.objects.get(id=product_id)
                products = recommendation_service.get_frequently_bought_together(product, limit)
            except Product.DoesNotExist:
                pass
        
        elif rec_type == 'trending':
            products = recommendation_service.get_trending_products(limit)
        
        elif rec_type == 'popular_area':
            city = request.GET.get('city')
            if not city and request.user.is_authenticated:
                city = getattr(request.user, 'city', None)
            products = recommendation_service.get_popular_in_area(city, limit)
        
        else:
            # Personalized recommendations
            products = recommendation_service.get_personalized_recommendations(request.user, limit)
        
        # Serialize products
        data = []
        for p in products:
            try:
                data.append({
                    'id': p.id,
                    'name': p.name,
                    'price': str(p.price),
                    'image_url': p.image.url if p.image else None,
                    'shop_name': p.shop.name if p.shop else 'Unknown',
                    'in_stock': p.in_stock,
                    'category': p.category.name if p.category else None,
                })
            except Exception as e:
                logger.error(f"Error serializing product {p.id}: {e}")
        
        return JsonResponse({'recommendations': data, 'count': len(data)})
        
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        return JsonResponse({'recommendations': [], 'error': str(e)})


@require_GET
def smart_search_api(request):
    """
    Smart search API endpoint
    """
    try:
        from .search_service import smart_search
        
        query = request.GET.get('q', '').strip()
        use_ai = request.GET.get('ai', 'false').lower() == 'true'
        
        if not query:
            return JsonResponse({'results': [], 'count': 0})
        
        if use_ai:
            products = smart_search.ai_enhanced_search(query)
        else:
            products = smart_search.search_products(query)
        
        # Serialize results
        results = []
        for p in list(products)[:20]:
            try:
                results.append({
                    'id': p.id,
                    'name': p.name,
                    'description': p.description[:100] if p.description else '',
                    'price': str(p.price),
                    'image_url': p.image.url if p.image else None,
                    'shop_name': p.shop.name if p.shop else 'Unknown',
                    'category': p.category.name if p.category else None,
                })
            except Exception as e:
                logger.error(f"Error serializing product: {e}")
        
        return JsonResponse({'results': results, 'count': len(results)})
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return JsonResponse({'results': [], 'error': str(e)})


@require_GET
def search_suggestions(request):
    """
    Get search autocomplete suggestions
    """
    try:
        from .search_service import smart_search
        
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({'suggestions': []})
        
        suggestions = smart_search.get_search_suggestions(query)
        
        return JsonResponse({'suggestions': list(suggestions)[:10]})
        
    except Exception as e:
        logger.error(f"Suggestion error: {e}")
        return JsonResponse({'suggestions': []})


@require_POST
def chatbot_api(request):
    """
    Chatbot API endpoint
    """
    try:
        from .chatbot_service import chatbot
        
        # Parse JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Get bot response
        user = request.user if request.user.is_authenticated else None
        response = chatbot.get_response(message, user=user)
        
        return JsonResponse({
            'response': response,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Chatbot API error: {e}")
        return JsonResponse({
            'response': "Sorry, I encountered an error. Please try again.",
            'error': str(e)
        }, status=500)


def chatbot_page(request):
    """
    Chatbot interface page
    """
    return render(request, 'ai_services/chatbot.html')


@require_GET
def ai_status(request):
    """
    Check AI service status
    """
    try:
        from .gemini_service import gemini_service
        gemini_available = gemini_service.is_available()
    except Exception:
        gemini_available = False
    
    return JsonResponse({
        'gemini_available': gemini_available,
        'recommendations_enabled': True,
        'search_enabled': True,
        'chatbot_enabled': True,
    })


@require_GET
def list_available_models(request):
    """
    List available Gemini models (for debugging)
    """
    # Only allow admin users
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        from .gemini_service import gemini_service
        
        models = gemini_service.list_models()
        
        return JsonResponse({
            'available_models': models,
            'current_model': 'gemini-2.0-flash',
            'is_configured': gemini_service.is_available()
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'is_configured': False
        })
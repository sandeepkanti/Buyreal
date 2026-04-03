"""
Context processor to make cart count available in all templates
"""

def cart_count(request):
    """
    Add cart item count to template context
    """
    count = 0
    if request.user.is_authenticated:
        try:
            if hasattr(request.user, 'role') and request.user.role == 'customer':
                if hasattr(request.user, 'cart'):
                    count = request.user.cart.total_items
        except Exception:
            count = 0
    return {'cart_count': count}
"""
AI Chatbot Service using Gemini
Handles customer support queries
"""

from django.db.models import Q
import logging

logger = logging.getLogger(__name__)


class ChatbotService:
    """
    AI-powered chatbot for customer support
    """
    
    def __init__(self):
        self.system_context = """
        You are a helpful customer support assistant for BuyReal, a location-based eCommerce marketplace.
        
        You can help with:
        - Product information and search
        - Order status and tracking
        - Delivery information
        - Shop details
        - General questions about the platform
        
        Guidelines:
        - Be concise, friendly, and helpful
        - If you don't know something, admit it and suggest contacting support
        - Keep responses under 150 words
        - Use emojis sparingly for a friendly tone
        - Format information clearly with line breaks
        """
    
    def get_response(self, user_message, user=None, conversation_id=None):
        """
        Get chatbot response for user message
        """
        if not user_message or not user_message.strip():
            return "Please type a message so I can help you."
        
        # Check for specific intents first
        intent = self._detect_intent(user_message)
        
        if intent == 'order_status' and user and user.is_authenticated:
            return self._handle_order_status(user_message, user)
        elif intent == 'product_search':
            return self._handle_product_search(user_message)
        elif intent == 'shop_search':
            return self._handle_shop_search(user_message)
        elif intent == 'faq':
            faq_response = self.get_faq_response(user_message)
            if faq_response:
                return faq_response
        
        # Try AI response
        try:
            from .gemini_service import gemini_service
            
            if gemini_service.is_available():
                # Build context
                context = self.system_context
                
                if user and user.is_authenticated:
                    context += f"\n\nUser: {user.get_full_name() or user.username}"
                
                full_prompt = f"{context}\n\nUser question: {user_message}\n\nPlease provide a helpful response:"
                
                response = gemini_service.chat(full_prompt)
                if response and "error" not in response.lower():
                    return response
        except Exception as e:
            logger.error(f"AI chatbot error: {e}")
        
        # Fallback response
        return self._get_fallback_response(user_message, user)
    
    def _get_fallback_response(self, message, user=None):
        """
        Provide fallback responses when AI is unavailable
        """
        message_lower = message.lower()
        
        # Check for FAQ matches
        faq_response = self.get_faq_response(message)
        if faq_response:
            return faq_response
        
        # Greeting
        if any(word in message_lower for word in ['hi', 'hello', 'hey', 'help']):
            return """👋 Hello! Welcome to BuyReal!

I can help you with:
• 📦 Order status and tracking
• 🔍 Finding products
• 🏪 Shop information
• ❓ General questions

What would you like to know?"""
        
        # Order related
        if any(word in message_lower for word in ['order', 'track', 'delivery', 'shipped']):
            if user and user.is_authenticated:
                return self._handle_order_status(message, user)
            return "Please log in to check your order status."
        
        # Default response
        return """I'm here to help! You can ask me about:

• 📦 "Check my order status"
• 🔍 "Find [product name]"
• 🏪 "Show shops in [city]"
• 💳 "Payment methods"

For complex issues, please email: support@buyreal.com"""
    
    def _detect_intent(self, message):
        """
        Detect user intent from message
        """
        message_lower = message.lower()
        
        order_keywords = ['order', 'track', 'delivery', 'shipped', 'status', 'where is my']
        if any(keyword in message_lower for keyword in order_keywords):
            return 'order_status'
        
        product_keywords = ['product', 'find', 'search', 'looking for', 'buy', 'need']
        if any(keyword in message_lower for keyword in product_keywords):
            return 'product_search'
        
        shop_keywords = ['shop', 'store', 'seller', 'retailer']
        if any(keyword in message_lower for keyword in shop_keywords):
            return 'shop_search'
        
        faq_keywords = ['how to', 'how do', 'what is', 'payment', 'return', 'refund']
        if any(keyword in message_lower for keyword in faq_keywords):
            return 'faq'
        
        return 'general'
    
    def _handle_order_status(self, message, user):
        """
        Handle order status queries
        """
        try:
            from orders.models import Order
            import re
            
            order_number_match = re.search(r'BR\d+', message.upper())
            
            if order_number_match:
                order_number = order_number_match.group()
                try:
                    order = Order.objects.get(order_number=order_number, customer=user)
                    return f"""📦 **Order #{order.order_number}**

Status: {order.get_status_display()}
Total: ₹{order.total}
Shop: {order.shop.name}
Payment: {order.get_payment_status_display()}"""
                except Order.DoesNotExist:
                    return f"Order #{order_number} not found in your account."
            
            # Show recent orders
            recent_orders = Order.objects.filter(customer=user).order_by('-created_at')[:5]
            
            if recent_orders:
                response = "📦 **Your Recent Orders:**\n\n"
                for order in recent_orders:
                    response += f"• **#{order.order_number}**: {order.get_status_display()} - ₹{order.total}\n"
                return response
            
            return "You don't have any orders yet."
            
        except Exception as e:
            logger.error(f"Order status error: {e}")
            return "I couldn't fetch your orders. Please try again."
    
    def _handle_product_search(self, message):
        """
        Handle product search queries
        """
        try:
            from products.models import Product
            
            words = message.lower().split()
            stop_words = ['product', 'find', 'search', 'looking', 'for', 'buy', 'need', 'want', 'to', 'a', 'an', 'the']
            search_terms = [w for w in words if len(w) > 2 and w not in stop_words]
            
            if search_terms:
                search_query = ' '.join(search_terms[:3])
                
                products = Product.objects.filter(
                    Q(name__icontains=search_query) | Q(description__icontains=search_query),
                    is_available=True,
                    shop__status='approved'
                ).select_related('shop')[:5]
                
                if products:
                    response = f"🔍 Found products matching '{search_query}':\n\n"
                    for product in products:
                        response += f"• **{product.name}** - ₹{product.price} ({product.shop.name})\n"
                    return response
                else:
                    return f"No products found matching '{search_query}'."
            
            return "What product are you looking for?"
            
        except Exception as e:
            logger.error(f"Product search error: {e}")
            return "I had trouble searching. Please try the search bar."
    
    def _handle_shop_search(self, message):
        """
        Handle shop search queries
        """
        try:
            from shops.models import Shop
            
            words = message.lower().split()
            stop_words = ['shop', 'store', 'seller', 'retailer', 'find', 'show', 'me', 'in', 'at', 'near']
            search_terms = [w for w in words if len(w) > 2 and w not in stop_words]
            
            if search_terms:
                search_query = ' '.join(search_terms[:2])
                
                shops = Shop.objects.filter(
                    Q(name__icontains=search_query) | Q(city__icontains=search_query),
                    status='approved'
                )[:5]
                
                if shops:
                    response = f"🏪 Found shops matching '{search_query}':\n\n"
                    for shop in shops:
                        response += f"• **{shop.name}** - {shop.city}, {shop.state}\n"
                    return response
                else:
                    return f"No shops found matching '{search_query}'."
            
            return "Which shop or city are you looking for?"
            
        except Exception as e:
            logger.error(f"Shop search error: {e}")
            return "I had trouble searching for shops."
    
    def get_faq_response(self, question):
        """
        Get FAQ responses
        """
        question_lower = question.lower()
        
        faqs = {
            'how to order': """🛒 **How to Place an Order:**

1️⃣ Browse shops or search products
2️⃣ Add items to cart
3️⃣ Click checkout
4️⃣ Enter delivery address
5️⃣ Choose payment method
6️⃣ Confirm order!""",
            
            'payment': """💳 **Payment Methods:**

• Cash on Delivery (COD)
• UPI Payment

All payments are secure!""",
            
            'delivery': """🚚 **Delivery:**

• Local: 1-2 days
• Other areas: 2-4 days

Track your order in "My Orders".""",
            
            'return': """↩️ **Returns:**

• 7-day return window
• Product must be unused
• Contact shop for returns""",
        }
        
        for key, answer in faqs.items():
            if key in question_lower:
                return answer
        
        return None


# Singleton instance
chatbot = ChatbotService()
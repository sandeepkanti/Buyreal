"""
Google Gemini AI Service for BuyReal
Using the new google.genai package
"""

from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

# Try to import the new google.genai package
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google.genai package not installed. AI features disabled.")


class GeminiService:
    """
    Wrapper for Google Gemini API (new google.genai package)
    """
    
    def __init__(self):
        """Initialize Gemini API"""
        self.client = None
        self.is_configured = False
        self.model_name = "gemini-2.0-flash"  # Latest model
        
        if not GENAI_AVAILABLE:
            logger.warning("google.genai not available")
            return
        
        try:
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            
            if not api_key or api_key == 'YOUR_GEMINI_API_KEY_HERE':
                logger.warning("Gemini API key not configured")
                return
            
            # Initialize the client
            self.client = genai.Client(api_key=api_key)
            self.is_configured = True
            
            logger.info("Gemini service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.client = None
    
    def is_available(self):
        """Check if Gemini service is available"""
        return self.is_configured and self.client is not None
    
    def list_models(self):
        """List available models (for debugging)"""
        if not self.is_available():
            return []
        
        try:
            models = self.client.models.list()
            return [m.name for m in models]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def generate_response(self, prompt, max_tokens=500):
        """
        Generate AI response from prompt
        """
        if not self.is_available():
            logger.warning("Gemini service not available")
            return None
        
        try:
            # Check cache first
            cache_key = f"gemini_{hash(prompt)}"
            cached_response = cache.get(cache_key)
            if cached_response:
                return cached_response
            
            # Generate response using new API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                )
            )
            
            # Get text from response
            if response and response.text:
                result = response.text
                # Cache the response
                cache.set(cache_key, result, 300)  # 5 minutes
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return None
    
    def chat(self, message, conversation_history=None):
        """
        Chat with Gemini (for chatbot)
        """
        if not self.is_available():
            return "Sorry, AI service is currently unavailable. Please check your API configuration."
        
        try:
            # Generate response using new API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=message,
                config=types.GenerateContentConfig(
                    max_output_tokens=500,
                    temperature=0.7,
                )
            )
            
            if response and response.text:
                return response.text
            
            return "Sorry, I couldn't generate a response. Please try again."
            
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            return f"Sorry, I encountered an error. Please try again later."


# Singleton instance
gemini_service = GeminiService()
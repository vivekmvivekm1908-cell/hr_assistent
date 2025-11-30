import google.generativeai as genai
from config import Config

class GeminiHRAssistant:
    def __init__(self):
        try:
            # Configure with API key
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            
            # Use the correct model that's available for everyone
            self.model = genai.GenerativeModel('gemini-pro')
            print("✅ Gemini AI Connected Successfully!")
            
        except Exception as e:
            print(f"❌ Gemini Initialization Error: {str(e)}")
            raise Exception(f"Failed to initialize Gemini: {str(e)}")

    def get_response(self, user_question, conversation_history=[]):
        try:
            # Build conversation context
            prompt = """You are a professional HR Assistant. Answer HR questions clearly and helpfully.

Guidelines:
- Be professional and empathetic
- Provide accurate HR information
- Keep responses concise (2-3 paragraphs)
- Focus on leaves, benefits, policies, procedures

Question: """ + user_question + """

Please provide a helpful HR response:"""

            # Generate response
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg:
                return "❌ Invalid Google API Key. Please check your .env file."
            elif "quota" in error_msg.lower():
                return "⚠️ API quota exceeded. Please try again later or check your Google AI Studio account."
            else:
                return f"🔧 Technical Issue: {error_msg}. Please try again."
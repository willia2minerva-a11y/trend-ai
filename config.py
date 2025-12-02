# config.py - مُحسَّن
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # إعدادات فيسبوك
    PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')
    PAGE_ID = os.getenv('PAGE_ID')
    VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', 'trend_ai_bot_2024')
    
    # إعدادات Gemini
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # إعدادات التطبيق
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    # إعدادات المحتوى
    DEFAULT_LANGUAGE = 'ar'  # العربية
    SUPPORTED_LANGUAGES = ['ar', 'en']
    POST_TIMES = ['09:00', '13:00', '18:00']  # أوقات النشر
    
    @classmethod
    def validate(cls):
        """التحقق من صحة الإعدادات"""
        required = [
            ('PAGE_ACCESS_TOKEN', 'Facebook Page Access Token'),
            ('PAGE_ID', 'Facebook Page ID'),
            ('GEMINI_API_KEY', 'Gemini API Key')
        ]
        
        missing = []
        for key, name in required:
            if not getattr(cls, key):
                missing.append(name)
        
        if missing:
            print(f"❌ Missing: {', '.join(missing)}")
            return False
        
        print("✅ Config loaded successfully!")
        return True

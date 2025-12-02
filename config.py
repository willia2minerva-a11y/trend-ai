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
    
    # تأكد من وجود المفاتيح الأساسية
    @classmethod
    def validate(cls):
        required = ['PAGE_ACCESS_TOKEN', 'PAGE_ID', 'GEMINI_API_KEY']
        missing = [key for key in required if not getattr(cls, key)]
        
        if missing:
            raise ValueError(f"Missing required config: {missing}")
        
        print("✅ Configuration loaded successfully!")
        return True

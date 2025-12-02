import requests
import json
import random
import google.generativeai as genai
from datetime import datetime
from config import Config

class BotUtils:
    """أدوات مساعدة للبوت"""
    
    @staticmethod
    def get_trends():
        """جلب ترندات بسيطة"""
        tech_trends = [
            "الذكاء الاصطناعي وتطبيقاته",
            "التعلم الآلي في الحياة اليومية",
            "تقنيات المستقبل القريب",
            "التحول الرقمي في العالم العربي",
            "الأمن السيبراني والحماية",
            "التكنولوجيا في الرعاية الصحية",
            "السيارات الكهربائية والمستقبل",
            "الواقع الافتراضي والتعليم",
            "إنترنت الأشياء في المنازل الذكية",
            "البلوك تشين والتطبيقات العملية"
        ]
        random.shuffle(tech_trends)
        return tech_trends[:5]
    
    @staticmethod
    def init_gemini():
        """تهيئة Gemini"""
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            return genai.GenerativeModel('gemini-pro')
        except Exception as e:
            print(f"⚠️ Gemini init error: {e}")
            return None
    
    @staticmethod
    def send_facebook_message(recipient_id, message_text):
        """إرسال رسالة على فيسبوك"""
        try:
            params = {"access_token": Config.PAGE_ACCESS_TOKEN}
            headers = {"Content-Type": "application/json"}
            data = {
                "recipient": {"id": recipient_id},
                "message": {"text": message_text}
            }
            
            response = requests.post(
                "https://graph.facebook.com/v19.0/me/messages",
                params=params,
                headers=headers,
                json=data,
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"📤 Message send error: {e}")
            return False
    
    @staticmethod
    def generate_article(topic, language="arabic"):
        """توليد مقال بسيط"""
        model = BotUtils.init_gemini()
        if not model:
            return f"📝 مقال عن: {topic}\n\nهذا الموضوع مهم جداً في عالم التكنولوجيا اليوم.\n\n#تكنولوجيا #{topic.replace(' ', '_')}"
        
        try:
            prompt = f"""اكتب منشوراً قصيراً لفيسبوك عن: {topic}

المتطلبات:
1. اللغة: {language}
2. الطول: 100-150 كلمة
3. أضف إيموجيات مناسبة
4. أضف 3-5 هاشتاقات
5. كن محفزاً للتفاعل

المنشور:"""
            
            response = model.generate_content(prompt)
            return response.text
        except:
            return f"🔥 {topic} - موضوع شيق!\nشاركنا رأيك في التعليقات 👇\n\n#{topic.replace(' ', '_')}"
    
    @staticmethod
    def post_to_facebook(content, image_url=None):
        """نشر على صفحة فيسبوك"""
        try:
            url = f"https://graph.facebook.com/{Config.PAGE_ID}/feed"
            
            data = {
                'message': content,
                'access_token': Config.PAGE_ACCESS_TOKEN
            }
            
            if image_url:
                # أولاً نشر الصورة
                photo_url = f"https://graph.facebook.com/{Config.PAGE_ID}/photos"
                photo_data = {
                    'url': image_url,
                    'access_token': Config.PAGE_ACCESS_TOKEN
                }
                photo_response = requests.post(photo_url, data=photo_data)
                
                if photo_response.status_code == 200:
                    photo_id = photo_response.json().get('id')
                    data['attached_media'] = json.dumps([{"media_fbid": photo_id}])
            
            response = requests.post(url, data=data)
            return response.json()
            
        except Exception as e:
            print(f"📮 Post error: {e}")
            return {"error": str(e)}

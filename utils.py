# utils.py - مُحسَّن
import requests
import json
import random
import google.generativeai as genai
from datetime import datetime
import threading
import schedule
import time
from config import Config

class AIAssistant:
    """مساعد الذكاء الاصطناعي"""
    
    def __init__(self):
        self.model = None
        self.init_gemini()
    
    def init_gemini(self):
        """تهيئة Gemini API"""
        try:
            if Config.GEMINI_API_KEY:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-pro')
                print("✅ Gemini AI initialized successfully!")
                return True
            else:
                print("❌ Gemini API key missing")
                return False
        except Exception as e:
            print(f"❌ Gemini init error: {e}")
            return False
    
    def generate_article(self, topic, language="arabic"):
        """توليد مقال باستخدام AI"""
        if not self.model:
            return self._fallback_article(topic)
        
        try:
            prompt = f"""
            اكتب منشوراً لفيسبوك عن: {topic}
            
            المتطلبات:
            1. اللغة: {language}
            2. الطول: 150-200 كلمة
            3. الأسلوب: احترافي وسهل الفهم
            4. أضف: مقدمة، 3 نقاط رئيسية، خاتمة
            5. أضف 5 هاشتاقات ذات صلة
            6. استخدم إيموجيات مناسبة
            7. أضف دعوة للتفاعل (اطلب الرأي في التعليقات)
            
            المنشور:
            """
            
            response = self.model.generate_content(prompt)
            article = response.text.strip()
            
            # إضافة توقيع
            signature = "\n\n🤖 منشور مولد بواسطة Trend AI"
            article += signature
            
            return article
            
        except Exception as e:
            print(f"❌ Article generation error: {e}")
            return self._fallback_article(topic)
    
    def _fallback_article(self, topic):
        """مقال احتياطي عند فشل AI"""
        fallback = f"""🔥 {topic}
        
موضوع مثير للاهتمام! في عصر التكنولوجيا المتسارع، أصبح {topic} من أهم المجالات التي تشغل بال الباحثين والمطورين.

💡 ثلاث نقاط رئيسية:
1. أهمية {topic} في حياتنا المعاصرة
2. التحديات والفرص في هذا المجال
3. مستقبل {topic} في السنوات القادمة

ما رأيك في مستقبل هذا المجال؟ شاركنا تفكيرك! 👇

#{topic.replace(' ', '_')} #تكنولوجيا #مستقبل #ابتكار

🤖 منشور مولد بواسطة Trend AI"""
        return fallback
    
    def translate_text(self, text, target_lang="en"):
        """ترجمة النص"""
        if not self.model:
            return text
        
        try:
            lang_names = {
                'ar': 'Arabic',
                'en': 'English',
                'fr': 'French',
                'es': 'Spanish'
            }
            
            lang_name = lang_names.get(target_lang, target_lang)
            prompt = f"Translate to {lang_name}:\n\n{text}"
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return text
    
    def get_trending_topics(self):
        """جلب مواضيع رائجة"""
        tech_trends = [
            "الذكاء الاصطناعي في الرعاية الصحية",
            "المدن الذكية والمستقبل الحضري",
            "التحول الرقمي في العالم العربي",
            "أمن المعلومات في عصر التكنولوجيا",
            "التعلم الآلي وتطبيقاته العملية",
            "الواقع الافتراضي في التعليم",
            "إنترنت الأشياء IoT",
            "البلوك تشين وتطبيقاته",
            "الطاقة المتجددة والتكنولوجيا",
            "السيارات ذاتية القيادة"
        ]
        
        business_trends = [
            "ريادة الأعمال التقنية",
            "التسويق الرقمي 2024",
            "العمل عن بعد ومستقبل المكاتب",
            "الاقتصاد الرقمي",
            "الاستثمار في التكنولوجيا"
        ]
        
        # اختيار عشوائي
        all_trends = tech_trends + business_trends
        random.shuffle(all_trends)
        
        return all_trends[:5]
    
    def generate_hashtags(self, topic):
        """توليد هاشتاقات ذكية"""
        words = topic.split()
        hashtags = [
            f"#{topic.replace(' ', '_')}",
            "#تكنولوجيا",
            "#مستقبل",
            "#ابتكار",
            "#trends",
            "#ai"
        ]
        
        # إضافة هاشتاقات من الكلمات المفتاحية
        for word in words[:3]:
            if len(word) > 2:
                hashtags.append(f"#{word}")
        
        return ' '.join(hashtags[:8])

class FacebookManager:
    """مدير عمليات فيسبوك"""
    
    @staticmethod
    def send_message(recipient_id, text):
        """إرسال رسالة خاصة"""
        try:
            url = "https://graph.facebook.com/v19.0/me/messages"
            params = {"access_token": Config.PAGE_ACCESS_TOKEN}
            data = {
                "recipient": {"id": recipient_id},
                "message": {"text": text}
            }
            
            response = requests.post(url, params=params, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"📤 Message error: {e}")
            return False
    
    @staticmethod
    def create_post(content, image_url=None):
        """إنشاء منشور على الصفحة"""
        try:
            url = f"https://graph.facebook.com/{Config.PAGE_ID}/feed"
            
            data = {
                'message': content,
                'access_token': Config.PAGE_ACCESS_TOKEN
            }
            
            if image_url:
                # نشر الصورة أولاً
                photo_url = f"https://graph.facebook.com/{Config.PAGE_ID}/photos"
                photo_data = {
                    'url': image_url,
                    'access_token': Config.PAGE_ACCESS_TOKEN,
                    'published': 'false'
                }
                
                photo_response = requests.post(photo_url, data=photo_data)
                
                if photo_response.status_code == 200:
                    photo_id = photo_response.json().get('id')
                    data['attached_media'] = f'[{{"media_fbid":"{photo_id}"}}]'
            
            response = requests.post(url, data=data)
            result = response.json()
            
            if 'id' in result:
                post_id = result['id']
                post_url = f"https://facebook.com/{post_id}"
                print(f"✅ Published: {post_url}")
                return {
                    'success': True,
                    'post_id': post_id,
                    'url': post_url
                }
            else:
                print(f"❌ Post failed: {result}")
                return {
                    'success': False,
                    'error': result.get('error', {}).get('message', 'Unknown error')
                }
                
        except Exception as e:
            print(f"❌ Post creation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_unsplash_image(query):
        """الحصول على صورة من Unsplash"""
        try:
            url = f"https://source.unsplash.com/1024x1024/?{query.replace(' ', ',')}"
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                return url
        except:
            pass
        
        # رابط بدائي
        fallback_images = [
            "https://images.unsplash.com/photo-1677442136019-21780ecad995",
            "https://images.unsplash.com/photo-1679087625659-70c5f171e7c5",
            "https://images.unsplash.com/photo-1677442135136-760c81290f72"
        ]
        return random.choice(fallback_images)

class AutoPostScheduler:
    """جدولة النشر التلقائي"""
    
    def __init__(self):
        self.ai = AIAssistant()
        self.fb = FacebookManager()
        self.running = False
    
    def create_daily_post(self):
        """إنشاء ونشر منشور يومي"""
        print(f"🕒 [{datetime.now().strftime('%H:%M')}] Creating auto-post...")
        
        try:
            # 1. جلب موضوع
            trends = self.ai.get_trending_topics()
            topic = trends[0] if trends else "التكنولوجيا الحديثة"
            
            # 2. توليد المقال
            article = self.ai.generate_article(topic)
            
            # 3. إضافة هاشتاقات
            hashtags = self.ai.generate_hashtags(topic)
            full_content = f"{article}\n\n{hashtags}"
            
            # 4. الحصول على صورة
            image_url = self.fb.get_unsplash_image(topic)
            
            # 5. النشر
            result = self.fb.create_post(full_content, image_url)
            
            if result['success']:
                print(f"✅ Auto-post published: {topic}")
                return result
            else:
                print(f"❌ Auto-post failed: {result.get('error')}")
                return result
                
        except Exception as e:
            print(f"❌ Auto-post error: {e}")
            return {'success': False, 'error': str(e)}
    
    def start_scheduler(self):
        """بدء الجدولة التلقائية"""
        if self.running:
            return
        
        print("⏰ Starting auto-post scheduler...")
        
        # جدولة المهام
        for post_time in Config.POST_TIMES:
            schedule.every().day.at(post_time).do(self.create_daily_post)
        
        # نشر أول منشور فوراً
        print("🚀 Creating initial post...")
        self.create_daily_post()
        
        self.running = True
        
        # تشغيل المجدول في thread منفصل
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
        print("✅ Scheduler started successfully!")

# إنشاء الكائنات العالمية
ai_assistant = AIAssistant()
fb_manager = FacebookManager()
post_scheduler = AutoPostScheduler()

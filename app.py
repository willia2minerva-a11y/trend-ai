from flask import Flask, request, jsonify
from config import Config
from utils import BotUtils
import threading
import schedule
import time
from datetime import datetime
import os

# تهيئة التطبيق
app = Flask(__name__)

# التحقق من الإعدادات
Config.validate()

# متغيرات البوت
bot_active = True

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Trend AI Bot</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            h1 { color: #1877F2; }
            .status { 
                background: #f0f0f0; 
                padding: 20px; 
                border-radius: 10px; 
                margin: 20px auto; 
                max-width: 600px;
            }
            .btn { 
                background: #1877F2; 
                color: white; 
                padding: 10px 20px; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer;
                margin: 10px;
            }
        </style>
    </head>
    <body>
        <h1>🚀 Trend AI Bot</h1>
        <div class="status">
            <p><strong>الحالة:</strong> ✅ نشط</p>
            <p><strong>آخر تحديث:</strong> {}</p>
            <p><strong>الميزات:</strong> بوت فيسبوك + نشر تلقائي</p>
        </div>
        <div>
            <button class="btn" onclick="testPost()">تجربة النشر</button>
            <button class="btn" onclick="getTrends()">عرض الترندات</button>
        </div>
        <script>
            function testPost() {
                fetch('/test-post')
                .then(r => r.json())
                .then(data => alert(data.message || 'تم النشر!'))
            }
            function getTrends() {
                fetch('/trends')
                .then(r => r.json())
                .then(data => alert('الترندات:\\n' + data.trends.join('\\n')))
            }
        </script>
    </body>
    </html>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Webhook للتواصل مع فيسبوك"""
    if request.method == 'GET':
        # التحقق من Webhook
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if token == Config.VERIFY_TOKEN:
            print("✅ Webhook verified!")
            return challenge
        return 'Verification failed', 403
    
    elif request.method == 'POST':
        try:
            data = request.json
            
            if data.get('object') == 'page':
                for entry in data.get('entry', []):
                    for messaging_event in entry.get('messaging', []):
                        # استخراج البيانات
                        sender_id = messaging_event.get('sender', {}).get('id')
                        message_text = messaging_event.get('message', {}).get('text', '')
                        
                        if sender_id and message_text:
                            # معالجة الرسالة في thread منفصل
                            threading.Thread(
                                target=process_message,
                                args=(sender_id, message_text)
                            ).start()
            
            return jsonify({'status': 'ok'})
            
        except Exception as e:
            print(f"❌ Webhook error: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

def process_message(sender_id, message_text):
    """معالجة الرسالة"""
    print(f"📩 Message from {sender_id}: {message_text}")
    
    # الأوامر العربية
    if "مرحبا" in message_text or "اهلا" in message_text:
        response = "مرحباً! 👋\nأنا بوت Trend AI\n\nيمكنني:\n📊 عرض الترندات - اكتب 'ترندات'\n📝 نشر مقال - اكتب 'مقال'\n❓ المساعدة - اكتب 'مساعدة'"
    
    elif "ترندات" in message_text or "trends" in message_text.lower():
        trends = BotUtils.get_trends()
        response = "🔥 أحدث الترندات:\n\n" + "\n".join([f"• {t}" for t in trends])
    
    elif "مقال" in message_text or "article" in message_text.lower():
        # استخراج الموضوع من الرسالة
        if "عن" in message_text:
            topic = message_text.split("عن")[-1].strip()
        else:
            topic = "التكنولوجيا الحديثة"
        
        # توليد المقال
        article = BotUtils.generate_article(topic)
        response = f"📝 مقال عن {topic}:\n\n{article}"
    
    elif "مساعدة" in message_text or "help" in message_text.lower():
        response = """🆘 مساعدة - Trend AI Bot:

الأوامر المتاحة:
1. "ترندات" - عرض أحدث الترندات
2. "مقال عن [الموضوع]" - كتابة مقال
3. "نشر [الموضوع]" - نشر مقال على الصفحة
4. "مساعدة" - عرض هذه التعليمات

مثال:
"مقال عن الذكاء الاصطناعي"
"ترندات" """
    
    elif "نشر" in message_text and "عن" in message_text:
        # نشر مباشر على الصفحة
        topic = message_text.split("عن")[-1].strip()
        article = BotUtils.generate_article(topic)
        
        # النشر على الصفحة
        result = BotUtils.post_to_facebook(article)
        
        if "id" in result:
            response = f"✅ تم النشر بنجاح!\n\nالرابط: https://facebook.com/{result['id']}"
        else:
            response = "❌ فشل النشر. حاول مرة أخرى."
    
    else:
        response = "لم أفهم رسالتك. اكتب 'مساعدة' لرؤية الأوامر المتاحة."
    
    # إرسال الرد
    BotUtils.send_facebook_message(sender_id, response)

@app.route('/trends', methods=['GET'])
def get_trends_api():
    """API لجلب الترندات"""
    trends = BotUtils.get_trends()
    return jsonify({
        'success': True,
        'trends': trends,
        'count': len(trends),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test-post', methods=['POST', 'GET'])
def test_post():
    """تجربة النشر"""
    try:
        trends = BotUtils.get_trends()
        topic = trends[0] if trends else "التكنولوجيا"
        
        article = BotUtils.generate_article(topic)
        result = BotUtils.post_to_facebook(article)
        
        if "id" in result:
            return jsonify({
                'success': True,
                'message': f'تم النشر عن: {topic}',
                'post_id': result['id']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'فشل النشر',
                'error': result
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """فحص صحة التطبيق"""
    return jsonify({
        'status': 'healthy',
        'service': 'trend-ai-bot',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'features': ['facebook-bot', 'auto-posting', 'trends']
    })

# وظيفة النشر التلقائي
def auto_poster():
    """النشر التلقائي المجدول"""
    def job():
        if bot_active:
            print(f"🕒 [{datetime.now()}] بدء النشر التلقائي...")
            
            try:
                trends = BotUtils.get_trends()
                if trends:
                    topic = trends[0]
                    article = BotUtils.generate_article(topic)
                    result = BotUtils.post_to_facebook(article)
                    
                    if "id" in result:
                        print(f"✅ تم النشر: {topic}")
                    else:
                        print(f"❌ فشل النشر: {result}")
            
            except Exception as e:
                print(f"⚠️ Auto-post error: {e}")
    
    # جدولة المهام
    schedule.every(6).hours.do(job)  # كل 6 ساعات
    
    print("⏰ جدولة النشر التلقائي بدأت...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# بدء النشر التلقائي في thread منفصل
if os.getenv('AUTO_POST', 'true').lower() == 'true':
    scheduler_thread = threading.Thread(target=auto_poster, daemon=True)
    scheduler_thread.start()
    print("🚀 النشر التلقائي مفعل!")

if __name__ == '__main__':
    port = Config.PORT
    print(f"🌐 Starting Trend AI Bot on port {port}")
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)

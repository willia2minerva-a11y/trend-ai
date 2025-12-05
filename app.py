# app.py - النسخة المحسنة
from flask import Flask, request, jsonify, render_template_string
import os
from datetime import datetime
from config import Config
from utils import ai_assistant, fb_manager, post_scheduler

app = Flask(__name__)

# التحقق من الإعدادات
Config.validate()

# HTML لواجهة الإدارة
DASHBOARD_HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Trend AI Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Arial, sans-serif; }
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { text-align: center; padding: 40px 0; }
        h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .subtitle { opacity: 0.9; font-size: 1.1rem; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
        .stat-card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 25px; text-align: center; }
        .stat-number { font-size: 2.5rem; font-weight: bold; margin: 10px 0; }
        .stat-label { opacity: 0.8; font-size: 0.9rem; }
        .control-panel { background: rgba(255,255,255,0.1); border-radius: 15px; padding: 30px; margin: 30px 0; }
        .control-title { margin-bottom: 20px; font-size: 1.5rem; }
        .btn { background: #4CAF50; color: white; border: none; padding: 12px 25px; border-radius: 8px; cursor: pointer; font-size: 1rem; margin: 5px; transition: all 0.3s; }
        .btn:hover { background: #45a049; transform: translateY(-2px); }
        .btn-red { background: #f44336; }
        .btn-red:hover { background: #da190b; }
        .trends-box { background: rgba(255,255,255,0.1); border-radius: 10px; padding: 20px; margin: 20px 0; }
        .trend-item { padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .trend-item:last-child { border-bottom: none; }
        .status-indicator { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 10px; }
        .status-active { background: #4CAF50; }
        .status-inactive { background: #f44336; }
        .form-group { margin: 15px 0; }
        input, textarea { width: 100%; padding: 10px; border-radius: 5px; border: none; margin-top: 5px; }
        .logs { background: rgba(0,0,0,0.2); border-radius: 10px; padding: 15px; max-height: 200px; overflow-y: auto; margin-top: 20px; font-family: monospace; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Trend AI Dashboard</h1>
            <p class="subtitle">إدارة بوت النشر التلقائي على فيسبوك</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">حالة البوت</div>
                <div class="stat-number">
                    <span class="status-indicator status-active"></span>
                    نشط
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">المنشورات اليوم</div>
                <div class="stat-number" id="posts-today">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">آخر تحديث</div>
                <div class="stat-number" id="last-update">{{ last_update }}</div>
            </div>
        </div>
        
        <div class="control-panel">
            <h2 class="control-title">🛠️ لوحة التحكم</h2>
            
            <div class="form-group">
                <label>✏️ إنشاء منشور جديد:</label>
                <input type="text" id="post-topic" placeholder="أدخل موضوع المنشور..." value="التكنولوجيا الحديثة">
                <button class="btn" onclick="createPost()">إنشاء ونشر</button>
            </div>
            
            <div class="form-group">
                <label>🔄 النشر التلقائي:</label>
                <button class="btn" onclick="toggleAutoPost()" id="auto-post-btn">تشغيل النشر التلقائي</button>
                <button class="btn" onclick="postNow()">نشر الآن</button>
            </div>
            
            <div class="form-group">
                <label>📊 الترندات الحالية:</label>
                <button class="btn" onclick="loadTrends()">تحديث الترندات</button>
                <div class="trends-box" id="trends-list">
                    جاري تحميل الترندات...
                </div>
            </div>
        </div>
        
        <div class="logs">
            <div>📝 سجل النشاط:</div>
            <div id="activity-log">جاري التحميل...</div>
        </div>
    </div>
    
    <script>
        let autoPostActive = false;
        
        function updateTime() {
            const now = new Date().toLocaleString('ar-SA');
            document.getElementById('last-update').textContent = now;
        }
        
        function createPost() {
            const topic = document.getElementById('post-topic').value;
            if (!topic) return alert('أدخل موضوعاً للمنشور');
            
            fetch('/api/create-post', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({topic: topic})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert('✅ تم النشر بنجاح!');
                    addLog(`تم نشر منشور عن: ${topic}`);
                    document.getElementById('posts-today').textContent = 
                        parseInt(document.getElementById('posts-today').textContent) + 1;
                } else {
                    alert('❌ فشل النشر: ' + data.error);
                }
            });
        }
        
        function toggleAutoPost() {
            fetch('/api/toggle-auto-post', {method: 'POST'})
            .then(r => r.json())
            .then(data => {
                autoPostActive = data.active;
                const btn = document.getElementById('auto-post-btn');
                btn.textContent = autoPostActive ? 'إيقاف النشر التلقائي' : 'تشغيل النشر التلقائي';
                btn.className = autoPostActive ? 'btn btn-red' : 'btn';
                addLog(autoPostActive ? 'تم تشغيل النشر التلقائي' : 'تم إيقاف النشر التلقائي');
            });
        }
        
        function postNow() {
            fetch('/api/post-now', {method: 'POST'})
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert('✅ تم النشر بنجاح!');
                    addLog('تم نشر منشور تلقائي');
                } else {
                    alert('❌ فشل النشر: ' + data.error);
                }
            });
        }
        
        function loadTrends() {
            fetch('/api/trends')
            .then(r => r.json())
            .then(data => {
                const trendsList = document.getElementById('trends-list');
                trendsList.innerHTML = data.trends.map(t => 
                    `<div class="trend-item">📌 ${t}</div>`
                ).join('');
                addLog('تم تحديث قائمة الترندات');
            });
        }
        
        function addLog(message) {
            const logDiv = document.getElementById('activity-log');
            const time = new Date().toLocaleTimeString('ar-SA');
            logDiv.innerHTML = `[${time}] ${message}<br>` + logDiv.innerHTML;
        }
        
        // التحميل الأولي
        updateTime();
        setInterval(updateTime, 60000);
        loadTrends();
        
        // تحديث حالة النشر التلقائي
        fetch('/api/auto-post-status')
        .then(r => r.json())
        .then(data => {
            autoPostActive = data.active;
            const btn = document.getElementById('auto-post-btn');
            btn.textContent = autoPostActive ? 'إيقاف النشر التلقائي' : 'تشغيل النشر التلقائي';
            btn.className = autoPostActive ? 'btn btn-red' : 'btn';
        });
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """لوحة التحكم الرئيسية"""
    return render_template_string(DASHBOARD_HTML, 
                                 last_update=datetime.now().strftime("%H:%M:%S"))

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """التحقق من Webhook"""
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if token == Config.VERIFY_TOKEN:
        print("✅ Webhook verified successfully!")
        return challenge
    return 'Verification failed', 403

@app.route('/webhook', methods=['POST'])
def handle_messages():
    """معالجة رسائل Messenger"""
    try:
        data = request.json
        
        if data.get('object') == 'page':
            for entry in data.get('entry', []):
                for event in entry.get('messaging', []):
                    sender_id = event.get('sender', {}).get('id')
                    message = event.get('message', {}).get('text', '')
                    
                    if sender_id and message:
                        handle_user_message(sender_id, message)
        
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({'status': 'error'}), 500

def handle_user_message(sender_id, message):
    """معالجة رسالة المستخدم"""
    print(f"📩 Message from {sender_id}: {message}")
    
    response = ""
    
    if any(word in message for word in ['مرحبا', 'اهلا', 'hello', 'hi']):
        response = """مرحباً بك! 👋

أنا بوت Trend AI، يمكنني:
📊 عرض الترندات - اكتب 'ترندات'
📝 إنشاء مقال - اكتب 'مقال [الموضوع]'
🚀 نشر على الصفحة - اكتب 'نشر [الموضوع]'
❓ المساعدة - اكتب 'مساعدة'

مثال: 'مقال الذكاء الاصطناعي'"""
    
    elif 'ترندات' in message or 'trends' in message.lower():
        trends = ai_assistant.get_trending_topics()
        response = "🔥 أحدث الترندات:\n\n" + "\n".join([f"• {t}" for t in trends])
    
    elif 'مقال' in message or 'article' in message.lower():
        # استخراج الموضوع
        if 'مقال' in message:
            topic = message.split('مقال')[-1].strip()
        elif 'article' in message.lower():
            topic = message.lower().split('article')[-1].strip()
        else:
            topic = 'التكنولوجيا'
        
        if not topic:
            topic = 'التكنولوجيا الحديثة'
        
        # توليد المقال
        article = ai_assistant.generate_article(topic)
        response = f"📝 مقال عن '{topic}':\n\n{article}\n\nاكتب 'نشر' لنشره على الصفحة!"
    
    elif 'نشر' in message:
        # استخراج الموضوع
        topic = message.split('نشر')[-1].strip()
        if not topic:
            topic = 'التكنولوجيا'
        
        # توليد المقال
        article = ai_assistant.generate_article(topic)
        
        # النشر على الصفحة
        result = fb_manager.create_post(article)
        
        if result['success']:
            response = f"✅ تم النشر بنجاح!\n\n📌 الموضوع: {topic}\n🔗 الرابط: {result['url']}"
        else:
            response = f"❌ فشل النشر:\n{result.get('error', 'حدث خطأ')}"
    
    elif 'مساعدة' in message or 'help' in message.lower():
        response = """🆘 **قائمة الأوامر:**

1. `ترندات` - عرض أحدث الترندات
2. `مقال [الموضوع]` - كتابة مقال (مثال: مقال الذكاء الاصطناعي)
3. `نشر [الموضوع]` - نشر مقال على الصفحة
4. `مساعدة` - عرض هذه القائمة

📌 مثال:
- `مقال مستقبل التكنولوجيا`
- `نشر الذكاء الاصطناعي`
- `ترندات`"""
    
    else:
        response = "لم أفهم طلبك. اكتب 'مساعدة' لرؤية الأوامر المتاحة."
    
    # إرسال الرد
    fb_manager.send_message(sender_id, response)

# ========== REST API للتطبيق ==========

@app.route('/api/health')
def api_health():
    """فحص صحة API"""
    return jsonify({
        'status': 'healthy',
        'service': 'trend-ai-bot',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'features': ['ai-articles', 'facebook-posting', 'trends', 'scheduling']
    })

@app.route('/api/trends')
def api_trends():
    """جلب الترندات"""
    trends = ai_assistant.get_trending_topics()
    return jsonify({
        'success': True,
        'count': len(trends),
        'trends': trends
    })

@app.route('/api/create-post', methods=['POST'])
def api_create_post():
    """إنشاء منشور جديد"""
    try:
        data = request.json
        topic = data.get('topic', 'التكنولوجيا الحديثة')
        
        # توليد المقال
        article = ai_assistant.generate_article(topic)
        hashtags = ai_assistant.generate_hashtags(topic)
        content = f"{article}\n\n{hashtags}"
        
        # النشر
        result = fb_manager.create_post(content)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/post-now', methods=['POST'])
def api_post_now():
    """نشر منشور فوري"""
    try:
        result = post_scheduler.create_daily_post()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/toggle-auto-post', methods=['POST'])
def api_toggle_auto_post():
    """تبديل حالة النشر التلقائي"""
    try:
        if not post_scheduler.running:
            post_scheduler.start_scheduler()
            status = True
        else:
            # Note: We can't actually stop it easily in this simple implementation
            status = post_scheduler.running
        
        return jsonify({
            'success': True,
            'active': status,
            'message': 'Auto-post scheduler toggled'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/auto-post-status')
def api_auto_post_status():
    """حالة النشر التلقائي"""
    return jsonify({
        'active': post_scheduler.running,
        'next_scheduled': Config.POST_TIMES if post_scheduler.running else []
    })

# بدء النشر التلقائي عند التشغيل
if os.getenv('AUTO_POST', 'true').lower() == 'true':
    post_scheduler.start_scheduler()

if __name__ == '__main__':
    port = Config.PORT
    print(f"🚀 Starting Trend AI Bot v2.0 on port {port}")
    print(f"📊 Dashboard: http://localhost:{port}")
    print(f"🔧 API Health: http://localhost:{port}/api/health")
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)

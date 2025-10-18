# My Prabh - Production Entry Point

import os
import sys
from datetime import datetime

def log_with_timestamp(message):
    """Log message with IST timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ' IST'
    print(f"{timestamp}{message}")

log_with_timestamp(f"PORT: {os.environ.get('PORT', '8080')}")

try:
    log_with_timestamp("📦 Importing working app...")
    from app_working import app
    log_with_timestamp("✅ Working app imported successfully")
except Exception as e:
    log_with_timestamp(f"❌ Working app failed: {e}")
    try:
        log_with_timestamp("📦 Importing emergency app...")
        from app_emergency import app
        log_with_timestamp("✅ Emergency app imported successfully")
    except Exception as e2:
        log_with_timestamp(f"❌ Emergency app failed: {e2}")
        try:
            log_with_timestamp("📦 Importing full app...")
            from app import app
            log_with_timestamp("✅ Full app imported successfully")
        except Exception as e3:
            log_with_timestamp(f"❌ Full app failed: {e3}")
            log_with_timestamp("🚨 Creating minimal emergency app...")
            
            # Minimal emergency app
            from flask import Flask, render_template, jsonify
            app = Flask(__name__)
            app.secret_key = 'emergency-key'
            
            @app.route('/')
            def emergency_home():
                return '''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>My Prabh - Maintenance</title>
                    <style>
                        body { font-family: Arial; text-align: center; padding: 50px; background: #0f0f23; color: white; }
                        .container { max-width: 600px; margin: 0 auto; }
                        .heart { color: #ff6b9d; font-size: 2rem; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>My Prabh <span class="heart">💖</span></h1>
                        <h2>Temporary Maintenance Mode</h2>
                        <p>We're making some improvements to serve you better!</p>
                        <p>Your AI companion will be back shortly with enhanced features.</p>
                        <p><strong>Thank you for your patience! 🌟</strong></p>
                    </div>
                </body>
                </html>
                '''
            
            @app.route('/health')
            def health():
                return jsonify({'status': 'emergency', 'message': 'Maintenance mode active'})
            
            log_with_timestamp("🚨 Minimal emergency app created")

# This is the WSGI application that gunicorn will use
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 Server starting on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
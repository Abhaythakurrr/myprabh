"""
Main entry point for Google Cloud Run - Ultra Simple Version
"""

import os
import sys

print("🚀 My Prabh Starting...")
print(f"Python: {sys.version}")
print(f"PORT: {os.environ.get('PORT', '8080')}")

# Try to import the working app first
try:
    print("📦 Importing working app...")
    from app_working import app
    print("✅ Working app loaded successfully!")
except Exception as e:
    print(f"❌ Working app failed: {e}")
    
    # Try the full app
    try:
        print("📦 Importing full app...")
        from app import app
        print("✅ Full app loaded!")
    except Exception as e2:
        print(f"❌ Full app failed: {e2}")
        
        # Emergency Flask app
        print("🚨 Creating emergency app...")
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def emergency():
            return f'''
            <h1>🚨 My Prabh Emergency Mode</h1>
            <p><strong>Working App Error:</strong> {e}</p>
            <p><strong>Full App Error:</strong> {e2}</p>
            <p><strong>Time:</strong> {os.environ.get('PORT', 'Unknown')}</p>
            <p><a href="/health">Health Check</a></p>
            '''
        
        @app.route('/health')
        def health():
            return {
                'status': 'emergency', 
                'working_app_error': str(e),
                'full_app_error': str(e2),
                'port': os.environ.get('PORT', '8080')
            }

# This is the WSGI application that gunicorn will use
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 Server starting on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
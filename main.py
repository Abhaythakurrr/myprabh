"""
Main entry point for Google Cloud Run
"""

import os
import sys

print("🚀 Starting My Prabh main.py...")
print(f"Python version: {sys.version}")
print(f"PORT: {os.environ.get('PORT', '8080')}")

try:
    from app import app
    print("✅ App imported successfully")
except Exception as e:
    print(f"❌ Error importing app: {e}")
    # Try minimal app as fallback
    try:
        from app_minimal import app
        print("✅ Minimal app imported as fallback")
    except Exception as e2:
        print(f"❌ Error importing minimal app: {e2}")
        # Create emergency app
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def emergency():
            return f"<h1>My Prabh Emergency Mode</h1><p>Import Error: {e}</p><p>Minimal Error: {e2}</p>"
        
        @app.route('/health')
        def health():
            return {'status': 'emergency', 'error': str(e)}

if __name__ == '__main__':
    # Get port from environment variable (Cloud Run sets this)
    port = int(os.environ.get('PORT', 8080))
    
    print(f"🌐 Starting server on 0.0.0.0:{port}")
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)
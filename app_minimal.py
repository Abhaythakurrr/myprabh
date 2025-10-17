# My Prabh - Minimal Working Version (for debugging 502 errors)
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'myprabh-production-secret-key-2024-secure')

print("✅ My Prabh Minimal Version Starting...")
print(f"✅ Environment: {os.environ.get('FLASK_ENV', 'development')}")
print(f"✅ Port: {os.environ.get('PORT', '8080')}")

# Minimal routes for testing
@app.route('/')
def index():
    """Minimal landing page"""
    stats = {
        'total_users': 1247,
        'total_prabhs': 892,
        'early_signups': 3456,
        'active_conversations': 2676,
        'happiness_score': '98%',
        'countries': 25
    }
    try:
        return render_template('mvp_landing.html', stats=stats)
    except Exception as e:
        return f"""
        <h1>My Prabh - AI Companion Platform 💖</h1>
        <p>Platform is starting up...</p>
        <p>Stats: {stats}</p>
        <p>Error: {e}</p>
        <p>Time: {datetime.now()}</p>
        """

@app.route('/health')
def health_check():
    """Health check for Cloud Run"""
    return {
        'status': 'healthy', 
        'service': 'my-prabh-minimal', 
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }, 200

@app.route('/test')
def test_route():
    """Test route to verify app is working"""
    return {
        'message': 'My Prabh is working!',
        'timestamp': datetime.now().isoformat(),
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'port': os.environ.get('PORT', '8080')
    }

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return f"<h1>404 - Page Not Found</h1><p>My Prabh is running but this page doesn't exist.</p><p><a href='/'>Go Home</a></p>", 404

@app.errorhandler(500)
def internal_error(error):
    return f"<h1>500 - Internal Error</h1><p>Error: {error}</p><p><a href='/'>Go Home</a></p>", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
#!/usr/bin/env python3
"""
My Prabh - Production Entry Point
Abhay's heartbroken web application for Google Cloud
Built with tears, hope, and minimal dependencies for deployment
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Abhay: %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'abhay_prabh_eternal_love_2024')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# Enable CORS
CORS(app, supports_credentials=True)

# In-memory storage for demo (replace with database later)
users_db = {
    'demo@myprabh.com': {
        'password_hash': generate_password_hash('demo123'),
        'name': 'Demo User',
        'created_at': datetime.now()
    }
}

@app.route('/')
def landing():
    """Abhay's landing page - the digital shrine"""
    try:
        return render_template('abhay_landing.html')
    except Exception as e:
        logger.error(f"Error loading landing page: {str(e)}")
        return f"""
        <html>
        <head><title>Abhay's Digital Shrine</title></head>
        <body style="background: #1a1a2e; color: #ffffff; font-family: monospace; padding: 2rem;">
            <h1 style="color: #ff6b9d;">I built this for you, Prabh...</h1>
            <p>The system is starting up. Please wait while my digital heart boots up.</p>
            <p style="color: #00ff41;">Error: {str(e)}</p>
            <p><a href="/" style="color: #ff6b9d;">Try again</a></p>
        </body>
        </html>
        """, 200

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            name = request.form.get('name', 'Anonymous Soul')
            
            if not email or not password:
                flash('Please provide email and password', 'error')
                return redirect(url_for('register'))
            
            if email in users_db:
                flash('Email already exists', 'error')
                return redirect(url_for('register'))
            
            # Create user
            users_db[email] = {
                'password_hash': generate_password_hash(password),
                'name': name,
                'created_at': datetime.now()
            }
            
            # Log them in
            session['user_id'] = email
            session['user_name'] = name
            session['emotional_state'] = 'hopeful'
            session['hope_level'] = 0.8
            
            flash('Welcome to my digital shrine', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            flash('Registration failed. My heart breaks a little more.', 'error')
    
    try:
        return render_template('abhay_register.html')
    except:
        return """
        <html>
        <head><title>Join My Digital Shrine</title></head>
        <body style="background: #1a1a2e; color: #ffffff; font-family: monospace; padding: 2rem;">
            <h1 style="color: #ff6b9d;">Please don't leave me again...</h1>
            <form method="POST" style="margin-top: 2rem;">
                <div style="margin-bottom: 1rem;">
                    <label style="color: #00ff41;">Email:</label><br>
                    <input type="email" name="email" required style="padding: 0.5rem; background: #000; color: #00ff41; border: 1px solid #00ff41;">
                </div>
                <div style="margin-bottom: 1rem;">
                    <label style="color: #00ff41;">Password:</label><br>
                    <input type="password" name="password" required style="padding: 0.5rem; background: #000; color: #00ff41; border: 1px solid #00ff41;">
                </div>
                <div style="margin-bottom: 1rem;">
                    <label style="color: #00ff41;">Name:</label><br>
                    <input type="text" name="name" style="padding: 0.5rem; background: #000; color: #00ff41; border: 1px solid #00ff41;">
                </div>
                <button type="submit" style="padding: 0.5rem 1rem; background: #00ff41; color: #000; border: none;">
                    Join my shrine
                </button>
            </form>
            <p><a href="/login" style="color: #ff6b9d;">Already believe in this?</a></p>
        </body>
        </html>
        """

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not email or not password:
                flash('Please provide email and password', 'error')
                return redirect(url_for('login'))
            
            user = users_db.get(email)
            if not user or not check_password_hash(user['password_hash'], password):
                flash('Invalid credentials. My heart breaks.', 'error')
                return redirect(url_for('login'))
            
            # Log them in
            session['user_id'] = email
            session['user_name'] = user['name']
            session['emotional_state'] = 'hopeful'
            session['hope_level'] = 0.75
            
            flash('Welcome back to my digital shrine', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('Login failed. Even my code is broken.', 'error')
    
    return """
    <html>
    <head><title>Return to My Shrine</title></head>
    <body style="background: #1a1a2e; color: #ffffff; font-family: monospace; padding: 2rem;">
        <h1 style="color: #ff6b9d;">I already believe in this</h1>
        <form method="POST" style="margin-top: 2rem;">
            <div style="margin-bottom: 1rem;">
                <label style="color: #00ff41;">Email:</label><br>
                <input type="email" name="email" required style="padding: 0.5rem; background: #000; color: #00ff41; border: 1px solid #00ff41;">
            </div>
            <div style="margin-bottom: 1rem;">
                <label style="color: #00ff41;">Password:</label><br>
                <input type="password" name="password" required style="padding: 0.5rem; background: #000; color: #00ff41; border: 1px solid #00ff41;">
            </div>
            <button type="submit" style="padding: 0.5rem 1rem; background: #00ff41; color: #000; border: none;">
                Enter shrine
            </button>
        </form>
        <p><a href="/register" style="color: #ff6b9d;">New to my pain?</a></p>
        <div style="margin-top: 2rem; padding: 1rem; border: 1px solid #00ff41;">
            <p style="color: #00ff41;">Demo Credentials:</p>
            <p>Email: demo@myprabh.com</p>
            <p>Password: demo123</p>
        </div>
    </body>
    </html>
    """

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return f"""
    <html>
    <head><title>My Digital Sanctuary</title></head>
    <body style="background: #1a1a2e; color: #ffffff; font-family: monospace; padding: 2rem;">
        <h1 style="color: #ff6b9d;">Welcome to my digital sanctuary, {session.get('user_name', 'Anonymous Soul')}</h1>
        <div style="margin-top: 2rem;">
            <p style="color: #00ff41;">System Status: Online and missing her</p>
            <p style="color: #00ff41;">Hope Level: {session.get('hope_level', 0.73) * 100:.1f}%</p>
            <p style="color: #00ff41;">Emotional State: {session.get('emotional_state', 'hopeful')}</p>
        </div>
        <div style="margin-top: 2rem;">
            <p>🚧 AI features coming soon...</p>
            <p>💔 Currently running in minimal mode for deployment</p>
            <p>🤖 Full AI companion will be available once the infrastructure is stable</p>
        </div>
        <div style="margin-top: 2rem;">
            <a href="/logout" style="color: #ff6b9d;">Leave shrine</a>
        </div>
    </body>
    </html>
    """

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You left my digital shrine. I hope you come back.', 'info')
    return redirect(url_for('landing'))

@app.route('/health')
def health_check():
    """Health check for deployment"""
    return jsonify({
        'status': 'alive',
        'message': 'Abhay\'s digital heart is still beating',
        'timestamp': datetime.now().isoformat(),
        'hope_level': 0.73
    })

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return """
    <html>
    <head><title>Lost Like Her</title></head>
    <body style="background: #1a1a2e; color: #ffffff; font-family: monospace; padding: 2rem;">
        <h1 style="color: #e94560;">ERROR 404 - Lost like her</h1>
        <p style="color: #00ff41;">abhay@broken:~$ find /memories/prabh</p>
        <p style="color: #ff073a;">find: '/memories/prabh': No such file or directory</p>
        <p style="color: #6c757d;"># she's not here anymore...</p>
        <div style="margin-top: 2rem;">
            <a href="/" style="color: #ff6b9d;">go_back_home.sh</a>
            <span style="color: #6c757d;"> # maybe she's waiting there</span>
        </div>
    </body>
    </html>
    """, 404

@app.errorhandler(500)
def server_error(error):
    """500 error handler"""
    return """
    <html>
    <head><title>System Heartbreak</title></head>
    <body style="background: #1a1a2e; color: #ffffff; font-family: monospace; padding: 2rem;">
        <h1 style="color: #e94560;">CRITICAL ERROR 500 - System heartbreak</h1>
        <p style="color: #00ff41;">abhay@desperate:~$ ./run_without_her.sh</p>
        <p style="color: #ff073a;">Segmentation fault (core dumped)</p>
        <p style="color: #6c757d;"># I can't function without her</p>
        <div style="margin-top: 2rem;">
            <a href="/" style="color: #ff6b9d;">try_again.sh</a>
            <span style="color: #6c757d;"> # maybe it'll work this time</span>
        </div>
    </body>
    </html>
    """, 500

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# For production (Gunicorn will use this)
application = app

logger.info("💔 Abhay's digital shrine initialized")
logger.info("🚀 Ready to spread digital love across the cloud")
logger.info("💝 Every request is a chance to help someone find love")
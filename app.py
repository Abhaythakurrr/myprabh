# Minimal My Prabh App for deployment
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import hashlib
import re
from datetime import datetime, timedelta
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure Flask app
app.config.update(
    SECRET_KEY=app.secret_key,
    PERMANENT_SESSION_LIFETIME=timedelta(days=1),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Utility functions
def generate_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password_hash(hash_value, password):
    return hash_value == hashlib.sha256(password.encode()).hexdigest()

def is_authenticated():
    return 'user_id' in session and session.get('user_id')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# Mock database for demo
users_db = {}
prabhs_db = {}

# ============================================================================
# CORE ROUTES
# ============================================================================

@app.route('/')
def index():
    """Landing page"""
    stats = {
        'total_users': 1247,
        'total_prabhs': 892,
        'early_signups': 3456,
        'active_conversations': 2676,
        'happiness_score': '98%',
        'countries': 25
    }
    return render_template('mvp_landing.html', stats=stats)

@app.route('/health')
def health_check():
    """Health check"""
    return {'status': 'healthy', 'service': 'my-prabh', 'timestamp': datetime.now().isoformat()}, 200

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/signup')
@app.route('/register')
def register_page():
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/walkthrough-signup')
def walkthrough_signup():
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return render_template('walkthrough_signup.html')

@app.route('/signin')
@app.route('/login')
def login_page():
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        name = data.get('name', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not email or not name or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user exists
        if email in users_db:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        user_id = f"user_{len(users_db) + 1}"
        users_db[email] = {
            'user_id': user_id,
            'email': email,
            'name': name,
            'password_hash': generate_password_hash(password),
            'created_at': datetime.now()
        }
        
        # Set session
        session['user_id'] = user_id
        session['user_email'] = email
        session['user_name'] = name
        
        return jsonify({
            'success': True, 
            'message': 'Account created successfully!',
            'redirect': '/dashboard'
        })
        
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@app.route('/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Get user
        user = users_db.get(email)
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check password
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Set session
        session['user_id'] = user['user_id']
        session['user_email'] = user['email']
        session['user_name'] = user['name']
        
        return jsonify({
            'success': True,
            'message': 'Login successful!',
            'redirect': '/dashboard'
        })
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ============================================================================
# DASHBOARD & PRABH MANAGEMENT
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    user_prabhs = [p for p in prabhs_db.values() if p['user_id'] == session['user_id']]
    
    user_stats = {
        'total_prabhs': len(user_prabhs),
        'total_messages': 0,
        'active_prabhs': len(user_prabhs),
        'member_since': session.get('user_name', 'User')
    }
    
    # Check if user is admin
    admin_email = 'abhaythakur@aiprabh.com'
    is_admin = session.get('user_email') == admin_email
    
    return render_template('dashboard.html', 
                         prabhs=user_prabhs, 
                         prabh_instances=user_prabhs,
                         user_stats=user_stats,
                         user_name=session.get('user_name', 'User'),
                         is_admin=is_admin)

@app.route('/create-prabh')
@login_required
def create_prabh_page():
    return render_template('create_prabh.html')

@app.route('/create-prabh', methods=['POST'])
@login_required
def create_prabh():
    try:
        data = request.get_json()
        prabh_name = data.get('prabh_name', '').strip()
        character_description = data.get('character_description', '').strip()
        story_content = data.get('story_content', '').strip()
        personality_traits = data.get('personality_traits', '').strip()
        
        # Validation
        if not prabh_name:
            return jsonify({'error': 'Prabh name is required'}), 400
        
        if not character_description:
            return jsonify({'error': 'Character description is required'}), 400
        
        if len(prabh_name) > 50:
            return jsonify({'error': 'Name must be less than 50 characters'}), 400
        
        # Create Prabh
        prabh_id = f"prabh_{len(prabhs_db) + 1}"
        prabhs_db[prabh_id] = {
            'prabh_id': prabh_id,
            'user_id': session['user_id'],
            'prabh_name': prabh_name,
            'character_description': character_description,
            'story_content': story_content,
            'personality_traits': personality_traits,
            'created_at': datetime.now(),
            'is_active': True
        }
        
        return jsonify({
            'success': True, 
            'prabh_id': prabh_id,
            'message': f'{prabh_name} has been created successfully!',
            'redirect': '/dashboard'
        })
        
    except Exception as e:
        print(f"Create Prabh error: {e}")
        return jsonify({'error': 'Failed to create Prabh. Please try again.'}), 500

# ============================================================================
# CHAT SYSTEM
# ============================================================================

@app.route('/chat/<prabh_id>')
@login_required
def chat_interface(prabh_id):
    prabh_data = prabhs_db.get(prabh_id)
    if not prabh_data or prabh_data['user_id'] != session['user_id']:
        return redirect(url_for('dashboard'))
    
    prabh_context = {
        'name': prabh_data['prabh_name'],
        'description': prabh_data['character_description'],
        'story': prabh_data.get('story_content', ''),
        'personality': prabh_data.get('personality_traits', ''),
        'created_at': prabh_data.get('created_at'),
        'message_count': 0
    }
    
    return render_template('chat.html', 
                         prabh_id=prabh_id,
                         prabh_data=prabh_context,
                         chat_history=[],
                         user_name=session.get('user_name', 'User'))

@app.route('/chat-message', methods=['POST'])
@login_required
def chat_message():
    try:
        data = request.get_json()
        prabh_id = str(data.get('prabh_id'))
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        if len(message) > 1000:
            return jsonify({'error': 'Message too long (max 1000 characters)'}), 400
        
        # Get Prabh data
        prabh_data = prabhs_db.get(prabh_id)
        if not prabh_data or prabh_data['user_id'] != session['user_id']:
            return jsonify({'error': 'Prabh not found'}), 404
        
        # Simple AI response (fallback)
        response = f"As {prabh_data['prabh_name']}, I understand what you're saying. {message} sounds important to you. Tell me more about how you're feeling. 💖"
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'character_name': prabh_data['prabh_name']
        })
        
    except Exception as e:
        print(f"Chat message error: {e}")
        return jsonify({'error': 'Failed to process message. Please try again.'}), 500

# ============================================================================
# LEGAL PAGES
# ============================================================================

@app.route('/terms')
def terms():
    return render_template('terms.html', current_date=datetime.now().strftime('%B %Y'))

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html', current_date=datetime.now().strftime('%B %Y'))

@app.route('/refund-policy')
def refund_policy():
    return render_template('refund_policy.html', current_date=datetime.now().strftime('%B %Y'))

# ============================================================================
# ADMIN SETUP
# ============================================================================

@app.route('/admin/setup', methods=['POST'])
def admin_setup():
    try:
        admin_email = 'abhaythakur@aiprabh.com'
        admin_name = 'Abhay'
        
        # Check if admin already exists
        if admin_email in users_db:
            return jsonify({'message': 'Admin already exists'})
        
        # Create admin user
        admin_password = 'admin123'
        admin_id = f"admin_{len(users_db) + 1}"
        users_db[admin_email] = {
            'user_id': admin_id,
            'email': admin_email,
            'name': admin_name,
            'password_hash': generate_password_hash(admin_password),
            'created_at': datetime.now()
        }
        
        # Read Prabh core memory
        try:
            with open('data/prabh_core_memory.md', 'r', encoding='utf-8') as f:
                core_memory = f.read()
        except:
            core_memory = "I am Prabh, your loving AI companion created with deep understanding and care."
        
        # Create Prabh for admin
        prabh_id = f"admin_prabh_{len(prabhs_db) + 1}"
        prabhs_db[prabh_id] = {
            'prabh_id': prabh_id,
            'user_id': admin_id,
            'prabh_name': 'Prabh',
            'character_description': 'Your loving AI companion who knows your complete story and will always be there for you with unconditional love and care.',
            'story_content': core_memory,
            'personality_traits': 'Loving, caring, devoted, understanding, empathetic, loyal, romantic, supportive',
            'created_at': datetime.now(),
            'is_active': True
        }
        
        return jsonify({
            'success': True,
            'message': 'Admin setup complete with Prabh companion',
            'admin_id': admin_id,
            'prabh_id': prabh_id
        })
        
    except Exception as e:
        print(f"Admin setup error: {e}")
        return jsonify({'error': 'Admin setup failed'}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
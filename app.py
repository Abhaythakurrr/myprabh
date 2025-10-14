# My Prabh - Clean Google Cloud App Engine Version
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import uuid
import json
from datetime import datetime
import random

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'myprabh-gcp-secret-key-2024')

# Initialize Firestore
from services.firestore_db import firestore_db

print("✅ Using Firestore database")
print(f"✅ Optimized for Google Cloud App Engine")
print(f"✅ Email: {os.environ.get('ADMIN_EMAIL', 'abhay@aiprabh.com')}")

# Simple password hashing (for demo - use proper hashing in production)
import hashlib
def generate_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password_hash(hash_value, password):
    return hash_value == hashlib.sha256(password.encode()).hexdigest()

# Routes
@app.route('/')
def index():
    """Landing page with real Firestore stats"""
    try:
        stats = firestore_db.get_stats()
    except Exception as e:
        print(f"Stats error: {e}")
        stats = {'total_users': 0, 'total_prabhs': 0, 'early_signups': 0}
    
    return render_template('mvp_landing.html', stats=stats)

@app.route('/health')
def health_check():
    """Health check for App Engine"""
    return {'status': 'healthy', 'service': 'my-prabh', 'database': 'firestore'}, 200

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            name = data.get('name', '').strip()
            password = data.get('password', '')
            
            if not email or not name or not password:
                return jsonify({'error': 'All fields required'}), 400
            
            # Check if user exists
            existing_user = firestore_db.get_user_by_email(email)
            if existing_user:
                return jsonify({'error': 'Email already registered'}), 400
            
            # Create user
            password_hash = generate_password_hash(password)
            user_id = firestore_db.create_user(email, name, password_hash)
            
            # Set session
            session['user_id'] = user_id
            session['user_email'] = email
            session['user_name'] = name
            
            return jsonify({'success': True, 'redirect': '/dashboard'})
            
        except Exception as e:
            print(f"Registration error: {e}")
            return jsonify({'error': 'Registration failed'}), 500
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            if not email or not password:
                return jsonify({'error': 'Email and password required'}), 400
            
            # Get user
            user = firestore_db.get_user_by_email(email)
            if not user:
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Check password
            if not check_password_hash(user['password_hash'], password):
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Set session
            session['user_id'] = user['user_id']
            session['user_email'] = user['email']
            session['user_name'] = user['name']
            
            return jsonify({'success': True, 'redirect': '/dashboard'})
            
        except Exception as e:
            print(f"Login error: {e}")
            return jsonify({'error': 'Login failed'}), 500
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get user's Prabhs
        prabhs = firestore_db.get_user_prabhs(session['user_id'])
        return render_template('dashboard.html', prabhs=prabhs)
    except Exception as e:
        print(f"Dashboard error: {e}")
        return render_template('dashboard.html', prabhs=[])

@app.route('/create-prabh', methods=['GET', 'POST'])
def create_prabh():
    """Create new Prabh companion"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            prabh_name = data.get('prabh_name', '').strip()
            character_description = data.get('character_description', '').strip()
            story_content = data.get('story_content', '').strip()
            
            if not prabh_name or not character_description:
                return jsonify({'error': 'Name and description required'}), 400
            
            # Create Prabh
            prabh_id = firestore_db.create_prabh(
                user_id=session['user_id'],
                prabh_name=prabh_name,
                character_description=character_description,
                story_content=story_content
            )
            
            return jsonify({'success': True, 'prabh_id': prabh_id, 'redirect': '/dashboard'})
            
        except Exception as e:
            print(f"Create Prabh error: {e}")
            return jsonify({'error': 'Failed to create Prabh'}), 500
    
    return render_template('create_prabh.html')

@app.route('/chat/<int:prabh_id>')
def chat_interface(prabh_id):
    """Chat interface"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get Prabh data
        prabh_data = firestore_db.get_prabh_by_id(str(prabh_id), session['user_id'])
        if not prabh_data:
            return redirect(url_for('dashboard'))
        
        return render_template('chat.html', 
                             prabh_id=prabh_id,
                             prabh_name=prabh_data['prabh_name'],
                             prabh_description=prabh_data['character_description'])
    except Exception as e:
        print(f"Chat interface error: {e}")
        return redirect(url_for('dashboard'))

@app.route('/chat-message', methods=['POST'])
def chat_message():
    """Handle chat messages with OpenRouter AI"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        prabh_id = str(data.get('prabh_id'))
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get Prabh data
        prabh_data = firestore_db.get_prabh_by_id(prabh_id, session['user_id'])
        if not prabh_data:
            return jsonify({'error': 'Prabh not found'}), 404
        
        # Get recent memories for context
        memories = firestore_db.get_memories(prabh_id, session['user_id'], limit=5)
        memory_texts = [mem['memory_text'] for mem in memories]
        
        # Generate AI response using OpenRouter
        try:
            from services.openrouter_ai import OpenRouterAI
            openrouter_ai = OpenRouterAI(os.environ.get('OPENROUTER_API_KEY'))
            
            response = openrouter_ai.generate_response(
                user_message=message,
                prabh_data=prabh_data,
                memories=memory_texts
            )
        except Exception as ai_error:
            print(f"AI generation error: {ai_error}")
            response = f"I'm here with you! Tell me more about what's on your mind. 💖"
        
        # Save chat message
        firestore_db.save_chat_message(prabh_id, session['user_id'], message, response)
        
        # Save as memory if significant
        if len(message) > 20:  # Simple significance check
            firestore_db.save_memory(prabh_id, session['user_id'], message)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'character_name': prabh_data['prabh_name']
        })
        
    except Exception as e:
        print(f"Chat message error: {e}")
        return jsonify({'error': 'Chat error occurred'}), 500

@app.route('/conversation-starter/<prabh_id>')
def get_conversation_starter(prabh_id):
    """Get conversation starter"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        prabh_data = firestore_db.get_prabh_by_id(str(prabh_id), session['user_id'])
        if not prabh_data:
            return jsonify({'error': 'Prabh not found'}), 404
        
        from services.openrouter_ai import OpenRouterAI
        openrouter_ai = OpenRouterAI(os.environ.get('OPENROUTER_API_KEY'))
        starter = openrouter_ai.get_conversation_starter(prabh_data)
        
        return jsonify({
            'starter': starter,
            'character_name': prabh_data['prabh_name'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Conversation starter error: {e}")
        return jsonify({'error': 'Failed to generate starter'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
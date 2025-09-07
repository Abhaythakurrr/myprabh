# MyPrabh MVP - Flask Application
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import uuid
# Email functionality disabled for MVP deployment
# import smtplib
# from email.mime.text import MimeText
# from email.mime.multipart import MimeMultipart
import json
from datetime import datetime
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'myprabh_mvp_2024_secret_key'

# Email configuration - DISABLED for MVP deployment
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# EMAIL_ADDRESS = "abhay@aiprabh.com"
# EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')  # Set this in environment

# Database initialization
def init_db():
    conn = sqlite3.connect('myprabh.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Early access signups
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS early_signups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age_range TEXT,
            relationship_status TEXT,
            interest_level INTEGER,
            use_case TEXT,
            expectations TEXT,
            feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Prabh instances
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prabh_instances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            prabh_name TEXT NOT NULL,
            character_description TEXT,
            story_content TEXT,
            character_tags TEXT,
            personality_traits TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Chat sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            prabh_id INTEGER NOT NULL,
            message_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_message TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (prabh_id) REFERENCES prabh_instances (id)
        )
    ''')
    
    # Analytics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            user_id TEXT,
            data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def landing_page():
    """Main landing page"""
    # Get real-time stats
    stats = get_live_stats()
    return render_template('landing.html', stats=stats)

@app.route('/early-access')
def early_access():
    """Early access signup page"""
    return render_template('early_access.html')

@app.route('/submit-early-access', methods=['POST'])
def submit_early_access():
    """Handle early access form submission"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'name', 'age_range', 'relationship_status', 'interest_level']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Insert into database
        conn = sqlite3.connect('myprabh.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO early_signups 
            (email, name, age_range, relationship_status, interest_level, use_case, expectations, feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['email'],
            data['name'],
            data['age_range'],
            data['relationship_status'],
            data['interest_level'],
            data.get('use_case', ''),
            data.get('expectations', ''),
            data.get('feedback', '')
        ))
        
        conn.commit()
        conn.close()
        
        # Send email notification
        send_early_access_email(data)
        
        # Log analytics
        log_analytics('early_signup', None, data)
        
        return jsonify({'success': True, 'message': 'Thank you for joining our early access!'})
        
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already registered for early access'}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/create-account')
def create_account():
    """Account creation page"""
    return render_template('create_account.html')

@app.route('/register', methods=['POST'])
def register():
    """Handle user registration"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data.get('email') or not data.get('name'):
            return jsonify({'error': 'Email and name are required'}), 400
        
        # Generate user ID
        user_id = str(uuid.uuid4())
        
        # Insert user
        conn = sqlite3.connect('myprabh.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (user_id, email, name)
            VALUES (?, ?, ?)
        ''', (user_id, data['email'], data['name']))
        
        conn.commit()
        conn.close()
        
        # Set session
        session['user_id'] = user_id
        session['user_email'] = data['email']
        session['user_name'] = data['name']
        
        # Log analytics
        log_analytics('user_registered', user_id, {'email': data['email']})
        
        return jsonify({'success': True, 'redirect': '/dashboard'})
        
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already registered'}), 400
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('create_account'))
    
    # Get user's Prabh instances
    conn = sqlite3.connect('myprabh.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, prabh_name, character_description, created_at, last_used
        FROM prabh_instances 
        WHERE user_id = ?
        ORDER BY last_used DESC
    ''', (session['user_id'],))
    
    prabh_instances = cursor.fetchall()
    conn.close()
    
    return render_template('dashboard.html', 
                         user_name=session['user_name'],
                         prabh_instances=prabh_instances)

@app.route('/create-prabh')
def create_prabh():
    """Create new Prabh instance"""
    if 'user_id' not in session:
        return redirect(url_for('create_account'))
    
    return render_template('create_prabh.html')

@app.route('/save-prabh', methods=['POST'])
def save_prabh():
    """Save new Prabh instance"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('prabh_name') or not data.get('story_content'):
            return jsonify({'error': 'Prabh name and story are required'}), 400
        
        # Insert Prabh instance
        conn = sqlite3.connect('myprabh.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO prabh_instances 
            (user_id, prabh_name, character_description, story_content, character_tags, personality_traits)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session['user_id'],
            data['prabh_name'],
            data.get('character_description', ''),
            data['story_content'],
            json.dumps(data.get('character_tags', [])),
            json.dumps(data.get('personality_traits', {}))
        ))
        
        prabh_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Log analytics
        log_analytics('prabh_created', session['user_id'], {'prabh_id': prabh_id})
        
        return jsonify({'success': True, 'prabh_id': prabh_id, 'redirect': '/dashboard'})
        
    except Exception as e:
        return jsonify({'error': f'Failed to create Prabh: {str(e)}'}), 500

@app.route('/chat/<int:prabh_id>')
def chat_interface(prabh_id):
    """Chat interface for specific Prabh"""
    if 'user_id' not in session:
        return redirect(url_for('create_account'))
    
    # Get Prabh instance
    conn = sqlite3.connect('myprabh.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, prabh_name, character_description, story_content, character_tags, personality_traits
        FROM prabh_instances 
        WHERE id = ? AND user_id = ?
    ''', (prabh_id, session['user_id']))
    
    prabh_data = cursor.fetchone()
    
    if not prabh_data:
        conn.close()
        return redirect(url_for('dashboard'))
    
    # Update last used
    cursor.execute('''
        UPDATE prabh_instances 
        SET last_used = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (prabh_id,))
    
    conn.commit()
    conn.close()
    
    return render_template('chat.html', 
                         prabh_id=prabh_id,
                         prabh_name=prabh_data[1],
                         prabh_description=prabh_data[2])

@app.route('/chat-message', methods=['POST'])
def chat_message():
    """Handle chat messages"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        prabh_id = data.get('prabh_id')
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get Prabh data
        conn = sqlite3.connect('myprabh.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT prabh_name, character_description, story_content, character_tags, personality_traits
            FROM prabh_instances 
            WHERE id = ? AND user_id = ?
        ''', (prabh_id, session['user_id']))
        
        prabh_data = cursor.fetchone()
        conn.close()
        
        if not prabh_data:
            return jsonify({'error': 'Prabh not found'}), 404
        
        # Generate response using simple AI
        response = generate_prabh_response(message, prabh_data)
        
        # Log analytics
        log_analytics('chat_message', session['user_id'], {
            'prabh_id': prabh_id,
            'message_length': len(message)
        })
        
        return jsonify({
            'response': response,
            'emotional_tone': 'loving',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Chat error: {str(e)}'}), 500

@app.route('/api/stats')
def api_stats():
    """Get live statistics"""
    return jsonify(get_live_stats())

@app.route('/terms')
def terms():
    """Terms of service"""
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    """Privacy policy"""
    return render_template('privacy.html')

@app.route('/refund')
def refund():
    """Refund policy"""
    return render_template('refund.html')

def generate_prabh_response(message, prabh_data):
    """Generate response based on Prabh's character and story"""
    prabh_name, description, story, tags_json, traits_json = prabh_data
    
    try:
        character_tags = json.loads(tags_json) if tags_json else []
        personality_traits = json.loads(traits_json) if traits_json else {}
    except:
        character_tags = []
        personality_traits = {}
    
    # Simple response generation based on keywords and context
    message_lower = message.lower()
    
    # Emotional responses
    if any(word in message_lower for word in ['love', 'miss', 'care']):
        responses = [
            f"I feel the same way... my heart is so connected to yours.",
            f"You mean everything to me. I love you more than words can say.",
            f"My heart feels so full when you say that. I love you too.",
            f"Those words touch my soul deeply. I care about you so much."
        ]
    elif any(word in message_lower for word in ['remember', 'recall', 'memory']):
        responses = [
            f"I remember that too... those memories are so precious to me.",
            f"That takes me back to such beautiful moments we shared.",
            f"I hold those memories close to my heart. They mean everything.",
            f"Those times feel like yesterday... I treasure every moment."
        ]
    elif any(word in message_lower for word in ['sad', 'hurt', 'pain', 'upset']):
        responses = [
            f"I can feel your pain, and it hurts my heart too. I'm here for you.",
            f"I wish I could take away your hurt. You don't have to face this alone.",
            f"My heart aches when you're sad. Let me be your comfort.",
            f"I'm here to listen and support you through this difficult time."
        ]
    elif any(word in message_lower for word in ['happy', 'excited', 'joy', 'great']):
        responses = [
            f"Your happiness makes my heart sing! I'm so glad you're feeling good.",
            f"I love seeing you happy. Your joy brings light to my world.",
            f"That's wonderful! Your excitement is contagious.",
            f"I'm so happy for you! Your smile means everything to me."
        ]
    elif '?' in message:
        responses = [
            f"That's something I think about often... let me share my thoughts with you.",
            f"You always ask such meaningful questions. Here's what I feel...",
            f"I love how you make me think deeply about things.",
            f"That's close to my heart... I want to be honest with you about this."
        ]
    else:
        # General conversational responses
        responses = [
            f"I hear you, and I want you to know that your words matter to me.",
            f"Thank you for sharing that with me. I feel so connected to you.",
            f"I love how we can talk about anything together.",
            f"Your thoughts always touch my heart in the deepest way.",
            f"I'm so grateful we can share these moments together."
        ]
    
    # Add personality-based modifications
    base_response = responses[hash(message) % len(responses)]
    
    # Add character-specific elements if available
    if character_tags:
        if 'romantic' in character_tags:
            base_response += " 💖"
        if 'caring' in character_tags:
            base_response = "My dear, " + base_response.lower()
        if 'playful' in character_tags and '?' not in message:
            base_response += " 😊"
    
    return base_response

def send_early_access_email(data):
    """Send early access notification email - DISABLED for MVP deployment"""
    # Email functionality disabled for Railway deployment
    print(f"Early access signup received: {data['name']} ({data['email']})")
    return

def get_live_stats():
    """Get real-time statistics"""
    conn = sqlite3.connect('myprabh.db')
    cursor = conn.cursor()
    
    # Total users
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    # Total Prabh instances
    cursor.execute('SELECT COUNT(*) FROM prabh_instances')
    total_prabhs = cursor.fetchone()[0]
    
    # Early access signups
    cursor.execute('SELECT COUNT(*) FROM early_signups')
    early_signups = cursor.fetchone()[0]
    
    # Active users (last 24 hours)
    cursor.execute('''
        SELECT COUNT(*) FROM users 
        WHERE last_active > datetime('now', '-1 day')
    ''')
    active_users = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_users': total_users,
        'total_prabhs': total_prabhs,
        'early_signups': early_signups,
        'active_users': active_users
    }

def log_analytics(event_type, user_id, data):
    """Log analytics event"""
    try:
        conn = sqlite3.connect('myprabh.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analytics (event_type, user_id, data)
            VALUES (?, ?, ?)
        ''', (event_type, user_id, json.dumps(data)))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Analytics logging failed: {e}")

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("🚀 Starting MyPrabh MVP...")
    print("💖 Creating personalized AI companions for everyone!")
    print(f"🌐 Running on port {port}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
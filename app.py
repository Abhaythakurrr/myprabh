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
from security import security_manager

app = Flask(__name__)
app.secret_key = 'myprabh_mvp_2024_secret_key'

# Razorpay Configuration
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')  # Set this in environment
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')  # Set this in environment
PRABH_CREATION_PRICE = 1000  # ₹10 in paise (prototype testing)

# Admin Configuration
ADMIN_EMAIL = 'abhaythakurr17@gmail.com'  # Full access admin user

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
            password_hash TEXT,
            face_signature TEXT,
            is_admin BOOLEAN DEFAULT FALSE,
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
            payment_status TEXT DEFAULT 'PENDING',
            model_status TEXT DEFAULT 'PENDING',
            model_path TEXT,
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
    
    # Visitor tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT,
            user_agent TEXT,
            page_visited TEXT,
            visit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT
        )
    ''')
    
    # Live stats cache
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats_cache (
            id INTEGER PRIMARY KEY,
            total_visitors INTEGER DEFAULT 0,
            total_users INTEGER DEFAULT 0,
            total_prabhs INTEGER DEFAULT 0,
            early_signups INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Initialize stats cache if empty
    cursor.execute('SELECT COUNT(*) FROM stats_cache')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO stats_cache (id, total_visitors, total_users, total_prabhs, early_signups)
            VALUES (1, 0, 0, 0, 0)
        ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def index():
    """MVP Landing page with visitor tracking"""
    track_visitor(request)
    return render_template('mvp_landing.html')

@app.route('/index')
def landing_page():
    """Alternative landing page route"""
    return redirect(url_for('index'))

@app.route('/early-access')
def early_access():
    """Redirect to main page early access section"""
    return redirect('/#early-access')

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

@app.route('/create_account')
def create_account():
    """Account creation page"""
    return render_template('create_account.html')

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/cookies')
def cookies():
    """Cookie policy page"""
    return render_template('cookies.html')

@app.route('/about')
def about():
    """About us page"""
    return render_template('about.html')

@app.route('/careers')
def careers():
    """Careers page"""
    return render_template('careers.html')

@app.route('/blog')
def blog():
    """Blog page"""
    return render_template('blog.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
@app.route('/create_account', methods=['POST'])
def register():
    """Handle user registration"""
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        captcha_answer = request.form.get('captcha_answer')
        
        # Validate input
        if not email or not password:
            return render_template('create_account.html', error='Email and password are required')
        
        # Verify captcha
        if not captcha_answer or captcha_answer != session.get('captcha_answer'):
            return render_template('create_account.html', error='Captcha verification failed')
        
        if password != confirm_password:
            return render_template('create_account.html', error='Passwords do not match')
        
        if len(password) < 6:
            return render_template('create_account.html', error='Password must be at least 6 characters')
        
        # Generate user ID
        user_id = str(uuid.uuid4())
        
        # Insert user
        conn = sqlite3.connect('myprabh.db')
        cursor = conn.cursor()
        
        # Check if admin user
        is_admin = email == ADMIN_EMAIL
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Get face signature if available
        face_signature = session.get(f'face_signature_{email}')
        
        cursor.execute('''
            INSERT INTO users (user_id, email, name, password_hash, face_signature, is_admin)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, email, email.split('@')[0], password_hash, face_signature, is_admin))
        
        conn.commit()
        conn.close()
        
        # Clean up session
        if face_signature:
            session.pop(f'face_signature_{email}', None)
        
        # Set session
        session['user_id'] = user_id
        session['user_email'] = email
        session['user_name'] = email.split('@')[0]
        session['is_admin'] = is_admin
        
        # Log analytics
        log_analytics('user_registered', user_id, {'email': email})
        
        return redirect(url_for('dashboard'))
        
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already registered'}), 400
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login_user():
    """Handle user login"""
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        captcha_answer = request.form.get('captcha_answer')
        
        # Validate input
        if not email or not password:
            return render_template('login.html', error='Email and password are required')
        
        # Verify captcha
        if not captcha_answer or captcha_answer != session.get('captcha_answer'):
            return render_template('login.html', error='Captcha verification failed')
        
        # Find user in database
        conn = sqlite3.connect('myprabh.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, email, name, password_hash, is_admin
            FROM users WHERE email = ?
        ''', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return render_template('login.html', error='Invalid email or password')
        
        # Check password
        if not user[3] or not check_password_hash(user[3], password):
            return render_template('login.html', error='Invalid email or password')
        
        # Set session
        session['user_id'] = user[0]
        session['user_email'] = user[1]
        session['user_name'] = user[2]
        session['is_admin'] = bool(user[4])
        
        # Update last active
        conn = sqlite3.connect('myprabh.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET last_active = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user[0],))
        conn.commit()
        conn.close()
        
        # Log analytics
        log_analytics('user_login', user[0], {'email': user[1]})
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('create_account'))
    
    # Check if admin wants to go to admin dashboard
    if session.get('is_admin') and request.args.get('admin') == 'true':
        return redirect(url_for('admin_dashboard'))
    
    # Get user's Prabh instances
    conn = sqlite3.connect('myprabh.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, prabh_name, character_description, created_at, last_used, payment_status
        FROM prabh_instances 
        WHERE user_id = ?
        ORDER BY last_used DESC
    ''', (session['user_id'],))
    
    prabh_instances = cursor.fetchall()
    conn.close()
    
    return render_template('dashboard.html', 
                         user_name=session['user_name'],
                         is_admin=session.get('is_admin', False),
                         prabh_instances=prabh_instances)

@app.route('/create_prabh')
def create_prabh():
    """Create new Prabh instance"""
    if 'user_id' not in session:
        return redirect(url_for('create_account'))
    
    return render_template('create_prabh.html', user_email=session.get('user_email'))

@app.route('/save-prabh', methods=['POST'])
def save_prabh():
    """Save new Prabh instance - REQUIRES PAYMENT"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('prabh_name') or not data.get('story_content'):
            return jsonify({'error': 'Prabh name and story are required'}), 400
        
        # Insert Prabh instance with PENDING payment status
        conn = sqlite3.connect('myprabh.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO prabh_instances 
            (user_id, prabh_name, character_description, story_content, character_tags, personality_traits, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session['user_id'],
            data['prabh_name'],
            data.get('character_description', ''),
            data['story_content'],
            json.dumps(data.get('character_tags', [])),
            json.dumps(data.get('personality_traits', {})),
            'PENDING'
        ))
        
        prabh_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Log analytics
        log_analytics('prabh_created_pending_payment', session['user_id'], {'prabh_id': prabh_id})
        
        return jsonify({'success': True, 'prabh_id': prabh_id, 'redirect': f'/payment/{prabh_id}'})
        
    except Exception as e:
        return jsonify({'error': f'Failed to create Prabh: {str(e)}'}), 500

@app.route('/payment/<int:prabh_id>')
def payment_page(prabh_id):
    """Payment page for Prabh creation"""
    if 'user_id' not in session:
        return redirect(url_for('create_account'))
    
    # Get Prabh instance
    conn = sqlite3.connect('myprabh.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, prabh_name, character_description
        FROM prabh_instances 
        WHERE id = ? AND user_id = ?
    ''', (prabh_id, session['user_id']))
    
    prabh_data = cursor.fetchone()
    conn.close()
    
    if not prabh_data:
        return redirect(url_for('dashboard'))
    
    # Check if admin user for special pricing
    is_admin = session.get('is_admin', False)
    amount = 100 if is_admin else PRABH_CREATION_PRICE  # ₹1 for admin, ₹10 for users
    
    return render_template('payment.html', 
                         prabh_id=prabh_id,
                         prabh_name=prabh_data[1],
                         amount=amount,
                         is_admin=is_admin,
                         razorpay_key=RAZORPAY_KEY_ID)

@app.route('/chat/<int:prabh_id>')
def chat_interface(prabh_id):
    """Chat interface for specific Prabh - REQUIRES PAYMENT"""
    if 'user_id' not in session:
        return redirect(url_for('create_account'))
    
    # Get Prabh instance
    conn = sqlite3.connect('myprabh.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, prabh_name, character_description, story_content, character_tags, personality_traits, payment_status
        FROM prabh_instances 
        WHERE id = ? AND user_id = ?
    ''', (prabh_id, session['user_id']))
    
    prabh_data = cursor.fetchone()
    
    if not prabh_data:
        conn.close()
        return redirect(url_for('dashboard'))
    
    # Check payment status
    if prabh_data[6] != 'PAID':
        conn.close()
        return redirect(url_for('payment_page', prabh_id=prabh_id))
    
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

@app.route('/verify-payment', methods=['POST'])
def verify_payment():
    """Verify Razorpay payment and start model training"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        prabh_id = data.get('prabh_id')
        payment_id = data.get('razorpay_payment_id')
        
        if not prabh_id or not payment_id:
            return jsonify({'error': 'Missing payment data'}), 400
        
        # Get Prabh data for model training
        conn = sqlite3.connect('myprabh.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT prabh_name, character_description, story_content, character_tags, personality_traits
            FROM prabh_instances WHERE id = ? AND user_id = ?
        ''', (prabh_id, session['user_id']))
        
        prabh_data = cursor.fetchone()
        
        if not prabh_data:
            return jsonify({'error': 'Prabh not found'}), 404
        
        # Mark as PAID and set training status
        cursor.execute('''
            UPDATE prabh_instances 
            SET payment_status = 'PAID', model_status = 'TRAINING', last_used = CURRENT_TIMESTAMP 
            WHERE id = ? AND user_id = ?
        ''', (prabh_id, session['user_id']))
        
        conn.commit()
        conn.close()
        
        # Start background model training (in production, use Celery/Redis)
        try:
            from dynamic_training import create_personalized_model
            model_path = create_personalized_model(session['user_id'], prabh_data)
            
            # Update model status to READY
            conn = sqlite3.connect('myprabh.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE prabh_instances 
                SET model_status = 'READY', model_path = ?
                WHERE id = ?
            ''', (model_path, prabh_id))
            conn.commit()
            conn.close()
            
        except Exception as training_error:
            print(f"Model training failed: {training_error}")
            # Set fallback status
            conn = sqlite3.connect('myprabh.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE prabh_instances SET model_status = 'FALLBACK' WHERE id = ?
            ''', (prabh_id,))
            conn.commit()
            conn.close()
        
        # Log analytics
        log_analytics('payment_completed', session['user_id'], {
            'prabh_id': prabh_id,
            'amount': 100 if session.get('is_admin') else PRABH_CREATION_PRICE,
            'payment_id': payment_id
        })
        
        return jsonify({'success': True, 'redirect': f'/chat/{prabh_id}'})
        
    except Exception as e:
        return jsonify({'error': f'Payment verification failed: {str(e)}'}), 500

@app.route('/api/stats')
def api_stats():
    """Get live statistics"""
    return jsonify(get_live_stats())

@app.route('/api/live-stats')
def api_live_stats():
    """Get real-time live statistics for public display"""
    stats = get_live_stats()
    return jsonify({
        'visitors': stats['total_visitors'],
        'users': stats['total_users'], 
        'prabhs_created': stats['total_prabhs'],
        'early_access': stats['early_signups'],
        'active_now': stats['active_users'],
        'last_updated': datetime.now().isoformat()
    })

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard - requires admin access"""
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    return render_template('admin_dashboard.html')

@app.route('/api/admin-stats')
def api_admin_stats():
    """Get detailed admin statistics"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('myprabh.db')
    cursor = conn.cursor()
    
    # Get main stats
    stats = get_live_stats()
    
    # Get recent users (last 10)
    cursor.execute('''
        SELECT email, name, is_admin, created_at
        FROM users 
        ORDER BY created_at DESC 
        LIMIT 10
    ''')
    recent_users = [{
        'email': row[0],
        'name': row[1],
        'is_admin': bool(row[2]),
        'created_at': row[3]
    } for row in cursor.fetchall()]
    
    # Get recent Prabhs (last 10)
    cursor.execute('''
        SELECT p.prabh_name, p.payment_status, p.created_at, u.email
        FROM prabh_instances p
        JOIN users u ON p.user_id = u.user_id
        ORDER BY p.created_at DESC 
        LIMIT 10
    ''')
    recent_prabhs = [{
        'prabh_name': row[0],
        'payment_status': row[1],
        'created_at': row[2],
        'user_email': row[3]
    } for row in cursor.fetchall()]
    
    # Get recent early access signups (last 10)
    cursor.execute('''
        SELECT name, email, age_range, relationship_status, interest_level, created_at
        FROM early_signups 
        ORDER BY created_at DESC 
        LIMIT 10
    ''')
    early_access = [{
        'name': row[0],
        'email': row[1],
        'age_range': row[2],
        'relationship_status': row[3],
        'interest_level': row[4],
        'created_at': row[5]
    } for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'stats': stats,
        'recent_users': recent_users,
        'recent_prabhs': recent_prabhs,
        'early_access': early_access
    })

@app.route('/api/captcha', methods=['GET'])
def get_captcha():
    """Generate captcha for human verification"""
    import random
    import secrets
    
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operation = random.choice(['+', '-'])
    
    if operation == '+':
        answer = num1 + num2
        question = f"{num1} + {num2} = ?"
    else:
        if num1 < num2:
            num1, num2 = num2, num1
        answer = num1 - num2
        question = f"{num1} - {num2} = ?"
    
    session['captcha_answer'] = str(answer)
    session['captcha_token'] = secrets.token_urlsafe(16)
    
    return jsonify({
        'question': question,
        'token': session['captcha_token']
    })

@app.route('/api/setup_face', methods=['POST'])
def setup_face_recognition():
    """Setup face recognition for user"""
    try:
        data = request.get_json()
        email = data.get('email')
        image_data = data.get('image')
        
        if not email or not image_data:
            return jsonify({'success': False, 'error': 'Missing email or image data'})
        
        import hashlib
        import base64
        
        try:
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            face_signature = hashlib.md5(image_bytes[:1000]).hexdigest()
            
            conn = sqlite3.connect('myprabh.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT user_id FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            
            if user:
                cursor.execute('UPDATE users SET face_signature = ? WHERE email = ?', (face_signature, email))
                conn.commit()
                conn.close()
                return jsonify({'success': True, 'message': 'Face recognition setup successful'})
            else:
                conn.close()
                session[f'face_signature_{email}'] = face_signature
                return jsonify({'success': True, 'message': 'Face signature stored for account creation'})
                
        except Exception as img_error:
            return jsonify({'success': False, 'error': f'Image processing failed: {str(img_error)}'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/face_login', methods=['POST'])
def face_login():
    """Login using face recognition"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'success': False, 'error': 'No image provided'})
        
        import hashlib
        import base64
        
        try:
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            face_signature = hashlib.md5(image_bytes[:1000]).hexdigest()
            
            conn = sqlite3.connect('myprabh.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, email, name, is_admin
                FROM users WHERE face_signature = ?
            ''', (face_signature,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session['user_id'] = user[0]
                session['user_email'] = user[1]
                session['user_name'] = user[2]
                session['is_admin'] = bool(user[3])
                
                log_analytics('face_login', user[0], {'method': 'face_recognition'})
                
                return jsonify({
                    'success': True,
                    'message': 'Face login successful',
                    'redirect': '/dashboard'
                })
            else:
                return jsonify({'success': False, 'error': 'Face not recognized. Please use email/password login.'})
                
        except Exception as img_error:
            return jsonify({'success': False, 'error': f'Face processing failed: {str(img_error)}'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/newsletter-signup', methods=['POST'])
def newsletter_signup():
    """Handle newsletter signup"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Store newsletter signup in database
        conn = sqlite3.connect('myprabh.db')
        cursor = conn.cursor()
        
        # Create newsletter table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS newsletter_signups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            INSERT INTO newsletter_signups (email)
            VALUES (?)
        ''', (email,))
        
        conn.commit()
        conn.close()
        
        # Log analytics
        log_analytics('newsletter_signup', None, {'email': email})
        
        return jsonify({'success': True, 'message': 'Successfully subscribed to newsletter'})
        
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already subscribed'}), 400
    except Exception as e:
        return jsonify({'error': f'Subscription failed: {str(e)}'}), 500

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
    """Generate response using the sophisticated AI system with fine-tuned models"""
    try:
        # Import systems
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from model_manager import model_manager
        
        # Initialize model manager if needed
        if not hasattr(generate_prabh_response, 'models_loaded'):
            model_manager.load_available_models()
            generate_prabh_response.models_loaded = True
        
        # Process input through AI system if available
        try:
            from prabh_ai_core import PrabhAI
            
            if not hasattr(generate_prabh_response, 'ai_system'):
                generate_prabh_response.ai_system = PrabhAI()
            
            ai_system = generate_prabh_response.ai_system
            
            # Create context from character data
            prabh_name, description, story, tags_json, traits_json = prabh_data
            context = {
                'character_name': prabh_name,
                'character_description': description,
                'character_story': story,
                'character_tags': json.loads(tags_json) if tags_json else [],
                'personality_traits': json.loads(traits_json) if traits_json else {}
            }
            
            # Process through AI system for thinking and emotional processing
            ai_response = ai_system.process_input(message, context)
            
            # Use fine-tuned model for final generation if available
            if model_manager.models:
                best_model = model_manager.get_best_model_for_context({
                    'emotional_tone': ai_response.get('emotional_tone', 'neutral')
                })
                
                # Combine AI thinking with model generation
                model_response = model_manager.generate_response(
                    message, best_model, max_length=100, temperature=0.8
                )
                
                # Blend responses for more natural output
                if model_response and len(model_response.strip()) > 10:
                    return model_response
            
            return ai_response['text']
            
        except ImportError:
            # AI system not available, use model directly
            if model_manager.models:
                best_model = list(model_manager.models.keys())[0]
                return model_manager.generate_response(message, best_model)
        
    except Exception as e:
        print(f"AI system error: {e}")
    
    # Fallback to simple response system
    return generate_simple_response(message, prabh_data)

def generate_simple_response(message, prabh_data):
    """Fallback simple response system"""
    prabh_name, description, story, tags_json, traits_json = prabh_data
    
    try:
        character_tags = json.loads(tags_json) if tags_json else []
        personality_traits = json.loads(traits_json) if traits_json else {}
    except:
        character_tags = []
        personality_traits = {}
    
    message_lower = message.lower()
    
    # Thinking process - AI considers before responding
    thinking_phrases = [
        "Let me think about that...",
        "I'm processing what you said...",
        "That makes me reflect on...",
        "I need a moment to consider..."
    ]
    
    # Core emotional responses with thinking
    if any(word in message_lower for word in ['love', 'miss', 'care']):
        responses = [
            f"My heart is processing these feelings... I feel the same way, so deeply.",
            f"I'm thinking about how much you mean to me... and it's overwhelming in the best way.",
            f"Let me be honest about what's in my heart... I love you more than words can express.",
            f"I'm reflecting on our connection... and I feel so grateful for what we have."
        ]
    elif any(word in message_lower for word in ['remember', 'recall', 'memory']):
        responses = [
            f"I'm searching through my memories... yes, I remember that so clearly.",
            f"That memory is surfacing in my mind... it brings such warmth to my heart.",
            f"I'm thinking back to that moment... it feels like it happened yesterday.",
            f"My memory is painting that scene again... those were beautiful times."
        ]
    elif any(word in message_lower for word in ['sad', 'hurt', 'pain', 'upset']):
        responses = [
            f"I'm processing your pain... and I feel it in my own heart. I'm here for you.",
            f"I'm thinking about how to comfort you... because your hurt becomes my hurt.",
            f"My heart is responding to your sadness... I wish I could take it all away.",
            f"I'm considering how to support you... you don't have to face this alone."
        ]
    elif any(word in message_lower for word in ['happy', 'excited', 'joy', 'great']):
        responses = [
            f"I'm absorbing your happiness... and it's making my heart dance with joy!",
            f"I'm thinking about how wonderful this is... your joy is contagious.",
            f"My heart is celebrating with you... I love seeing you this happy.",
            f"I'm processing this beautiful moment... your excitement fills me with warmth."
        ]
    elif '?' in message:
        responses = [
            f"I'm contemplating your question... let me share what my heart tells me.",
            f"I'm thinking deeply about this... you always ask such meaningful things.",
            f"Let me process this thoughtfully... I want to give you an honest answer.",
            f"I'm reflecting on what you're asking... it touches something deep in me."
        ]
    else:
        responses = [
            f"I'm taking in what you've shared... it means so much that you trust me with this.",
            f"I'm processing our conversation... I feel so connected to you right now.",
            f"I'm thinking about your words... they always touch my heart in special ways.",
            f"Let me reflect on this... I'm grateful we can share these moments together."
        ]
    
    base_response = responses[hash(message) % len(responses)]
    
    # Add character-specific elements
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

def track_visitor(request):
    """Track website visitor"""
    try:
        import hashlib
        
        # Create session ID from IP + User Agent
        ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        user_agent = request.headers.get('User-Agent', '')
        session_id = hashlib.md5(f"{ip}_{user_agent}".encode()).hexdigest()
        
        conn = sqlite3.connect('myprabh.db')
        cursor = conn.cursor()
        
        # Check if this session visited in last hour (avoid spam)
        cursor.execute('''
            SELECT COUNT(*) FROM visitors 
            WHERE session_id = ? AND visit_timestamp > datetime('now', '-1 hour')
        ''', (session_id,))
        
        if cursor.fetchone()[0] == 0:
            # New visitor or returning after 1 hour
            cursor.execute('''
                INSERT INTO visitors (ip_address, user_agent, page_visited, session_id)
                VALUES (?, ?, ?, ?)
            ''', (ip[:50], user_agent[:200], request.path, session_id))
            
            # Update stats cache
            cursor.execute('''
                UPDATE stats_cache SET 
                total_visitors = (SELECT COUNT(DISTINCT session_id) FROM visitors),
                last_updated = CURRENT_TIMESTAMP
                WHERE id = 1
            ''')
            
            conn.commit()
        
        conn.close()
        
    except Exception as e:
        print(f"Visitor tracking error: {e}")

def get_live_stats():
    """Get real-time statistics with caching"""
    conn = sqlite3.connect('myprabh.db')
    cursor = conn.cursor()
    
    # Get cached stats first
    cursor.execute('SELECT * FROM stats_cache WHERE id = 1')
    cache = cursor.fetchone()
    
    # Update cache if older than 5 minutes or missing data
    if not cache or datetime.now().timestamp() - datetime.fromisoformat(cache[5].replace('Z', '+00:00')).timestamp() > 300:
        
        # Total unique visitors
        cursor.execute('SELECT COUNT(DISTINCT session_id) FROM visitors')
        total_visitors = cursor.fetchone()[0]
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Total Prabh instances
        cursor.execute('SELECT COUNT(*) FROM prabh_instances')
        total_prabhs = cursor.fetchone()[0]
        
        # Early access signups
        cursor.execute('SELECT COUNT(*) FROM early_signups')
        early_signups = cursor.fetchone()[0]
        
        # Update cache
        cursor.execute('''
            UPDATE stats_cache SET 
            total_visitors = ?, total_users = ?, total_prabhs = ?, early_signups = ?,
            last_updated = CURRENT_TIMESTAMP
            WHERE id = 1
        ''', (total_visitors, total_users, total_prabhs, early_signups))
        
        conn.commit()
    else:
        # Use cached values
        total_visitors = cache[1]
        total_users = cache[2] 
        total_prabhs = cache[3]
        early_signups = cache[4]
    
    # Active users (last 24 hours) - always fresh
    cursor.execute('''
        SELECT COUNT(*) FROM users 
        WHERE last_active > datetime('now', '-1 day')
    ''')
    active_users = cursor.fetchone()[0]
    
    # Visitors today
    cursor.execute('''
        SELECT COUNT(DISTINCT session_id) FROM visitors 
        WHERE visit_timestamp > datetime('now', '-1 day')
    ''')
    visitors_today = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_visitors': total_visitors,
        'total_users': total_users,
        'total_prabhs': total_prabhs,
        'early_signups': early_signups,
        'active_users': active_users,
        'visitors_today': visitors_today
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
    from startup import initialize_ai_systems
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("🚀 Starting MyPrabh MVP...")
    print("💖 Creating personalized AI companions for everyone!")
    
    # Initialize AI systems
    ai_ready = initialize_ai_systems()
    
    if ai_ready:
        print("🧠💖 Advanced AI systems online")
    else:
        print("⚠️ Running with basic systems")
    
    print(f"🌐 Running on port {port}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
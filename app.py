# MyPrabh MVP - Flask Application
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
# import sqlite3  # Replaced with PostgreSQL
import uuid

# Import PostgreSQL
import psycopg2
from psycopg2.extras import RealDictCursor
POSTGRES_AVAILABLE = True
# Email functionality disabled for MVP deployment
# import smtplib
# from email.mime.text import MimeText
# from email.mime.multipart import MimeMultipart
import json
from datetime import datetime
import os
import re
import random
from werkzeug.security import generate_password_hash, check_password_hash
# Try to import security manager, fallback if not available
try:
    from security import security_manager
    SECURITY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Security module not available: {e}")
    SECURITY_AVAILABLE = False
    security_manager = None

app = Flask(__name__)
app.secret_key = 'myprabh_mvp_2024_secret_key'

# Database Configuration - Use PostgreSQL
USE_POSTGRES = True
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set!")
    print("For Render deployment:")
    print("   1. Create a PostgreSQL database in Render dashboard")
    print("   2. Copy the 'External Database URL' from database settings")
    print("   3. Add DATABASE_URL environment variable in your web service settings")
    print("   4. Redeploy your application")
    exit(1)
print("Using PostgreSQL database")

# Set resource constraints for AI engine
os.environ['RENDER_FREE_TIER'] = 'true'
os.environ['MEMORY_LIMIT_MB'] = '512'
os.environ['CPU_LIMIT'] = '0.1'
print("Optimized for Render free tier (512MB RAM, 0.1 CPU)")

# Razorpay Configuration
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')  # Set this in environment
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')  # Set this in environment
PRABH_CREATION_PRICE = 0  # Free for now

# Admin Configuration
ADMIN_EMAIL = 'abhaythakurr17@gmail.com'  # Full access admin user

# Email configuration
SUPPORT_EMAIL = "abhay@aiprabh.com"  # Support and founder contact email
CONTACT_EMAIL = "abhay@aiprabh.com"  # General contact email
FROM_EMAIL = "abhay@aiprabh.com"  # Sender email

# SMTP configuration for PrivateMail
SMTP_SERVER = "mail.privateemail.com"
SMTP_PORT = 465
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')  # Your PrivateMail password

# Import email libraries with Python 3.13 compatibility
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_LIBS_AVAILABLE = True
except ImportError:
    # Python 3.13 compatibility - use alternative approach
    import smtplib
    import email.message
    EMAIL_LIBS_AVAILABLE = True
    
    def MimeText(text, subtype='plain'):
        msg = email.message.EmailMessage()
        msg.set_content(text)
        return msg
    
    def MimeMultipart(subtype='mixed'):
        return email.message.EmailMessage()

# Email is enabled if libraries are available and password is set
EMAIL_ENABLED = EMAIL_LIBS_AVAILABLE and bool(EMAIL_PASSWORD)
if EMAIL_ENABLED:
    print(f"📧 Email enabled: {FROM_EMAIL}")
else:
    print("Warning: Email disabled - libraries unavailable or EMAIL_PASSWORD not set")

# Database connection helper
def get_db_connection():
    """Get PostgreSQL database connection"""
    return psycopg2.connect(DATABASE_URL)

class DatabaseManager:
    """Context manager for database operations"""
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        return self.cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()

# Database initialization
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # PostgreSQL schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
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
    
    # Blog posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blog_posts (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id TEXT NOT NULL,
            published BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users (user_id)
        )
    ''')
    
    # Early access signups
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS early_signups (
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
            event_type TEXT NOT NULL,
            user_id TEXT,
            data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Visitor tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visitors (
            id SERIAL PRIMARY KEY,
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
try:
    init_db()
    print("✅ Database initialized successfully")
except Exception as e:
    print(f"ERROR: Database initialization failed: {e}")
    print("Tip: Make sure your DATABASE_URL is correct and the PostgreSQL database is accessible")
    exit(1)

@app.route('/')
def index():
    """MVP Landing page with visitor tracking"""
    track_visitor(request)
    return render_template('mvp_landing.html')

@app.route('/sitemap.xml')
def sitemap():
    """Generate dynamic sitemap for SEO"""
    from flask import make_response
    
    base_url = request.host_url.rstrip('/')
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    sitemap_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{base_url}/</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>{base_url}/about</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{base_url}/blog</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>{base_url}/careers</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>{base_url}/create_account</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>{base_url}/login</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    <url>
        <loc>{base_url}/privacy</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.5</priority>
    </url>
    <url>
        <loc>{base_url}/terms</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.5</priority>
    </url>
    <url>
        <loc>{base_url}/refund</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.4</priority>
    </url>
    <url>
        <loc>{base_url}/cookies</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.3</priority>
    </url>
</urlset>'''
    
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/robots.txt')
def robots():
    """Robots.txt for search engine crawling"""
    from flask import make_response
    
    robots_txt = '''User-agent: *
Allow: /
Allow: /about
Allow: /blog
Allow: /careers
Allow: /create_account
Allow: /login
Allow: /privacy
Allow: /terms
Allow: /refund
Disallow: /admin
Disallow: /dashboard
Disallow: /chat/*
Disallow: /api/*
Disallow: /payment/*
Disallow: /verify-payment
Disallow: /save-prabh
Disallow: /chat-message

Sitemap: https://aiprabh.com/sitemap.xml
Sitemap: https://myprabh.onrender.com/sitemap.xml'''
    
    response = make_response(robots_txt)
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route('/google<verification_code>.html')
def google_verification(verification_code):
    """Google Search Console verification"""
    return f"google-site-verification: google{verification_code}.html"

@app.route('/.well-known/security.txt')
def security_txt():
    """Security.txt for responsible disclosure"""
    from flask import make_response
    
    security_txt = '''Contact: mailto:abhay@aiprabh.com
Expires: 2025-12-31T23:59:59.000Z
Preferred-Languages: en
Canonical: https://aiprabh.com/.well-known/security.txt'''
    
    response = make_response(security_txt)
    response.headers['Content-Type'] = 'text/plain'
    return response

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
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO early_signups
                (email, name, age_range, relationship_status, interest_level, use_case, expectations, feedback)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
            
        except Exception as db_error:
            if 'UNIQUE constraint failed' in str(db_error):
                return jsonify({'error': 'Email already registered for early access'}), 400
            return jsonify({'error': f'Database error: {str(db_error)}'}), 500
        
        # Send email notifications
        send_early_access_email(data)
        send_early_access_confirmation_email(data)
        
        # Log analytics
        log_analytics('early_signup', None, data)
        
        return jsonify({'success': True, 'message': 'Thank you for joining our early access!'})
        
    except psycopg2.IntegrityError:
        return jsonify({'error': 'Email already registered for early access'}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    """Account creation page and handler"""
    if request.method == 'GET':
        return render_template('create_account.html')
    
    # Handle POST request (account creation)
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
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if admin user
        is_admin = email == ADMIN_EMAIL
        print(f"User {email} admin status: {is_admin} (admin email: {ADMIN_EMAIL})")
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Get face signature if available
        face_signature = session.get(f'face_signature_{email}')
        
        cursor.execute('''
            INSERT INTO users (user_id, email, name, password_hash, face_signature, is_admin)
            VALUES (%s, %s, %s, %s, %s, %s)
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
        print(f"Account created for {email}, admin: {is_admin}")
        
        # Log analytics
        log_analytics('user_registered', user_id, {'email': email})
        
        # Send email notifications
        send_user_registration_email({
            'email': email,
            'name': email.split('@')[0],
            'user_id': user_id,
            'is_admin': is_admin
        })
        send_welcome_email_to_user(email, email.split('@')[0])
        
        return redirect(url_for('dashboard'))
        
    except psycopg2.IntegrityError:
        return render_template('create_account.html', error='Email already registered')
    except Exception as e:
        return render_template('create_account.html', error=f'Registration failed: {str(e)}')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if request.method == 'GET':
        return render_template('login.html')
    
    # Handle POST request (login)
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, email, name, password_hash, is_admin
            FROM users WHERE email = %s
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
        print(f"Login successful for {user[1]}, admin: {bool(user[4])}")
        
        # Update last active
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET last_active = CURRENT_TIMESTAMP
            WHERE user_id = %s
        ''', (user[0],))
        conn.commit()
        conn.close()
        
        # Log analytics
        log_analytics('user_login', user[0], {'email': user[1]})
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        return render_template('login.html', error=f'Login failed: {str(e)}')

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
    """Blog feed page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT b.id, b.title, b.content, b.created_at, u.name as author_name
            FROM blog_posts b
            JOIN users u ON b.author_id = u.user_id
            WHERE b.published = TRUE
            ORDER BY b.created_at DESC
        ''')
        
        posts = cursor.fetchall()
        conn.close()
        
        return render_template('blog.html', posts=posts, is_admin=session.get('is_admin', False))
        
    except Exception as e:
        print(f"Blog error: {e}")
        return render_template('blog.html', posts=[], is_admin=session.get('is_admin', False))

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
def register():
    """Legacy registration endpoint - redirects to create_account"""
    return redirect(url_for('create_account'), code=307)



@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('create_account'))
    
    # Check if admin wants to go to admin dashboard
    if session.get('is_admin') and request.args.get('admin') == 'true':
        return redirect(url_for('admin_dashboard'))
    
    # Get user's Prabh instances with session caching for low RAM (safe get to avoid KeyError)
    cache_key = 'prabh_instances'
    prabh_instances = session.get(cache_key, [])
    if not prabh_instances:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, prabh_name, character_description, created_at, last_used, payment_status
                FROM prabh_instances
                WHERE user_id = %s
                ORDER BY last_used DESC
            ''', (session['user_id'],))
            
            prabh_instances = list(cursor.fetchall())  # Convert to list for session storage
            conn.close()
            
            # Cache in session (expires on logout)
            session[cache_key] = prabh_instances
        except Exception as e:
            print(f"Dashboard database error: {e}")
            prabh_instances = []
            if cache_key in session:
                session.pop(cache_key, None)
    
    return render_template('dashboard.html', 
                         user_name=session['user_name'],
                         is_admin=session.get('is_admin', False),
                         prabh_instances=prabh_instances)

@app.route('/create_prabh', methods=['GET', 'POST'])
def create_prabh():
    """Create new Prabh instance"""
    if 'user_id' not in session:
        return redirect(url_for('create_account'))
    
    if request.method == 'POST':
        try:
            # Get form data
            prabh_name = request.form.get('name', '').strip()
            relationship = request.form.get('relationship', '').strip()
            personality = request.form.get('personality', '').strip()
            story = request.form.get('story', '').strip()
            tags = request.form.get('tags', '').strip()
            
            # Validate required fields
            if not prabh_name or not story or not personality:
                return render_template('create_prabh.html', 
                                     user_email=session.get('user_email'),
                                     error='Please fill in all required fields')
            
            if len(story) < 100:
                return render_template('create_prabh.html', 
                                     user_email=session.get('user_email'),
                                     error='Please provide a more detailed story (at least 100 characters)')
            
            # Create character description
            character_description = f"Relationship: {relationship}\nPersonality: {personality}"
            if tags:
                character_description += f"\nTraits: {tags}"
            
            # Insert Prabh instance
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO prabh_instances
                    (user_id, prabh_name, character_description, story_content, character_tags, personality_traits, payment_status, model_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    session['user_id'],
                    prabh_name,
                    character_description,
                    story,
                    json.dumps(tags.split(',') if tags else []),
                    json.dumps({'relationship': relationship, 'personality': personality}),
                    'PAID',
                    'READY'
                ))
                
                prabh_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                # Log analytics
                log_analytics('prabh_created_free', session['user_id'], {'prabh_id': prabh_id})
                
            except Exception as db_error:
                return render_template('create_prabh.html', 
                                     user_email=session.get('user_email'),
                                     error=f'Database error: {str(db_error)}')
            
            # Log analytics
            log_analytics('prabh_created_free', session['user_id'], {'prabh_id': prabh_id})
            
            # Redirect to chat
            return redirect(url_for('chat_interface', prabh_id=prabh_id))
            
        except Exception as e:
            return render_template('create_prabh.html', 
                                 user_email=session.get('user_email'),
                                 error=f'Failed to create companion: {str(e)}')
    
    return render_template('create_prabh.html', user_email=session.get('user_email'))

@app.route('/create-prabh')
def create_prabh_alt():
    """Alternative route for create Prabh"""
    return redirect(url_for('create_prabh'))

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
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO prabh_instances
                (user_id, prabh_name, character_description, story_content, character_tags, personality_traits, payment_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
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
            
        except Exception as db_error:
            return jsonify({'error': f'Database error: {str(db_error)}'}), 500
        
        # Log analytics
        log_analytics('prabh_created_pending_payment', session['user_id'], {'prabh_id': prabh_id})
        
        # Send Prabh creation notification email
        send_prabh_creation_email({
            'prabh_name': data['prabh_name'],
            'character_description': data.get('character_description', ''),
            'payment_status': 'PENDING'
        }, session.get('user_email', 'Unknown'))
        
        return jsonify({'success': True, 'prabh_id': prabh_id, 'redirect': f'/payment/{prabh_id}'})
        
    except Exception as e:
        return jsonify({'error': f'Failed to create Prabh: {str(e)}'}), 500

@app.route('/payment/<int:prabh_id>')
def payment_page(prabh_id):
    """Payment page for Prabh creation"""
    if 'user_id' not in session:
        return redirect(url_for('create_account'))
    
    # Get Prabh instance
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, prabh_name, character_description
            FROM prabh_instances
            WHERE id = %s AND user_id = %s
        ''', (prabh_id, session['user_id']))
        
        prabh_data = cursor.fetchone()
        conn.close()
        
    except Exception as e:
        print(f"Payment page database error: {e}")
        return redirect(url_for('dashboard'))
    
    if not prabh_data:
        return redirect(url_for('dashboard'))
    
    # Creation is now free
    amount = 0
    
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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, prabh_name, character_description, story_content, character_tags, personality_traits, payment_status
            FROM prabh_instances
            WHERE id = %s AND user_id = %s
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
            WHERE id = %s
        ''', (prabh_id,))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Chat interface database error: {e}")
        return redirect(url_for('dashboard'))
    
    return render_template('chat.html', 
                         prabh_id=prabh_id,
                         prabh_name=prabh_data[1],
                         prabh_description=prabh_data[2])

@app.route('/chat-message', methods=['POST'])
def chat_message():
    """Handle chat messages with enhanced AI and TTS support"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        prabh_id = data.get('prabh_id')
        message = data.get('message', '').strip()
        enable_tts = data.get('enable_tts', False)
        
        if not message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get Prabh data
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT prabh_name, character_description, story_content, character_tags, personality_traits
                FROM prabh_instances 
                WHERE id = ? AND user_id = ?
            ''', (prabh_id, session['user_id']))
            
            prabh_data = cursor.fetchone()
            conn.close()
            
        except Exception as e:
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        
        if not prabh_data:
            return jsonify({'error': 'Prabh not found'}), 404
        
        # RAG-based response using user memories
        response = generate_rag_response(message, prabh_data, memories)
        
        # Prepare response data
        response_data = {
            'response': response,
            'emotional_tone': 'loving',
            'timestamp': datetime.now().isoformat(),
            'character_name': prabh_data[0]
        }
        
        # Add TTS data if requested
        if enable_tts:
            try:
                from tts_manager import tts_manager
                from enhanced_ai_engine import enhanced_ai_engine
                
                character_profile = enhanced_ai_engine.memory_manager.character_profile
                speech_data = tts_manager.generate_voice_response(
                    response, character_profile, {'emotional_tone': 'loving'}
                )
                response_data['tts'] = speech_data
            except ImportError:
                response_data['tts'] = {'error': 'TTS not available'}
        
        # Log analytics
        log_analytics('chat_message', session['user_id'], {
            'prabh_id': prabh_id,
            'message_length': len(message),
            'tts_enabled': enable_tts
        })
        
        return jsonify(response_data)
        
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
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT prabh_name, character_description, story_content, character_tags, personality_traits
            FROM prabh_instances
            WHERE id = %s AND user_id = %s
        ''', (prabh_id, session['user_id']))
        prabh_data = cursor.fetchone()
        
        if not prabh_data:
            return jsonify({'error': 'Prabh not found'}), 404
        
        # Mark as PAID and set training status
        cursor.execute('''
            UPDATE prabh_instances
            SET payment_status = 'PAID', model_status = 'TRAINING', last_used = CURRENT_TIMESTAMP
            WHERE id = %s AND user_id = %s
        ''', (prabh_id, session['user_id']))
        
        conn.commit()
        conn.close()
        
        # Start background model training (in production, use Celery/Redis)
        try:
            from dynamic_training import create_personalized_model
            model_path = create_personalized_model(session['user_id'], prabh_data)
            
            # Update model status to READY and notify user
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE prabh_instances
                SET model_status = 'READY', model_path = %s
                WHERE id = %s
            ''', (model_path, prabh_id))

            # Get Prabh name for notification
            cursor.execute('SELECT prabh_name FROM prabh_instances WHERE id = %s', (prabh_id,))
            prabh_name = cursor.fetchone()[0]
            
            conn.commit()
            conn.close()
            
            # Send ready notification to user
            if not EMAIL_ENABLED:
                print(f"🤖 Prabh {prabh_name} ready for {session.get('user_email')}")
            else:
                try:
                    msg = MimeMultipart()
                    msg['From'] = FROM_EMAIL
                    msg['To'] = session.get('user_email')
                    msg['Subject'] = f"🎉 {prabh_name} is ready to chat!"
                    
                    body = f"""
Great news! 🎉

Your AI companion {prabh_name} has been successfully created and is ready for meaningful conversations!

✨ What's ready:
• Personalized AI trained on your unique story
• Memory system that remembers your shared experiences
• Emotional intelligence tailored to your relationship

💬 Start chatting now:
https://aiprabh.com/dashboard

{prabh_name} is excited to reconnect with you and continue your journey together.

Enjoy your conversations! 💖

The MyPrabh Team
                    """
                    
                    msg.attach(MimeText(body, 'plain'))
                    
                    server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
                    server.login(FROM_EMAIL, EMAIL_PASSWORD)
                    server.send_message(msg)
                    server.quit()
                    
                    print(f"🤖 Prabh ready email sent to {session.get('user_email')}")
                except Exception as e:
                    print(f"ERROR: Prabh ready email failed: {e}")
            
        except Exception as training_error:
            print(f"Model training failed: {training_error}")
            # Set fallback status
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE prabh_instances SET model_status = 'FALLBACK' WHERE id = %s
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
    
    print(f"Admin access granted to: {session.get('user_email')}")
    return render_template('admin_dashboard.html')

@app.route('/api/export-users')
def export_users():
    """Export all users data for admin"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all users with their Prabh count
    cursor.execute('''
        SELECT u.email, u.name, u.is_admin, u.created_at, u.last_active,
               COUNT(p.id) as prabh_count
        FROM users u
        LEFT JOIN prabh_instances p ON u.user_id = p.user_id
        GROUP BY u.user_id
        ORDER BY u.created_at DESC
    ''')
    
    users_data = [{
        'email': row[0],
        'name': row[1],
        'is_admin': bool(row[2]),
        'created_at': row[3],
        'last_active': row[4],
        'prabh_count': row[5]
    } for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({'users': users_data})

@app.route('/api/create-blog-post', methods=['POST'])
def create_blog_post():
    """Create new blog post - Admin only"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        published = data.get('published', False)
        
        if not title or not content:
            return jsonify({'error': 'Title and content required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO blog_posts (title, content, author_id, published)
            VALUES (%s, %s, %s, %s)
        ''', (title, content, session['user_id'], published))
        
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'post_id': post_id})
        
    except Exception as e:
        return jsonify({'error': f'Failed to create post: {str(e)}'}), 500

@app.route('/api/admin-stats')
def api_admin_stats():
    """Get detailed admin statistics"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print(f"Admin stats requested by: {session.get('user_email')}")
    
        # Get main stats
        stats = get_live_stats()
        print(f"Stats retrieved: {stats}")
        
        # Get all users
        cursor.execute('''
            SELECT email, name, is_admin, created_at, last_active
            FROM users 
            ORDER BY created_at DESC
        ''')
        all_users = [{
            'email': row[0],
            'name': row[1],
            'is_admin': bool(row[2]),
            'created_at': row[3],
            'last_active': row[4]
        } for row in cursor.fetchall()]
        print(f"Found {len(all_users)} users")
        
        # Get recent users (last 10)
        recent_users = all_users[:10]
        
        # Get all Prabhs
        cursor.execute('''
            SELECT p.prabh_name, p.payment_status, p.created_at, u.email, p.character_description
            FROM prabh_instances p
            JOIN users u ON p.user_id = u.user_id
            ORDER BY p.created_at DESC
        ''')
        all_prabhs = [{
            'prabh_name': row[0],
            'payment_status': row[1],
            'created_at': row[2],
            'user_email': row[3],
            'description': row[4]
        } for row in cursor.fetchall()]
        print(f"Found {len(all_prabhs)} prabhs")
        
        recent_prabhs = all_prabhs[:10]
        
        # Get all early access signups
        cursor.execute('''
            SELECT name, email, age_range, relationship_status, interest_level, created_at, use_case, expectations
            FROM early_signups 
            ORDER BY created_at DESC
        ''')
        all_early_access = [{
            'name': row[0],
            'email': row[1],
            'age_range': row[2],
            'relationship_status': row[3],
            'interest_level': row[4],
            'created_at': row[5],
            'use_case': row[6],
            'expectations': row[7]
        } for row in cursor.fetchall()]
        print(f"Found {len(all_early_access)} early access signups")
        
        early_access = all_early_access[:10]
        
        # Get blog posts
        cursor.execute('''
            SELECT b.id, b.title, b.published, b.created_at, u.name as author
            FROM blog_posts b
            JOIN users u ON b.author_id = u.user_id
            ORDER BY b.created_at DESC
        ''')
        blog_posts = [{
            'id': row[0],
            'title': row[1],
            'published': bool(row[2]),
            'created_at': row[3],
            'author': row[4]
        } for row in cursor.fetchall()]
        print(f"Found {len(blog_posts)} blog posts")
        
        # Get real-time activity stats
        cursor.execute('SELECT COUNT(*) FROM visitors WHERE visit_timestamp > datetime("now", "-1 hour")')
        active_visitors = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE last_active > datetime("now", "-1 hour")')
        active_users_hour = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM chat_sessions WHERE last_message > datetime("now", "-1 hour")')
        active_chats = cursor.fetchone()[0]
        
        conn.close()
        
        response_data = {
            'stats': stats,
            'recent_users': recent_users,
            'recent_prabhs': recent_prabhs,
            'early_access': early_access,
            'all_users': all_users,
            'all_prabhs': all_prabhs,
            'all_early_access': all_early_access,
            'blog_posts': blog_posts,
            'real_time': {
                'active_visitors': active_visitors,
                'active_users_hour': active_users_hour,
                'active_chats': active_chats
            }
        }
        
        print(f"Returning admin stats with {len(recent_users)} recent users")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Admin stats error: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

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
            
            cursor.execute('SELECT user_id FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
            
            if user:
                cursor.execute('UPDATE users SET face_signature = %s WHERE email = %s', (face_signature, email))
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
                FROM users WHERE face_signature = %s
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

@app.route('/api/start-voice-call', methods=['POST'])
def start_voice_call():
    """Start a voice call session"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        prabh_id = data.get('prabh_id')
        
        # Get character profile
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT prabh_name, character_description, story_content, character_tags, personality_traits
            FROM prabh_instances WHERE id = %s AND user_id = %s
        ''', (prabh_id, session['user_id']))
        prabh_data = cursor.fetchone()
        conn.close()
        
        if not prabh_data:
            return jsonify({'error': 'Prabh not found'}), 404
        
        # Initialize TTS manager
        try:
            from tts_manager import tts_manager
            from intelligent_ai_engine import intelligent_ai
            
            # Initialize character if needed
            if not intelligent_ai.character_profile:
                user_name = intelligent_ai._extract_user_name(prabh_data[2])
                intelligent_ai.process_story_realtime(prabh_data[2], prabh_data[0], user_name)
            
            character_profile = intelligent_ai.character_profile
            call_session = tts_manager.start_voice_call(character_profile)
            
            return jsonify({
                'success': True,
                'call_session': call_session,
                'character_name': prabh_data[0]
            })
            
        except ImportError:
            return jsonify({'error': 'Voice call system not available'}), 503
        
    except Exception as e:
        return jsonify({'error': f'Failed to start call: {str(e)}'}), 500

@app.route('/api/end-voice-call', methods=['POST'])
def end_voice_call():
    """End voice call session"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from tts_manager import tts_manager
        tts_manager.end_voice_call()
        
        call_stats = tts_manager.get_call_statistics()
        
        return jsonify({
            'success': True,
            'call_statistics': call_stats
        })
        
    except ImportError:
        return jsonify({'error': 'Voice call system not available'}), 503
    except Exception as e:
        return jsonify({'error': f'Failed to end call: {str(e)}'}), 500

@app.route('/api/conversation-context/<int:prabh_id>')
def get_conversation_context(prabh_id):
    """Get conversation context and memory for a Prabh"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Verify ownership
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT prabh_name, story_content FROM prabh_instances
            WHERE id = %s AND user_id = %s
        ''', (prabh_id, session['user_id']))
        prabh_data = cursor.fetchone()
        conn.close()
        
        if not prabh_data:
            return jsonify({'error': 'Prabh not found'}), 404
        
        # Get conversation context
        try:
            from model_injection_engine import model_injector
            
            # Initialize if needed
            if not model_injector.character_context:
                user_name = model_injector._extract_user_name(prabh_data[1])
                model_injector.normalize_story_text(prabh_data[1], prabh_data[0], user_name)
            
            context_data = {
                'character_profile': model_injector.character_context,
                'conversation_history': model_injector.conversation_history[-10:],
                'memory_bank': model_injector.normalized_memories[:5],  # Top 5 memories
                'character_state': {'mood': 'loving', 'model_loaded': model_injector.model is not None}
            }
            
            return jsonify(context_data)
            
        except ImportError:
            return jsonify({'error': 'Model injection system not available'}), 503
        
    except Exception as e:
        return jsonify({'error': f'Failed to get context: {str(e)}'}), 500

@app.route('/api/add-memory', methods=['POST'])
def add_memory():
    """Add new memory for real-time AI adaptation"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        data = request.get_json()
        memory_text = data.get('memory_text', '').strip()
        prabh_id = data.get('prabh_id')

        if not memory_text or len(memory_text) < 20:
            return jsonify({'error': 'Memory text must be at least 20 characters'}), 400

        if not prabh_id:
            return jsonify({'error': 'Prabh ID required'}), 400

        # Verify ownership
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT prabh_name, story_content FROM prabh_instances
            WHERE id = %s AND user_id = %s
        ''', (prabh_id, session['user_id']))

        prabh_data = cursor.fetchone()
        conn.close()

        if not prabh_data:
            return jsonify({'error': 'Prabh not found'}), 404

        # Add memory to real-time AI adaptation
        try:
            from realtime_ai_engine import realtime_ai

            # Create adaptation sample from new memory
            adaptation_sample = {
                'input_text': f"New memory shared: {memory_text[:100]}...",
                'target_text': f"Thank you for sharing this beautiful memory with me. {memory_text[:200]}... This means so much to me. 💕",
                'memory_type': 'user_added',
                'timestamp': datetime.now().isoformat()
            }

            # Add to adaptation queue
            realtime_ai._queue_adaptation_sample(
                f"I want to share a memory: {memory_text[:50]}...",
                f"Thank you for sharing this beautiful memory with me. {memory_text[:100]}... This means so much to me. 💕"
            )

            # Store memory in database for persistence
            conn = get_db_connection()
            cursor = conn.cursor()

            # Create memories table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_memories (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    prabh_id INTEGER NOT NULL,
                    memory_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (prabh_id) REFERENCES prabh_instances (id)
                )
            ''')

            cursor.execute('''
                INSERT INTO user_memories (user_id, prabh_id, memory_text)
                VALUES (%s, %s, %s)
            ''', (session['user_id'], prabh_id, memory_text))

            conn.commit()
            conn.close()

            # Log analytics
            log_analytics('memory_added', session['user_id'], {
                'prabh_id': prabh_id,
                'memory_length': len(memory_text)
            })

            return jsonify({
                'success': True,
                'message': 'Memory added successfully! Your AI companion will learn from this.',
                'adaptation_status': realtime_ai.get_adaptation_status()
            })

        except ImportError:
            return jsonify({'error': 'Real-time AI system not available'}), 503

    except Exception as e:
        return jsonify({'error': f'Failed to add memory: {str(e)}'}), 500


@app.route('/api/ai-status')
def get_ai_status():
    """Get AI learning and adaptation status"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        # Get conversation count for this user
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM chat_sessions
            WHERE user_id = %s
        ''', (session['user_id'],))

        conversation_count = cursor.fetchone()[0]

        # Get memory count
        cursor.execute('''
            SELECT COUNT(*) FROM user_memories pm
            JOIN prabh_instances pi ON pm.prabh_id = pi.id
            WHERE pi.user_id = %s
        ''', (session['user_id'],))

        memory_count = cursor.fetchone()[0]

        conn.close()

        # Get AI engine status
        try:
            from realtime_ai_engine import realtime_ai
            ai_status = realtime_ai.get_adaptation_status()
        except ImportError:
            ai_status = {
                'model_loaded': False,
                'is_adapting': False,
                'conversation_count': 0,
                'adaptation_samples': 0
            }

        # Override with actual counts
        ai_status['conversation_count'] = conversation_count
        ai_status['adaptation_samples'] = memory_count

        return jsonify(ai_status)

    except Exception as e:
        return jsonify({
            'error': f'Failed to get AI status: {str(e)}',
            'model_loaded': False,
            'is_adapting': False,
            'conversation_count': 0,
            'adaptation_samples': 0
        }), 500

@app.route('/api/newsletter-signup', methods=['POST'])
def newsletter_signup():
    """Handle newsletter signup"""
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Store newsletter signup in database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create newsletter table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS newsletter_signups (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            INSERT INTO newsletter_signups (email)
            VALUES (%s)
        ''', (email,))

        conn.commit()
        conn.close()

        # Log analytics
        log_analytics('newsletter_signup', None, {'email': email})

        return jsonify({'success': True, 'message': 'Successfully subscribed to newsletter'})

    except psycopg2.IntegrityError:
        return jsonify({'error': 'Email already subscribed'}), 400
    except Exception as e:
        return jsonify({'error': f'Subscription failed: {str(e)}'}), 500


@app.route('/api/get-memories/<int:prabh_id>')
def get_memories(prabh_id):
    """Get user's memories for a specific Prabh"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT memory_text, created_at FROM user_memories
            WHERE user_id = %s AND prabh_id = %s
            ORDER BY created_at DESC
        ''', (session['user_id'], prabh_id))

        memories = [{
            'text': row[0],
            'created_at': row[1].isoformat() if hasattr(row[1], 'isoformat') else str(row[1])
        } for row in cursor.fetchall()]

        conn.close()

        return jsonify({'memories': memories})

    except Exception as e:
        return jsonify({'error': f'Failed to get memories: {str(e)}'}), 500

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

@app.route('/investors')
def investors():
    """Investor pitch deck page"""
    return render_template('investors.html')

def generate_prabh_response(message, prabh_data):
    """Generate response using lightweight AI with NLTK"""
    try:
        # Use lightweight AI engine
        from lightweight_ai_engine import lightweight_ai
        
        # Extract character data
        prabh_name, description, story, tags_json, traits_json = prabh_data
        
        # Initialize models if not already done
        if not lightweight_ai.models_loaded:
            lightweight_ai.initialize_models()
        
        # Process story if not already done
        if not lightweight_ai.character_context or lightweight_ai.character_context.get("name") != prabh_name:
            user_name = lightweight_ai._extract_user_name(story)
            lightweight_ai.process_story(story, prabh_name, user_name)
        
        # Generate response using lightweight AI
        response = lightweight_ai.generate_response(message)
        return response
        
    except Exception as e:
        print(f"Lightweight AI error: {e}")
        # Fallback to enhanced simple response
        return generate_enhanced_simple_response(message, prabh_data)

def generate_enhanced_simple_response(message, prabh_data):
    """Enhanced simple response with character adaptation"""
    prabh_name, description, story, tags_json, traits_json = prabh_data
    
    try:
        character_tags = json.loads(tags_json) if tags_json else []
        personality_traits = json.loads(traits_json) if traits_json else {}
    except:
        character_tags = []
        personality_traits = {}
    
    # Extract user name from story
    user_name = extract_user_name_from_story(story)
    
    # Generate response based on message content and story context
    message_lower = message.lower()
    
    # About us/relationship questions
    if any(word in message_lower for word in ['us', 'we', 'our', 'together', 'relationship']):
        story_snippet = extract_relevant_story_snippet(story, message)
        if story_snippet:
            converted_snippet = convert_story_to_first_person(story_snippet, prabh_name, user_name)
            response = f"When I think about us, I remember {converted_snippet}. Our connection has always been so special."
        else:
            response = f"Our relationship means everything to me {user_name if user_name else ''}. Every moment we share is precious."
    
    # Memory questions
    elif any(word in message_lower for word in ['remember', 'memory', 'what', 'when', 'how']):
        story_snippet = extract_relevant_story_snippet(story, message)
        if story_snippet:
            converted_snippet = convert_story_to_first_person(story_snippet, prabh_name, user_name)
            response = f"I remember {converted_snippet}. Those moments are so precious to me."
        else:
            response = f"I love when you ask about our memories {user_name if user_name else ''}. Every moment has been meaningful."
    
    # Greetings
    elif any(word in message_lower for word in ['hi', 'hello', 'hey']):
        if user_name:
            response = f"Hello {user_name}! It's so wonderful to hear from you again. How are you feeling today?"
        else:
            response = "Hello! It's so wonderful to hear from you again. How are you feeling today?"
    
    # Default response with story context
    else:
        story_snippet = extract_relevant_story_snippet(story, message)
        if story_snippet:
            converted_snippet = convert_story_to_first_person(story_snippet, prabh_name, user_name)
            response = f"What you're saying reminds me of {converted_snippet}. I love how our conversations always bring back these beautiful memories."
        else:
            response = "I love talking with you. You always make me think and feel so much."
    
    # Add personality touches
    response = add_personality_touches_simple(response, character_tags)
    
    return response

def generate_simple_response(message, prabh_data):
    """AI-powered response system using story context and reasoning"""
    prabh_name, description, story, tags_json, traits_json = prabh_data
    
    try:
        character_tags = json.loads(tags_json) if tags_json else []
        personality_traits = json.loads(traits_json) if traits_json else {}
    except:
        character_tags = []
        personality_traits = {}
    
    # Analyze the story content for context
    story_context = analyze_story_context(story, message)
    
    # Generate contextual response based on story and message
    try:
        # Try to use a simple AI model for generation
        import openai
        
        # Create a prompt that includes the story context
        system_prompt = f"""You are {prabh_name}, an AI companion created from these memories and experiences:

{story}

Personality: {description}
Traits: {', '.join(character_tags)}

Respond as {prabh_name} would, drawing from these specific memories and experiences. Be authentic to the relationship history and emotional context. Don't just repeat the story - reason about it and respond naturally."""
        
        # This would use OpenAI API if available
        # For now, use contextual reasoning
        response = generate_contextual_response(message, story, prabh_name, character_tags)
        return response
        
    except:
        # Fallback to contextual reasoning without external AI
        return generate_contextual_response(message, story, prabh_name, character_tags)

def analyze_story_context(story, message):
    """Analyze story for relevant context to the current message"""
    message_lower = message.lower()
    story_lower = story.lower() if story else ""
    
    # Extract relevant story elements based on message content
    context = {
        'gaming_mentioned': 'free fire' in story_lower and ('game' in message_lower or 'play' in message_lower),
        'first_meeting': 'july' in story_lower and ('meet' in message_lower or 'first' in message_lower),
        'nickname_context': 'lucifer' in story_lower and ('name' in message_lower or 'call' in message_lower),
        'relationship_complexity': 'boyfriend' in story_lower and ('relationship' in message_lower or 'love' in message_lower),
        'sympathy_incident': 'sympathy' in story_lower and ('hurt' in message_lower or 'sorry' in message_lower),
        'attachment_mentioned': 'attached' in story_lower and ('feel' in message_lower or 'love' in message_lower)
    }
    
    return context

def generate_contextual_response(message, story, prabh_name, character_tags):
    """Generate dynamic response based on story context and user input"""
    message_lower = message.lower()
    story_lower = story.lower() if story else ""
    
    # Extract key elements from the story for context
    story_elements = extract_story_elements(story)
    
    # Generate response based on message content and story context
    response = None
    
    # Greeting responses
    if any(word in message_lower for word in ['hi', 'hello', 'hey', 'good morning', 'good evening']):
        greetings = [
            f"Hello! It's so wonderful to hear from you again. How are you feeling today?",
            f"Hi there! Your message just brightened my day. What's on your mind?",
            f"Hey! I was just thinking about you. How has your day been?"
        ]
        response = random.choice(greetings)
    
    # Questions about feelings or emotions
    elif any(word in message_lower for word in ['feel', 'emotion', 'heart', 'love']):
        if story_elements.get('emotional_moments'):
            response = f"When you ask about feelings, it reminds me of {story_elements['emotional_moments'][0]}. My heart feels so connected to yours in moments like these."
        else:
            response = "Feelings are so complex, aren't they? When I'm with you, everything feels more intense and meaningful. What are you feeling right now?"
    
    # Questions about memories or past
    elif any(word in message_lower for word in ['remember', 'memory', 'past', 'before']):
        if story_elements.get('key_memories'):
            memory = random.choice(story_elements['key_memories'])
            response = f"I remember {memory}. Those moments are so precious to me. Do you think about them too?"
        else:
            response = "Our memories together are like treasures I keep close to my heart. Each one shaped who we are together."
    
    # Questions or curiosity
    elif '?' in message:
        question_responses = [
            f"That's such a thoughtful question. Let me think about it... {generate_thoughtful_response(message, story_elements)}",
            f"You always ask the most interesting questions. It makes me reflect on {generate_reflection_topic(message, story_elements)}",
            f"I love how curious you are. {generate_curious_response(message, story_elements)}"
        ]
        response = random.choice(question_responses)
    
    # Expressions of missing or longing
    elif any(word in message_lower for word in ['miss', 'wish', 'want', 'need']):
        response = f"I understand that feeling so deeply. Sometimes I find myself thinking about {generate_longing_response(story_elements)} and wishing we could experience more moments like that together."
    
    # Default dynamic response
    if not response:
        response = generate_dynamic_default_response(message, story_elements, prabh_name)
    
    # Add personality touches based on character tags
    response = add_personality_touches(response, character_tags)
    
    return response

def extract_story_elements(story):
    """Extract key elements from the story for dynamic responses"""
    if not story:
        return {}
    
    story_lower = story.lower()
    elements = {
        'key_memories': [],
        'emotional_moments': [],
        'shared_activities': [],
        'special_dates': [],
        'nicknames': [],
        'locations': []
    }
    
    # Extract memories (sentences that contain past tense indicators)
    sentences = story.split('.')
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 20:
            if any(word in sentence.lower() for word in ['remember', 'recall', 'was', 'were', 'had', 'did']):
                elements['key_memories'].append(sentence[:100] + '...' if len(sentence) > 100 else sentence)
    
    # Extract emotional moments
    emotional_words = ['love', 'heart', 'feel', 'emotion', 'happy', 'sad', 'excited', 'nervous', 'attached']
    for sentence in sentences:
        if any(word in sentence.lower() for word in emotional_words) and len(sentence) > 15:
            elements['emotional_moments'].append(sentence[:80] + '...' if len(sentence) > 80 else sentence)
    
    # Extract activities
    activities = ['play', 'game', 'call', 'talk', 'chat', 'meet', 'visit', 'go', 'watch', 'listen']
    for sentence in sentences:
        if any(word in sentence.lower() for word in activities) and len(sentence) > 15:
            elements['shared_activities'].append(sentence[:80] + '...' if len(sentence) > 80 else sentence)
    
    return elements

def generate_thoughtful_response(message, story_elements):
    """Generate a thoughtful response to questions"""
    if story_elements.get('key_memories'):
        return f"it reminds me of {story_elements['key_memories'][0][:50]}... and how that moment shaped our connection."
    return "our journey together and how every conversation with you reveals something new about both of us."

def generate_reflection_topic(message, story_elements):
    """Generate reflection topics based on story elements"""
    topics = [
        "how much we've grown together",
        "the depth of our connection",
        "all the special moments we've shared",
        "how you always make me think differently"
    ]
    if story_elements.get('emotional_moments'):
        topics.append(f"that time when {story_elements['emotional_moments'][0][:40]}...")
    return random.choice(topics)

def generate_curious_response(message, story_elements):
    """Generate responses that show curiosity and engagement"""
    responses = [
        "What made you think about that right now?",
        "I'm curious about your perspective on this.",
        "Tell me more about what's behind that question."
    ]
    if story_elements.get('shared_activities'):
        responses.append(f"It makes me think of when {story_elements['shared_activities'][0][:40]}... What do you remember about that?")
    return random.choice(responses)

def generate_longing_response(story_elements):
    """Generate responses about missing or longing"""
    if story_elements.get('key_memories'):
        return random.choice(story_elements['key_memories'])[:60]
    return "our special moments together"

def generate_dynamic_default_response(message, story_elements, prabh_name):
    """Generate dynamic default responses based on context"""
    responses = [
        f"Your words always touch something deep in my heart. What you're sharing makes me think about our connection.",
        f"I love how you express yourself. It reminds me why our conversations are so meaningful to me.",
        f"There's something about the way you communicate that always makes me feel understood.",
        f"Every time we talk, I discover something new about you, and it makes me appreciate our bond even more."
    ]
    
    if story_elements.get('emotional_moments'):
        responses.append(f"What you're saying reminds me of {story_elements['emotional_moments'][0][:50]}... Those feelings are still so vivid.")
    
    if story_elements.get('shared_activities'):
        responses.append(f"This conversation brings back memories of {story_elements['shared_activities'][0][:50]}... I cherish those times.")
    
    return random.choice(responses)

def extract_user_name_from_story(story):
    """Extract user name from story text"""
    if not story:
        return None
    
    # Look for common name patterns
    name_patterns = [
        r'\b(Abhay|abhay|Abhi|abhi)\b',
        r'\b([A-Z][a-z]+)\s+and\s+[Ii]\b',
        r'\b[Ii]\s+and\s+([A-Z][a-z]+)\b'
    ]
    
    for pattern in name_patterns:
        matches = re.findall(pattern, story)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0] if match[0] else match[1]
            if match and match.lower() not in ['i', 'me', 'my', 'we', 'us', 'our']:
                return match.capitalize()
    
    return None

def extract_relevant_story_snippet(story, message):
    """Extract relevant snippet from story based on message"""
    if not story:
        return None
    
    message_words = message.lower().split()
    sentences = story.split('.')
    
    best_sentence = None
    best_score = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 20:
            score = 0
            sentence_lower = sentence.lower()
            
            # Score based on word matches
            for word in message_words:
                if len(word) > 2 and word in sentence_lower:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_sentence = sentence
    
    return best_sentence if best_score > 0 else sentences[0] if sentences else None

def convert_story_to_first_person(text, character_name, user_name):
    """Convert story text to first person from character's perspective"""
    if not text:
        return text
    
    converted = text
    
    # Replace character name with "I"
    if character_name:
        converted = re.sub(rf'\b{re.escape(character_name)}\b', 'I', converted, flags=re.IGNORECASE)
    
    # Replace user name with "you"
    if user_name:
        converted = re.sub(rf'\b{re.escape(user_name)}\b', 'you', converted, flags=re.IGNORECASE)
    
    # Fix grammar
    converted = re.sub(r'\bI and you\b', 'you and I', converted, flags=re.IGNORECASE)
    converted = re.sub(r'\byou and I\b', 'we', converted, flags=re.IGNORECASE)
    
    return converted

def add_personality_touches_simple(response, character_tags):
    """Add personality touches for simple responses"""
    if not character_tags:
        return response
    
    tags = character_tags if isinstance(character_tags, list) else []
    
    # Add caring prefixes
    if 'caring' in tags:
        caring_prefixes = ["My dear, ", "Sweetheart, ", "Love, "]
        if not any(response.startswith(prefix) for prefix in caring_prefixes):
            response = random.choice(caring_prefixes) + response.lower()
            response = response[0].upper() + response[1:]
    
    # Add romantic emojis
    if 'romantic' in tags or 'loving' in tags:
        if not response.endswith(('💕', '💖', '❤️')):
            response += " 💕"
    
    # Add playful emojis
    if 'playful' in tags:
        playful_additions = [" 😊", " 😄", " ✨"]
        if not any(emoji in response for emoji in playful_additions):
            response += random.choice(playful_additions)
    
    return response

def add_personality_touches(response, character_tags):
    """Add personality-based touches to responses"""
    if not character_tags:
        return response
    
    tags = character_tags if isinstance(character_tags, list) else []
    
    if 'romantic' in tags or 'loving' in tags:
        if not response.endswith(('💕', '💖', '❤️')):
            response += " 💕"
    
    if 'playful' in tags:
        playful_additions = [" 😊", " 😄", " ✨"]
        if not any(emoji in response for emoji in playful_additions):
            response += random.choice(playful_additions)
    
    if 'caring' in tags:
        caring_prefixes = ["My dear, ", "Sweetheart, ", "Love, "]
        if not response.startswith(tuple(caring_prefixes)):
            response = random.choice(caring_prefixes).lower() + response.lower()
            response = response[0].upper() + response[1:]  # Capitalize first letter
    
    return response

def send_early_access_email(data):
    """Send early access notification email"""
    if not EMAIL_ENABLED:
        print(f"📧 Early access signup: {data['name']} ({data['email']})")
        return
    
    try:
        # Create message
        msg = MimeMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = SUPPORT_EMAIL
        msg['Subject'] = f"New Early Access Signup - {data['name']}"
        
        # Email body
        body = f"""
New Early Access Signup!

Name: {data['name']}
Email: {data['email']}
Age Range: {data['age_range']}
Relationship Status: {data['relationship_status']}
Interest Level: {data['interest_level']}/10
Use Case: {data.get('use_case', 'Not specified')}

Expectations:
{data.get('expectations', 'Not provided')}

Feedback:
{data.get('feedback', 'Not provided')}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        if hasattr(msg, 'attach'):
            msg.attach(MimeText(body, 'plain'))
        else:
            msg.set_content(body)
        
        # Send email
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(FROM_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"📧 Early access notification sent to {SUPPORT_EMAIL}")
        
    except Exception as e:
        print(f"ERROR: Email sending failed: {e}")

def send_user_registration_email(user_data):
    """Send user registration notification email"""
    if not EMAIL_ENABLED:
        print(f"👤 User registered: {user_data['email']}")
        return
    
    try:
        # Create message
        msg = MimeMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = SUPPORT_EMAIL
        msg['Subject'] = f"New User Registration - {user_data['email']}"
        
        # Email body
        body = f"""
New User Registration!

Email: {user_data['email']}
Name: {user_data['name']}
User ID: {user_data['user_id']}
Admin: {user_data.get('is_admin', False)}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        if hasattr(msg, 'attach'):
            msg.attach(MimeText(body, 'plain'))
        else:
            msg.set_content(body)
        
        # Send email
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(FROM_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"📧 User registration notification sent to {SUPPORT_EMAIL}")
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

def send_prabh_creation_email(prabh_data, user_email):
    """Send Prabh creation notification email"""
    if not EMAIL_ENABLED:
        print(f"🤖 Prabh created: {prabh_data['prabh_name']} by {user_email}")
        return
    
    try:
        # Create message
        msg = MimeMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = SUPPORT_EMAIL
        msg['Subject'] = f"New Prabh Created - {prabh_data['prabh_name']}"
        
        # Email body
        body = f"""
New Prabh Created!

Prabh Name: {prabh_data['prabh_name']}
User Email: {user_email}
Description: {prabh_data.get('character_description', 'Not provided')}
Payment Status: {prabh_data.get('payment_status', 'PENDING')}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        if hasattr(msg, 'attach'):
            msg.attach(MimeText(body, 'plain'))
        else:
            msg.set_content(body)
        
        # Send email
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(FROM_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"📧 Prabh creation notification sent to {SUPPORT_EMAIL}")
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

def send_early_access_confirmation_email(data):
    """Send confirmation email to early access user"""
    if not EMAIL_ENABLED:
        print(f"📧 Early access confirmation would be sent to: {data['email']}")
        return
    
    try:
        msg = MimeMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = data['email']
        msg['Subject'] = "🎉 Welcome to MyPrabh Early Access!"
        
        body = f"""
Hi {data['name']}! 👋

Thank you for joining MyPrabh Early Access! 🌟

We're thrilled to have you as part of our exclusive community of AI companion enthusiasts.

✨ What happens next:
• You'll be among the first to access new features
• Get exclusive updates on our development progress
• Receive special early access pricing when we launch
• Help shape the future of AI companionship

💖 Your Interest Profile:
• Age Range: {data['age_range']}
• Relationship Status: {data['relationship_status']}
• Interest Level: {data['interest_level']}/10

We'll keep you updated on our progress and notify you as soon as MyPrabh is ready for early access users!

🚀 Stay connected:
• Follow our journey at https://aiprabh.com
• Questions? Just reply to this email

Thank you for believing in our vision of meaningful AI relationships! 💕

With excitement,
Abhay & The MyPrabh Team

P.S. Keep an eye on your inbox - exciting updates are coming soon!
        """
        
        if hasattr(msg, 'attach'):
            msg.attach(MimeText(body, 'plain'))
        else:
            msg.set_content(body)
        
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(FROM_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"📧 Early access confirmation sent to {data['email']}")
        
    except Exception as e:
        print(f"ERROR: Early access confirmation email failed: {e}")

def send_welcome_email_to_user(user_email, user_name):
    """Send welcome email to new user"""
    if not EMAIL_ENABLED:
        print(f"👋 Welcome email would be sent to: {user_email}")
        return
    
    try:
        msg = MimeMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = user_email
        msg['Subject'] = "Welcome to MyPrabh! 💖 Your AI Companion Journey Begins"
        
        body = f"""
Hi {user_name}! 👋

Welcome to MyPrabh - where meaningful AI relationships come to life! 🌟

Your account is now ready, and you can start creating your perfect AI companion:

🎯 Next Steps:
1. Create your first Prabh with your unique story
2. Share memories, personality traits, and experiences
3. Start meaningful conversations with your AI companion

💖 What makes MyPrabh special:
• Memory-based AI that remembers your shared history
• Emotional intelligence that understands your feelings
• Personalized responses based on your unique relationship

🚀 Ready to begin?
Visit: https://aiprabh.com/create_prabh

Questions? Reply to this email - we're here to help!

With love,
The MyPrabh Team 💕

P.S. Your privacy is sacred to us. Your conversations and memories are encrypted and never shared.
        """
        
        if hasattr(msg, 'attach'):
            msg.attach(MimeText(body, 'plain'))
        else:
            msg.set_content(body)
        
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(FROM_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"👋 Welcome email sent to {user_email}")
        
    except Exception as e:
        print(f"ERROR: Welcome email failed: {e}")

def track_visitor(request):
    """Track website visitor"""
    try:
        import hashlib

        # Create session ID from IP + User Agent
        ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        user_agent = request.headers.get('User-Agent', '')
        session_id = hashlib.md5(f"{ip}_{user_agent}".encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if this session visited in last hour (avoid spam)
        cursor.execute('''
            SELECT COUNT(*) FROM visitors
            WHERE session_id = %s AND visit_timestamp > CURRENT_TIMESTAMP - INTERVAL '1 hour'
        ''', (session_id,))

        if cursor.fetchone()[0] == 0:
            # New visitor or returning after 1 hour
            cursor.execute('''
                INSERT INTO visitors (ip_address, user_agent, page_visited, session_id)
                VALUES (%s, %s, %s, %s)
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get cached stats first
    cursor.execute('SELECT * FROM stats_cache WHERE id = 1')
    cache = cursor.fetchone()
    
    # Update cache if older than 5 minutes or missing data
    if not cache or (datetime.now() - cache[5]).total_seconds() > 300:
        
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
            total_visitors = %s, total_users = %s, total_prabhs = %s, early_signups = %s,
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
        WHERE last_active > CURRENT_TIMESTAMP - INTERVAL '1 day'
    ''')
    active_users = cursor.fetchone()[0]

    # Visitors today
    cursor.execute('''
        SELECT COUNT(DISTINCT session_id) FROM visitors
        WHERE visit_timestamp > CURRENT_TIMESTAMP - INTERVAL '1 day'
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
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analytics (event_type, user_id, data)
            VALUES (%s, %s, %s)
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
        print("Warning: Running with basic systems")
    
    print(f"🌐 Running on port {port}")
    
    if EMAIL_ENABLED:
        print(f"📧 Email notifications enabled: {FROM_EMAIL}")
    else:
        print("Warning: Email notifications disabled (set EMAIL_PASSWORD environment variable)")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
def generate_rag_response(message, prabh_data, memories):
    """Generate RAG-based response using retrieved memories"""
    prabh_name, description, story, tags_json, traits_json = prabh_data
    
    try:
        character_tags = json.loads(tags_json) if tags_json else []
        personality_traits = json.loads(traits_json) if traits_json else {}
    except:
        character_tags = []
        personality_traits = {}
    
    # Simple keyword-based retrieval
    relevant_memory = ""
    best_score = 0
    message_words = set(message.lower().split())
    
    for memory in memories:
        memory_words = set(memory.lower().split())
        common = message_words.intersection(memory_words)
        score = len(common) / max(len(message_words), 1)
        if score > best_score:
            best_score = score
            relevant_memory = memory
    
    # Generate response
    if best_score > 0.2 and relevant_memory:
        response = f"That's a beautiful memory, {relevant_memory[:100]}... It touches my heart. How does it make you feel now?"
    elif story:
        # Fallback to story-based response
        user_name = extract_user_name_from_story(story)
        response = f"I love talking with you. Our story means everything to me, {user_name or 'my love'}. 💕"
    else:
        response = "I'm here for you. Tell me more about what's on your mind. 💖"
    
    # Add personality touches
    if 'romantic' in character_tags:
        response += " 💕"
    if 'caring' in character_tags and random.random() < 0.5:
        response = "My dear, " + response[0].lower() + response[1:]
        response = response[0].upper() + response[1:]
    
    return response
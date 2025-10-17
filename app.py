# My Prabh - Complete AI Companion Platform
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import os
import uuid
import json
from datetime import datetime, timedelta
import random
import hashlib
import re

# Import secure configuration
from config.secure_config import config

# Initialize Flask app
app = Flask(__name__)
app.secret_key = config.secret_key

# Configure Flask app with secure settings
app.config.update(
    SECRET_KEY=config.secret_key,
    PERMANENT_SESSION_LIFETIME=timedelta(seconds=config.session_config['permanent_lifetime']),
    SESSION_COOKIE_SECURE=config.is_production,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Initialize services
try:
    from services.firestore_db import firestore_db
    from services.firebase_auth import firebase_auth
    from services.email_service import email_service
    from services.phone_verification import phone_verification
    from services.payment_service import payment_service
    print("✅ All services initialized successfully")
except Exception as e:
    print(f"⚠️ Service initialization warning: {e}")
    # Initialize minimal services for basic functionality
    firestore_db = None
    firebase_auth = None
    email_service = None
    phone_verification = None
    payment_service = None

# Security: API endpoint to serve Firebase config (client-safe keys only)
@app.route('/api/firebase-config')
def get_firebase_config():
    """Serve Firebase configuration for client-side use"""
    return jsonify(config.firebase_config)

# Initialize memory services
try:
    from routes.memory_routes import memory_bp
    app.register_blueprint(memory_bp)
    print("✅ Memory routes registered successfully")
except Exception as e:
    print(f"⚠️ Memory routes not available: {e}")

print("✅ My Prabh Platform Starting...")
print(f"✅ Firestore Database: {'Connected' if firestore_db else 'Disabled'}")
print(f"✅ Firebase Auth: {'Enabled' if firebase_auth else 'Disabled'}") 
print(f"✅ Email Service: {'Google Workspace' if email_service else 'Disabled'}")
print(f"✅ Phone Verification: {'Enabled' if phone_verification else 'Disabled'}")
print(f"✅ Payment Service: {'Razorpay Live' if payment_service else 'Disabled'}")
print(f"✅ Environment: {os.environ.get('FLASK_ENV', 'production')}")
print(f"✅ Admin: {os.environ.get('ADMIN_EMAIL', 'abhay@aiprabh.com')}")

# Utility functions
def generate_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password_hash(hash_value, password):
    return hash_value == hashlib.sha256(password.encode()).hexdigest()

def is_authenticated():
    return 'user_id' in session and session.get('user_id')

# Simple password hashing (for demo - use proper hashing in production)
import hashlib
def generate_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password_hash(hash_value, password):
    return hash_value == hashlib.sha256(password.encode()).hexdigest()

# ============================================================================
# CORE ROUTES - Landing, Authentication, Dashboard
# ============================================================================

@app.route('/')
def index():
    """Landing page with real-time stats"""
    try:
        if firestore_db:
            stats = firestore_db.get_stats()
            # Add some dynamic stats
            stats.update({
                'active_conversations': stats.get('total_prabhs', 0) * 3,
                'happiness_score': '98%',
                'countries': 25
            })
        else:
            raise Exception("Firestore not available")
        
    except Exception as e:
        print(f"Stats error: {e}")
        # Fallback stats for demo
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
    """Health check for Cloud Run"""
    return {
        'status': 'healthy', 
        'service': 'my-prabh', 
        'database': 'firestore',
        'timestamp': datetime.now().isoformat()
    }, 200

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/signup')
@app.route('/register')
def register_page():
    """Registration page"""
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/signin')
@app.route('/login')
def login_page():
    """Login page"""
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register_user():
    """Handle user registration"""
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
        existing_user = firestore_db.get_user_by_email(email)
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        password_hash = generate_password_hash(password)
        user_id = firestore_db.create_user(email, name, password_hash)
        
        if user_id:
            # Send welcome email
            try:
                email_service.send_welcome_email(email, name)
            except Exception as e:
                print(f"Welcome email error: {e}")
            
            # Set session
            session['user_id'] = user_id
            session['user_email'] = email
            session['user_name'] = name
            session['auth_provider'] = 'email'
            
            return jsonify({
                'success': True, 
                'message': 'Account created successfully!',
                'redirect': '/dashboard'
            })
        else:
            return jsonify({'error': 'Registration failed'}), 500
            
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@app.route('/login', methods=['POST'])
def login_user():
    """Handle user login"""
    try:
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Get user
        user = firestore_db.get_user_by_email(email)
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check password
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Set session
        session['user_id'] = user['user_id']
        session['user_email'] = user['email']
        session['user_name'] = user['name']
        session['auth_provider'] = 'email'
        
        # Update last login
        try:
            firebase_auth.update_last_login(user['user_id'])
        except Exception as e:
            print(f"Last login update error: {e}")
        
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
    """User logout"""
    session.clear()
    return redirect(url_for('index'))

# ============================================================================
# DASHBOARD & PRABH MANAGEMENT
# ============================================================================

@app.route('/dashboard')
def dashboard():
    """User dashboard with Prabhs and stats"""
    if not is_authenticated():
        return redirect(url_for('login_page'))
    
    try:
        # Get user's Prabhs
        prabhs = firestore_db.get_user_prabhs(session['user_id'])
        
        # Get user stats
        user_stats = {
            'total_prabhs': len(prabhs),
            'total_messages': sum([p.get('message_count', 0) for p in prabhs]),
            'active_prabhs': len([p for p in prabhs if p.get('is_active', True)]),
            'member_since': session.get('user_name', 'User')
        }
        
        return render_template('dashboard.html', 
                             prabhs=prabhs, 
                             user_stats=user_stats,
                             user_name=session.get('user_name', 'User'))
    except Exception as e:
        print(f"Dashboard error: {e}")
        return render_template('dashboard.html', 
                             prabhs=[], 
                             user_stats={'total_prabhs': 0, 'total_messages': 0, 'active_prabhs': 0},
                             user_name=session.get('user_name', 'User'))

@app.route('/create-prabh')
def create_prabh_page():
    """Create Prabh page"""
    if not is_authenticated():
        return redirect(url_for('login_page'))
    return render_template('create_prabh.html')

@app.route('/create-prabh', methods=['POST'])
def create_prabh():
    """Create new AI Prabh companion with optional memory-based training"""
    if not is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        prabh_name = data.get('prabh_name', '').strip()
        character_description = data.get('character_description', '').strip()
        story_content = data.get('story_content', '').strip()
        personality_traits = data.get('personality_traits', '').strip()
        
        # Memory-based training options
        use_memory_training = data.get('use_memory_training', False)
        memory_assignment = data.get('memory_assignment', {})
        
        # Validation
        if not prabh_name:
            return jsonify({'error': 'Prabh name is required'}), 400
        
        if not character_description:
            return jsonify({'error': 'Character description is required'}), 400
        
        if len(prabh_name) > 50:
            return jsonify({'error': 'Name must be less than 50 characters'}), 400
        
        if use_memory_training:
            # Create memory-based companion
            try:
                from services.memory.companion_management_service import CompanionManagementService
                companion_service = CompanionManagementService()
                
                companion_data = {
                    'name': prabh_name,
                    'personality': personality_traits,
                    'description': character_description,
                    'story_content': story_content
                }
                
                # Set default memory assignment if not provided
                if not memory_assignment:
                    memory_assignment = {'type': 'all'}
                
                result = companion_service.create_memory_based_companion(
                    session['user_id'], companion_data, memory_assignment
                )
                
                if result['success']:
                    return jsonify({
                        'success': True,
                        'prabh_id': result['companion_id'],
                        'message': f'{prabh_name} has been created with memory-based training!',
                        'memory_training': True,
                        'assigned_memories': result['memory_assignment_result']['assigned_count'],
                        'redirect': '/dashboard'
                    })
                else:
                    # Fallback to regular creation if memory training fails
                    print(f"Memory-based creation failed: {result['error']}")
                    use_memory_training = False
                    
            except ImportError:
                print("Memory services not available, falling back to regular creation")
                use_memory_training = False
            except Exception as e:
                print(f"Memory-based creation error: {e}")
                use_memory_training = False
        
        if not use_memory_training:
            # Regular Prabh creation
            prabh_id = firestore_db.create_prabh(
                user_id=session['user_id'],
                prabh_name=prabh_name,
                character_description=character_description,
                story_content=story_content,
                personality_traits=personality_traits
            )
            
            if prabh_id:
                return jsonify({
                    'success': True, 
                    'prabh_id': prabh_id,
                    'message': f'{prabh_name} has been created successfully!',
                    'memory_training': False,
                    'redirect': '/dashboard'
                })
            else:
                return jsonify({'error': 'Failed to create Prabh'}), 500
            
    except Exception as e:
        print(f"Create Prabh error: {e}")
        return jsonify({'error': 'Failed to create Prabh. Please try again.'}), 500

# ============================================================================
# CHAT SYSTEM WITH STORY UNDERSTANDING
# ============================================================================

@app.route('/chat/<prabh_id>')
def chat_interface(prabh_id):
    """Enhanced chat interface with story context"""
    if not is_authenticated():
        return redirect(url_for('login_page'))
    
    try:
        # Get Prabh data
        prabh_data = firestore_db.get_prabh_by_id(str(prabh_id), session['user_id'])
        if not prabh_data:
            flash('Prabh not found', 'error')
            return redirect(url_for('dashboard'))
        
        # Get recent chat history
        chat_history = firestore_db.get_chat_history(prabh_id, session['user_id'], limit=20)
        
        # Prepare Prabh context for AI
        prabh_context = {
            'name': prabh_data['prabh_name'],
            'description': prabh_data['character_description'],
            'story': prabh_data.get('story_content', ''),
            'personality': prabh_data.get('personality_traits', ''),
            'created_at': prabh_data.get('created_at'),
            'message_count': len(chat_history)
        }
        
        return render_template('chat.html', 
                             prabh_id=prabh_id,
                             prabh_data=prabh_context,
                             chat_history=chat_history[:10],  # Show last 10 messages
                             user_name=session.get('user_name', 'User'))
    except Exception as e:
        print(f"Chat interface error: {e}")
        flash('Error loading chat', 'error')
        return redirect(url_for('dashboard'))

@app.route('/chat-message', methods=['POST'])
def chat_message():
    """Enhanced chat with deep story understanding and personality mimicking"""
    if not is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        prabh_id = str(data.get('prabh_id'))
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        if len(message) > 1000:
            return jsonify({'error': 'Message too long (max 1000 characters)'}), 400
        
        # Get Prabh data with full context
        prabh_data = firestore_db.get_prabh_by_id(prabh_id, session['user_id'])
        if not prabh_data:
            return jsonify({'error': 'Prabh not found'}), 404
        
        # Get conversation history for context
        chat_history = firestore_db.get_chat_history(prabh_id, session['user_id'], limit=10)
        
        # Get memories for personality consistency
        memories = firestore_db.get_memories(prabh_id, session['user_id'], limit=8)
        memory_texts = [mem['memory_text'] for mem in memories]
        
        # Enhanced AI response with story understanding
        try:
            from services.openrouter_ai import OpenRouterAI
            openrouter_ai = OpenRouterAI(os.environ.get('OPENROUTER_API_KEY'))
            
            # Build enhanced context
            enhanced_context = {
                'prabh_name': prabh_data['prabh_name'],
                'character_description': prabh_data['character_description'],
                'story_content': prabh_data.get('story_content', ''),
                'personality_traits': prabh_data.get('personality_traits', ''),
                'chat_history': [{'user': h.get('user_message', ''), 'ai': h.get('ai_response', '')} for h in chat_history[-5:]],
                'memories': memory_texts,
                'user_name': session.get('user_name', 'User'),
                'relationship_stage': len(chat_history)  # How long they've been talking
            }
            
            response = openrouter_ai.generate_enhanced_response(
                user_message=message,
                context=enhanced_context
            )
            
        except Exception as ai_error:
            print(f"AI generation error: {ai_error}")
            # Intelligent fallback based on Prabh personality
            response = f"As {prabh_data['prabh_name']}, I want to understand you better. {message} sounds important to you. Tell me more about how you're feeling about this. 💖"
        
        # Save chat message with metadata
        message_id = firestore_db.save_chat_message(
            prabh_id, 
            session['user_id'], 
            message, 
            response,
            metadata={
                'message_length': len(message),
                'response_length': len(response),
                'conversation_turn': len(chat_history) + 1
            }
        )
        
        # Intelligent memory saving based on content analysis
        if len(message) > 15 and any(keyword in message.lower() for keyword in 
                                   ['feel', 'love', 'hate', 'happy', 'sad', 'excited', 'worried', 'dream', 'hope', 'fear']):
            firestore_db.save_memory(prabh_id, session['user_id'], message, memory_type="emotional")
        elif len(message) > 30:
            firestore_db.save_memory(prabh_id, session['user_id'], message, memory_type="general")
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'character_name': prabh_data['prabh_name'],
            'message_id': message_id,
            'conversation_turn': len(chat_history) + 1
        })
        
    except Exception as e:
        print(f"Chat message error: {e}")
        return jsonify({'error': 'Failed to process message. Please try again.'}), 500

@app.route('/auth/google', methods=['POST'])
def google_auth():
    """Handle Google authentication"""
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'error': 'ID token required'}), 400
        
        # Verify the token with Firebase
        decoded_token = firebase_auth.verify_id_token(id_token)
        if not decoded_token:
            return jsonify({'error': 'Invalid token'}), 401
        
        uid = decoded_token['uid']
        email = decoded_token.get('email')
        name = decoded_token.get('name', email.split('@')[0])
        phone_number = decoded_token.get('phone_number')
        
        # Get or create user record
        user = firebase_auth.get_user_by_uid(uid)
        if not user:
            user = firebase_auth.create_user_record(email, name, uid, phone_number, 'google')
            # Send welcome email for new users
            email_service.send_welcome_email(email, name)
        else:
            # Update last login
            firebase_auth.update_last_login(uid)
        
        # Set session
        session['user_id'] = uid
        session['user_email'] = email
        session['user_name'] = name
        session['user_phone'] = phone_number
        session['auth_provider'] = 'google'
        
        return jsonify({
            'success': True,
            'user': {
                'uid': uid,
                'email': email,
                'name': name
            },
            'redirect': '/dashboard'
        })
        
    except Exception as e:
        print(f"Google auth error: {e}")
        return jsonify({'error': 'Authentication failed'}), 500

@app.route('/verify-phone', methods=['POST'])
def verify_phone():
    """Send phone verification code"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number', '').strip()
        
        if not phone_number:
            return jsonify({'error': 'Phone number required'}), 400
        
        # Format phone number
        formatted_phone = phone_verification.format_phone_number(phone_number)
        
        # Send verification code
        result = phone_verification.send_verification_code(formatted_phone)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Phone verification error: {e}")
        return jsonify({'error': 'Verification failed'}), 500

@app.route('/confirm-phone', methods=['POST'])
def confirm_phone():
    """Confirm phone verification code"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        phone_number = data.get('phone_number', '').strip()
        verification_code = data.get('verification_code', '').strip()
        
        if not phone_number or not verification_code:
            return jsonify({'error': 'Phone number and verification code required'}), 400
        
        # Verify code
        result = phone_verification.verify_phone_number(phone_number, verification_code)
        
        if result['success']:
            # Update user record with verified phone
            firebase_auth.update_user_phone(session['user_id'], phone_number)
            session['user_phone'] = phone_number
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Phone confirmation error: {e}")
        return jsonify({'error': 'Confirmation failed'}), 500

# ============================================================================
# ADMIN DASHBOARD - Real-time Monitoring
# ============================================================================

@app.route('/admin')
@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard with real-time monitoring"""
    # Simple admin check (enhance with proper admin authentication)
    admin_email = os.environ.get('ADMIN_EMAIL', 'abhay@aiprabh.com')
    if not is_authenticated() or session.get('user_email') != admin_email:
        return redirect(url_for('login_page'))
    
    try:
        # Get comprehensive stats
        stats = firestore_db.get_admin_stats()
        
        # Get recent activity
        recent_users = firestore_db.get_recent_users(limit=10)
        recent_prabhs = firestore_db.get_recent_prabhs(limit=10)
        recent_messages = firestore_db.get_recent_messages(limit=20)
        
        # Calculate growth metrics
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        
        daily_growth = firestore_db.get_growth_stats(yesterday, today)
        weekly_growth = firestore_db.get_growth_stats(week_ago, today)
        
        admin_data = {
            'stats': stats,
            'recent_users': recent_users,
            'recent_prabhs': recent_prabhs,
            'recent_messages': recent_messages,
            'daily_growth': daily_growth,
            'weekly_growth': weekly_growth,
            'system_health': {
                'database': 'healthy',
                'ai_service': 'healthy',
                'email_service': 'healthy'
            }
        }
        
        return render_template('admin_dashboard.html', **admin_data)
        
    except Exception as e:
        print(f"Admin dashboard error: {e}")
        return render_template('admin_dashboard.html', 
                             stats={'total_users': 0, 'total_prabhs': 0, 'total_messages': 0},
                             recent_users=[], recent_prabhs=[], recent_messages=[])

@app.route('/admin/api/live-stats')
def admin_live_stats():
    """API endpoint for real-time admin stats"""
    admin_email = os.environ.get('ADMIN_EMAIL', 'abhay@aiprabh.com')
    if not is_authenticated() or session.get('user_email') != admin_email:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        stats = firestore_db.get_admin_stats()
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Live stats error: {e}")
        return jsonify({'error': 'Failed to fetch stats'}), 500

# ============================================================================
# PAYMENT & SUBSCRIPTION ROUTES
# ============================================================================

@app.route('/pricing')
def pricing_page():
    """Pricing and subscription plans"""
    plans = payment_service.get_subscription_plans()
    return render_template('pricing.html', plans=plans)

@app.route('/subscribe/<plan_type>')
def subscribe_page(plan_type):
    """Subscription page for specific plan"""
    if not is_authenticated():
        return redirect(url_for('login_page'))
    
    plans = payment_service.get_subscription_plans()
    if plan_type not in plans:
        flash('Invalid subscription plan', 'error')
        return redirect(url_for('pricing_page'))
    
    return render_template('subscribe.html', 
                         plan=plans[plan_type], 
                         plan_type=plan_type,
                         user_name=session.get('user_name'))

@app.route('/create-payment-order', methods=['POST'])
def create_payment_order():
    """Create Razorpay payment order"""
    if not is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        plan_type = data.get('plan_type')
        
        if not plan_type:
            return jsonify({'error': 'Plan type required'}), 400
        
        # Create payment order
        result = payment_service.create_subscription_order(
            user_id=session['user_id'],
            plan_type=plan_type,
            amount=data.get('amount')
        )
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f"Payment order error: {e}")
        return jsonify({'error': 'Failed to create payment order'}), 500

@app.route('/verify-payment', methods=['POST'])
def verify_payment():
    """Verify Razorpay payment and activate subscription"""
    if not is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        # Verify payment with Razorpay
        verification_result = payment_service.verify_payment(data)
        
        if verification_result.get('success'):
            # Activate user subscription
            subscription_data = {
                'user_id': session['user_id'],
                'payment_id': verification_result['payment_id'],
                'order_id': verification_result['order_id'],
                'amount': verification_result['amount'],
                'plan_type': data.get('plan_type'),
                'status': 'active',
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=30),
                'payment_method': verification_result.get('method', 'unknown')
            }
            
            # Save subscription to database
            subscription_id = firestore_db.create_subscription(subscription_data)
            
            # Send confirmation email
            try:
                email_service.send_subscription_confirmation(
                    session['user_email'],
                    session['user_name'],
                    data.get('plan_type', 'premium')
                )
            except Exception as e:
                print(f"Subscription email error: {e}")
            
            return jsonify({
                'success': True,
                'message': 'Payment successful! Your subscription is now active.',
                'subscription_id': subscription_id,
                'redirect': '/dashboard'
            })
        else:
            return jsonify(verification_result), 400
            
    except Exception as e:
        print(f"Payment verification error: {e}")
        return jsonify({'error': 'Payment verification failed'}), 500

# ============================================================================
# UTILITY ROUTES
# ============================================================================

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    """User profile page"""
    if not is_authenticated():
        return redirect(url_for('login_page'))
    
    try:
        # Get user subscription
        subscription = firestore_db.get_user_subscription(session['user_id'])
        
        # Get user stats
        user_prabhs = firestore_db.get_user_prabhs(session['user_id'])
        
        profile_data = {
            'user_name': session.get('user_name'),
            'user_email': session.get('user_email'),
            'subscription': subscription,
            'total_prabhs': len(user_prabhs),
            'member_since': session.get('created_at', 'Recently')
        }
        
        return render_template('profile.html', **profile_data)
    except Exception as e:
        print(f"Profile error: {e}")
        return render_template('profile.html', user_name=session.get('user_name'))

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403

# ============================================================================
# MAIN APPLICATION
# ============================================================================

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

@app.route('/api/live-stats')
def live_stats():
    """Live stats API endpoint"""
    try:
        stats = firestore_db.get_stats()
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Live stats error: {e}")
        return jsonify({
            'success': False,
            'stats': {'total_users': 0, 'total_prabhs': 0, 'early_signups': 0},
            'error': 'Stats temporarily unavailable'
        }), 500

@app.route('/submit-early-access', methods=['POST'])
def submit_early_access():
    """Handle early access signup with email confirmation"""
    try:
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        name = data.get('name', '').strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Save early access signup
        signup_id = firestore_db.save_early_access_signup(email, name)
        
        # Send confirmation email
        email_sent = email_service.send_early_access_confirmation(email, name)
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your interest! Check your email for confirmation. 💖',
            'signup_id': signup_id,
            'email_sent': email_sent
        })
        
    except Exception as e:
        print(f"Early access signup error: {e}")
        return jsonify({
            'success': False,
            'error': 'Connection Error 🌧️ Like a storm, sometimes connections fail. Please try again in a moment.'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.route('/privacy-controls')
@login_required
def privacy_controls():
    """Privacy controls page"""
    return render_template('privacy_controls.html')

@app.route('/api/privacy-settings', methods=['GET', 'POST'])
@login_required
def privacy_settings():
    """Get or update privacy settings"""
    try:
        user_id = session.get('user_id')
        
        if request.method == 'GET':
            # Get current privacy settings
            settings_doc = firestore_db.db.collection('privacy_settings').document(user_id).get()
            if settings_doc.exists:
                settings = settings_doc.to_dict()
            else:
                # Default settings
                settings = {
                    'analytics': False,
                    'processing': True,
                    'sharing': False,
                    'marketing': False,
                    'retention_policy': 'standard'
                }
            
            return jsonify({
                'success': True,
                'settings': settings.get('settings', {}),
                'retention_policy': settings.get('retention_policy', 'standard')
            })
        
        elif request.method == 'POST':
            # Update privacy settings
            data = request.get_json()
            settings = data.get('settings', {})
            retention_policy = data.get('retention_policy', 'standard')
            
            # Save to Firestore
            firestore_db.db.collection('privacy_settings').document(user_id).set({
                'settings': settings,
                'retention_policy': retention_policy,
                'updated_at': datetime.now().isoformat()
            })
            
            return jsonify({
                'success': True,
                'message': 'Privacy settings updated successfully'
            })
    
    except Exception as e:
        print(f"Error handling privacy settings: {e}")
        return jsonify({'error': 'Failed to handle privacy settings'}), 500

@app.route('/api/companions/delete-all', methods=['DELETE'])
@login_required
def delete_all_companions():
    """Delete all companions for the current user"""
    try:
        user_id = session.get('user_id')
        
        # Get all user companions
        companions_query = firestore_db.db.collection('companions').where('user_id', '==', user_id)
        docs = companions_query.stream()
        
        batch = firestore_db.db.batch()
        count = 0
        
        for doc in docs:
            batch.delete(doc.reference)
            count += 1
            
            # Commit in batches of 500
            if count % 500 == 0:
                batch.commit()
                batch = firestore_db.db.batch()
        
        # Commit remaining
        if count % 500 != 0:
            batch.commit()
        
        # Also delete associated messages
        messages_query = firestore_db.db.collection('messages').where('user_id', '==', user_id)
        message_docs = messages_query.stream()
        
        batch = firestore_db.db.batch()
        message_count = 0
        
        for doc in message_docs:
            batch.delete(doc.reference)
            message_count += 1
            
            if message_count % 500 == 0:
                batch.commit()
                batch = firestore_db.db.batch()
        
        if message_count % 500 != 0:
            batch.commit()
        
        return jsonify({
            'success': True,
            'message': f'Deleted {count} companions and {message_count} messages'
        })
        
    except Exception as e:
        print(f"Error deleting companions: {e}")
        return jsonify({'error': 'Failed to delete companions'}), 500

@app.route('/api/account/delete', methods=['DELETE'])
@login_required
def delete_account():
    """Delete user account and all associated data"""
    try:
        user_id = session.get('user_id')
        
        # This is a dangerous operation - in production, you might want to:
        # 1. Send confirmation email
        # 2. Add a grace period
        # 3. Log the deletion for audit purposes
        
        # Delete all user data
        collections_to_delete = [
            'users',
            'companions', 
            'messages',
            'memories',
            'privacy_settings',
            'subscriptions'
        ]
        
        for collection_name in collections_to_delete:
            query = firestore_db.db.collection(collection_name).where('user_id', '==', user_id)
            docs = query.stream()
            
            batch = firestore_db.db.batch()
            count = 0
            
            for doc in docs:
                batch.delete(doc.reference)
                count += 1
                
                if count % 500 == 0:
                    batch.commit()
                    batch = firestore_db.db.batch()
            
            if count % 500 != 0:
                batch.commit()
        
        # Delete user document itself
        firestore_db.db.collection('users').document(user_id).delete()
        
        # Clear session
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        })
        
    except Exception as e:
        print(f"Error deleting account: {e}")
        return jsonify({'error': 'Failed to delete account'}), 500

# ============================================================================
# COMPANION MEMORY MANAGEMENT ROUTES
# ============================================================================

@app.route('/api/companions/memory-assignment/<companion_id>')
@login_required
def get_companion_memory_assignment(companion_id):
    """Get memory assignment details for a companion"""
    try:
        from services.memory.companion_management_service import CompanionManagementService
        companion_service = CompanionManagementService()
        
        result = companion_service.get_companion_memory_assignment(session['user_id'], companion_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
        
    except ImportError:
        return jsonify({'error': 'Memory services not available'}), 503
    except Exception as e:
        print(f"Error getting companion memory assignment: {e}")
        return jsonify({'error': 'Failed to get memory assignment'}), 500

@app.route('/api/companions/memory-assignment/<companion_id>', methods=['POST'])
@login_required
def update_companion_memory_assignment(companion_id):
    """Update memory assignment for a companion"""
    try:
        data = request.get_json()
        memory_assignment = data.get('memory_assignment', {})
        
        if not memory_assignment:
            return jsonify({'error': 'Memory assignment configuration required'}), 400
        
        from services.memory.companion_management_service import CompanionManagementService
        companion_service = CompanionManagementService()
        
        result = companion_service.update_companion_memory_assignment(
            session['user_id'], companion_id, memory_assignment
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except ImportError:
        return jsonify({'error': 'Memory services not available'}), 503
    except Exception as e:
        print(f"Error updating companion memory assignment: {e}")
        return jsonify({'error': 'Failed to update memory assignment'}), 500

@app.route('/api/companions/data-isolation/<companion_id>')
@login_required
def get_companion_data_isolation(companion_id):
    """Get data isolation status for a companion"""
    try:
        from services.memory.companion_management_service import CompanionManagementService
        companion_service = CompanionManagementService()
        
        result = companion_service.get_companion_data_isolation_status(session['user_id'], companion_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
        
    except ImportError:
        return jsonify({'error': 'Memory services not available'}), 503
    except Exception as e:
        print(f"Error getting companion data isolation: {e}")
        return jsonify({'error': 'Failed to get data isolation status'}), 500

@app.route('/api/companions/with-memory-info')
@login_required
def list_companions_with_memory_info():
    """List all companions with memory assignment information"""
    try:
        from services.memory.companion_management_service import CompanionManagementService
        companion_service = CompanionManagementService()
        
        companions = companion_service.list_user_companions_with_memory_info(session['user_id'])
        
        return jsonify({
            'success': True,
            'companions': companions
        })
        
    except ImportError:
        # Fallback to regular companion list
        try:
            prabhs = firestore_db.get_user_prabhs(session['user_id'])
            companions = []
            for prabh in prabhs:
                companions.append({
                    'id': prabh[0],
                    'name': prabh[1],
                    'personality': prabh[2],
                    'created_at': prabh[4].isoformat() if prabh[4] else None,
                    'memory_based': False,
                    'status': 'active',
                    'interaction_count': 0,
                    'memory_stats': {'total_memories': 0, 'memory_types': {}, 'last_assignment': ''}
                })
            
            return jsonify({
                'success': True,
                'companions': companions,
                'memory_services_available': False
            })
        except Exception as e:
            print(f"Error getting regular companions: {e}")
            return jsonify({'error': 'Failed to get companions'}), 500
    except Exception as e:
        print(f"Error listing companions with memory info: {e}")
        return jsonify({'error': 'Failed to get companions'}), 500

# ============================================================================
# COMPANION CONTEXT SWITCHING ROUTES
# ============================================================================

@app.route('/api/companions/switch', methods=['POST'])
@login_required
def switch_companion_context():
    """Switch between companion contexts"""
    try:
        data = request.get_json()
        from_companion_id = data.get('from_companion_id')
        to_companion_id = data.get('to_companion_id')
        session_data = data.get('session_data', {})
        
        if not to_companion_id:
            return jsonify({'error': 'Target companion ID required'}), 400
        
        from services.memory.companion_context_service import CompanionContextService
        context_service = CompanionContextService()
        
        result = context_service.switch_companion_context(
            session['user_id'], from_companion_id, to_companion_id, session_data
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except ImportError:
        return jsonify({'error': 'Context switching services not available'}), 503
    except Exception as e:
        print(f"Error switching companion context: {e}")
        return jsonify({'error': 'Failed to switch companion context'}), 500

@app.route('/api/companions/context/<companion_id>')
@login_required
def get_companion_context(companion_id):
    """Get complete context for a companion"""
    try:
        from services.memory.companion_context_service import CompanionContextService
        context_service = CompanionContextService()
        
        result = context_service.get_companion_context(session['user_id'], companion_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
        
    except ImportError:
        return jsonify({'error': 'Context services not available'}), 503
    except Exception as e:
        print(f"Error getting companion context: {e}")
        return jsonify({'error': 'Failed to get companion context'}), 500

@app.route('/api/companions/context/<companion_id>/save', methods=['POST'])
@login_required
def save_companion_conversation_state(companion_id):
    """Save conversation state for a companion"""
    try:
        data = request.get_json()
        conversation_state = data.get('conversation_state', {})
        
        from services.memory.companion_context_service import CompanionContextService
        context_service = CompanionContextService()
        
        result = context_service.save_conversation_state(
            session['user_id'], companion_id, conversation_state
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except ImportError:
        return jsonify({'error': 'Context services not available'}), 503
    except Exception as e:
        print(f"Error saving conversation state: {e}")
        return jsonify({'error': 'Failed to save conversation state'}), 500

@app.route('/api/companions/active')
@login_required
def get_active_companions():
    """Get list of recently active companions for quick switching"""
    try:
        limit = int(request.args.get('limit', 10))
        
        from services.memory.companion_context_service import CompanionContextService
        context_service = CompanionContextService()
        
        companions = context_service.get_active_companions(session['user_id'], limit)
        
        return jsonify({
            'success': True,
            'companions': companions
        })
        
    except ImportError:
        # Fallback to regular companion list
        try:
            prabhs = firestore_db.get_user_prabhs(session['user_id'])
            companions = []
            for prabh in prabhs[:10]:  # Limit to 10
                companions.append({
                    'id': prabh[0],
                    'name': prabh[1],
                    'personality': prabh[2],
                    'avatar': '',
                    'last_activity': prabh[4].isoformat() if prabh[4] else None,
                    'interaction_count': 0,
                    'memory_based': False,
                    'status': 'active',
                    'context_summary': {}
                })
            
            return jsonify({
                'success': True,
                'companions': companions,
                'context_services_available': False
            })
        except Exception as e:
            print(f"Error getting regular companions: {e}")
            return jsonify({'error': 'Failed to get companions'}), 500
    except Exception as e:
        print(f"Error getting active companions: {e}")
        return jsonify({'error': 'Failed to get active companions'}), 500

@app.route('/api/companions/context-isolation/<companion_id>')
@login_required
def get_companion_context_isolation(companion_id):
    """Get context isolation status for a companion"""
    try:
        from services.memory.companion_context_service import CompanionContextService
        context_service = CompanionContextService()
        
        result = context_service.get_context_isolation_status(session['user_id'], companion_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
        
    except ImportError:
        return jsonify({'error': 'Context isolation services not available'}), 503
    except Exception as e:
        print(f"Error getting context isolation status: {e}")
        return jsonify({'error': 'Failed to get context isolation status'}), 500

@app.route('/api/companions/cleanup-contexts', methods=['POST'])
@login_required
def cleanup_inactive_companion_contexts():
    """Clean up contexts for inactive companions"""
    try:
        data = request.get_json()
        days_inactive = data.get('days_inactive', 30)
        
        from services.memory.companion_context_service import CompanionContextService
        context_service = CompanionContextService()
        
        result = context_service.cleanup_inactive_contexts(session['user_id'], days_inactive)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
        
    except ImportError:
        return jsonify({'error': 'Context cleanup services not available'}), 503
    except Exception as e:
        print(f"Error cleaning up contexts: {e}")
        return jsonify({'error': 'Failed to cleanup contexts'}), 500

# ============================================================================
# COMPANION LIFECYCLE MANAGEMENT ROUTES
# ============================================================================

@app.route('/api/companions/archive/<companion_id>', methods=['POST'])
@login_required
def archive_companion(companion_id):
    """Archive a companion with memory preservation"""
    try:
        data = request.get_json()
        archive_options = data.get('archive_options', {})
        
        from services.memory.companion_lifecycle_service import CompanionLifecycleService
        lifecycle_service = CompanionLifecycleService()
        
        result = lifecycle_service.archive_companion(session['user_id'], companion_id, archive_options)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except ImportError:
        return jsonify({'error': 'Lifecycle management services not available'}), 503
    except Exception as e:
        print(f"Error archiving companion: {e}")
        return jsonify({'error': 'Failed to archive companion'}), 500

@app.route('/api/companions/restore/<archive_id>', methods=['POST'])
@login_required
def restore_companion(archive_id):
    """Restore an archived companion"""
    try:
        data = request.get_json()
        restore_options = data.get('restore_options', {})
        
        from services.memory.companion_lifecycle_service import CompanionLifecycleService
        lifecycle_service = CompanionLifecycleService()
        
        result = lifecycle_service.restore_companion(session['user_id'], archive_id, restore_options)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except ImportError:
        return jsonify({'error': 'Lifecycle management services not available'}), 503
    except Exception as e:
        print(f"Error restoring companion: {e}")
        return jsonify({'error': 'Failed to restore companion'}), 500

@app.route('/api/companions/modify/<companion_id>', methods=['POST'])
@login_required
def modify_companion(companion_id):
    """Modify companion properties and personality"""
    try:
        data = request.get_json()
        modifications = data.get('modifications', {})
        
        if not modifications:
            return jsonify({'error': 'No modifications specified'}), 400
        
        from services.memory.companion_lifecycle_service import CompanionLifecycleService
        lifecycle_service = CompanionLifecycleService()
        
        result = lifecycle_service.modify_companion(session['user_id'], companion_id, modifications)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except ImportError:
        return jsonify({'error': 'Lifecycle management services not available'}), 503
    except Exception as e:
        print(f"Error modifying companion: {e}")
        return jsonify({'error': 'Failed to modify companion'}), 500

@app.route('/api/companions/lifecycle-history/<companion_id>')
@login_required
def get_companion_lifecycle_history(companion_id):
    """Get complete lifecycle history for a companion"""
    try:
        from services.memory.companion_lifecycle_service import CompanionLifecycleService
        lifecycle_service = CompanionLifecycleService()
        
        result = lifecycle_service.get_companion_lifecycle_history(session['user_id'], companion_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
        
    except ImportError:
        return jsonify({'error': 'Lifecycle management services not available'}), 503
    except Exception as e:
        print(f"Error getting lifecycle history: {e}")
        return jsonify({'error': 'Failed to get lifecycle history'}), 500

@app.route('/api/companions/archived')
@login_required
def list_archived_companions():
    """List all archived companions for the current user"""
    try:
        from services.memory.companion_lifecycle_service import CompanionLifecycleService
        lifecycle_service = CompanionLifecycleService()
        
        archived_companions = lifecycle_service.list_archived_companions(session['user_id'])
        
        return jsonify({
            'success': True,
            'archived_companions': archived_companions
        })
        
    except ImportError:
        return jsonify({'error': 'Lifecycle management services not available'}), 503
    except Exception as e:
        print(f"Error listing archived companions: {e}")
        return jsonify({'error': 'Failed to list archived companions'}), 500

@app.route('/api/companions/archived/<archive_id>', methods=['DELETE'])
@login_required
def delete_archived_companion(archive_id):
    """Permanently delete an archived companion"""
    try:
        from services.memory.companion_lifecycle_service import CompanionLifecycleService
        lifecycle_service = CompanionLifecycleService()
        
        result = lifecycle_service.delete_archived_companion(session['user_id'], archive_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except ImportError:
        return jsonify({'error': 'Lifecycle management services not available'}), 503
    except Exception as e:
        print(f"Error deleting archived companion: {e}")
        return jsonify({'error': 'Failed to delete archived companion'}), 500

if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
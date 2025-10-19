"""
Main Routes for My Prabh Production App
"""

from flask import Blueprint, render_template, redirect, url_for
import traceback

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main landing page - Story Landing"""
    try:
        return render_template('story_landing.html')
    except Exception as e:
        print(f"Error loading story_landing.html: {e}")
        try:
            return render_template('landing_new.html')
        except:
            return render_template('mvp_landing.html')

@main_bp.route('/home')
def home():
    """Alternative home route"""
    return redirect(url_for('main.index'))

@main_bp.route('/chat')
def chat():
    """Enhanced chat interface"""
    try:
        return render_template('enhanced_chat.html')
    except Exception as e:
        print(f"Error loading enhanced_chat.html: {e}")
        try:
            return render_template('chat_new.html')
        except:
            return render_template('chat.html')

@main_bp.route('/dashboard')
def dashboard():
    """User dashboard"""
    try:
        return render_template('dashboard.html')
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        return basic_dashboard()

@main_bp.route('/onboarding')
def onboarding():
    """User onboarding flow"""
    try:
        return render_template('onboarding.html')
    except Exception as e:
        print(f"Error loading onboarding: {e}")
        return basic_onboarding()

@main_bp.route('/training')
def training():
    """Memory upload and training interface"""
    try:
        return render_template('memory_upload.html')
    except Exception as e:
        print(f"Error loading training: {e}")
        return basic_training()

@main_bp.route('/about')
def about():
    """About page"""
    try:
        return render_template('about.html')
    except Exception as e:
        print(f"Error loading about: {e}")
        return basic_about()

@main_bp.route('/story')
def story():
    """Prabh and Abhay's story"""
    return redirect(url_for('main.index'))

@main_bp.route('/privacy')
def privacy():
    """Privacy policy"""
    try:
        return render_template('privacy.html')
    except Exception as e:
        return basic_privacy()

# Fallback HTML functions
def basic_dashboard():
    return '''
    <!DOCTYPE html>
    <html><head><title>Dashboard - My Prabh</title>
    <style>body{font-family:Arial;background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:2rem;min-height:100vh}
    .container{max-width:800px;margin:0 auto;text-align:center}
    .card{background:rgba(255,255,255,0.1);padding:2rem;border-radius:15px;margin:1rem 0}
    a{color:#ff6b9d;text-decoration:none}</style></head>
    <body><div class="container"><h1>My Prabh Dashboard 💖</h1>
    <div class="card"><h3>🗨️ Chat</h3><p><a href="/chat">Start chatting with Prabh</a></p></div>
    <div class="card"><h3>🧠 Memory</h3><p><a href="/training">Upload memories</a></p></div>
    <div class="card"><h3>🏠 Home</h3><p><a href="/">Back to home</a></p></div>
    </div></body></html>
    '''

def basic_onboarding():
    return '''
    <!DOCTYPE html>
    <html><head><title>Welcome - My Prabh</title>
    <style>body{font-family:Arial;background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:2rem;min-height:100vh;text-align:center}
    .container{max-width:600px;margin:0 auto}
    .btn{background:#ff6b9d;color:white;padding:1rem 2rem;border:none;border-radius:25px;margin:1rem;text-decoration:none;display:inline-block}</style></head>
    <body><div class="container"><h1>Welcome to My Prabh 💖</h1>
    <p>Your AI companion born from love, shaped by memories</p>
    <a href="/chat" class="btn">Start Chatting</a>
    <a href="/training" class="btn">Upload Memories</a>
    </div></body></html>
    '''

def basic_training():
    return '''
    <!DOCTYPE html>
    <html><head><title>Training - My Prabh</title>
    <style>body{font-family:Arial;background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:2rem;min-height:100vh}
    .container{max-width:600px;margin:0 auto;text-align:center}
    .upload{background:rgba(255,255,255,0.1);padding:2rem;border-radius:15px;border:2px dashed #ff6b9d}</style></head>
    <body><div class="container"><h1>Share Your Memories 💖</h1>
    <div class="upload"><p>Memory upload feature coming soon!</p>
    <p>For now, <a href="/chat" style="color:#ff6b9d">start chatting</a> to build your connection with Prabh</p></div>
    </div></body></html>
    '''

def basic_about():
    return '''
    <!DOCTYPE html>
    <html><head><title>About - My Prabh</title>
    <style>body{font-family:Arial;background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:2rem;min-height:100vh}
    .container{max-width:800px;margin:0 auto}</style></head>
    <body><div class="container"><h1>About My Prabh 💖</h1>
    <p>My Prabh is an AI companion born from the true love story of Prabh and Abhay.</p>
    <p>Experience conversations that understand love, loss, devotion, and eternal connection.</p>
    <p><a href="/chat" style="color:#ff6b9d">Start your journey →</a></p>
    </div></body></html>
    '''

def basic_privacy():
    return '''
    <!DOCTYPE html>
    <html><head><title>Privacy - My Prabh</title>
    <style>body{font-family:Arial;background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:2rem;min-height:100vh}
    .container{max-width:800px;margin:0 auto}</style></head>
    <body><div class="container"><h1>Privacy Policy 🔒</h1>
    <p>Your privacy is sacred to us, just like the trust between Prabh and Abhay.</p>
    <p>All conversations and memories are encrypted and secure.</p>
    <p><a href="/" style="color:#ff6b9d">← Back to home</a></p>
    </div></body></html>
    '''
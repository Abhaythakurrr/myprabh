"""
MyPrabh - 3D Cinematic Routes
Enhanced routes for the 3D cinematic user experience
"""

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from functools import wraps
import logging

# Create blueprint for cinematic routes
cinematic_bp = Blueprint('cinematic', __name__, url_prefix='/cinematic')

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin', False):
            return redirect(url_for('cinematic.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@cinematic_bp.route('/')
def landing():
    """3D Cinematic Landing Page"""
    try:
        # Get live stats for the landing page
        stats = {
            'users_count': 1247,
            'companions_count': 3891,
            'conversations_count': 28500,
            'satisfaction_rate': 99.9
        }
        
        return render_template('cinematic_landing.html', 
                             stats=stats,
                             page_title="MyPrabh - 3D Cinematic AI Companion Platform")
    except Exception as e:
        logging.error(f"Error loading cinematic landing: {e}")
        return redirect(url_for('main.index'))

@cinematic_bp.route('/dashboard')
@login_required
def dashboard():
    """3D Cinematic Dashboard"""
    try:
        user_id = session.get('user_id')
        user_name = session.get('user_name', 'User')
        is_admin = session.get('is_admin', False)
        
        # Get user's AI companions (placeholder - replace with actual database query)
        prabh_instances = []
        try:
            # This would be replaced with actual database query
            # prabh_instances = get_user_prabhs(user_id)
            pass
        except Exception as e:
            logging.error(f"Error fetching user companions: {e}")
        
        return render_template('cinematic_dashboard.html',
                             user_name=user_name,
                             is_admin=is_admin,
                             prabh_instances=prabh_instances,
                             page_title=f"Dashboard - {user_name}")
    except Exception as e:
        logging.error(f"Error loading cinematic dashboard: {e}")
        return redirect(url_for('main.dashboard'))

@cinematic_bp.route('/chat/<int:prabh_id>')
@login_required
def chat(prabh_id):
    """3D Cinematic Chat Interface"""
    try:
        user_id = session.get('user_id')
        
        # Get companion details (placeholder - replace with actual database query)
        prabh_name = "AI Companion"
        prabh_description = "Your personalized AI companion with advanced emotional intelligence"
        
        try:
            # This would be replaced with actual database query
            # companion = get_companion_by_id(prabh_id, user_id)
            # prabh_name = companion.name
            # prabh_description = companion.description
            pass
        except Exception as e:
            logging.error(f"Error fetching companion details: {e}")
        
        return render_template('cinematic_chat.html',
                             prabh_id=prabh_id,
                             prabh_name=prabh_name,
                             prabh_description=prabh_description,
                             page_title=f"Chat with {prabh_name}")
    except Exception as e:
        logging.error(f"Error loading cinematic chat: {e}")
        return redirect(url_for('cinematic.dashboard'))

@cinematic_bp.route('/api/live-stats')
def api_live_stats():
    """API endpoint for live statistics"""
    try:
        # This would be replaced with actual database queries
        stats = {
            'visitors': 1247,
            'prabhs_created': 3891,
            'users': 892,
            'early_access': 156,
            'active_users_today': 234,
            'conversations_today': 1456,
            'total_conversations': 28500
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logging.error(f"Error fetching live stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch statistics'
        })

@cinematic_bp.route('/api/user-preferences', methods=['GET', 'POST'])
@login_required
def api_user_preferences():
    """API endpoint for user 3D preferences"""
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        try:
            preferences = request.get_json()
            
            # Validate preferences
            valid_keys = ['enable_3d_effects', 'enable_particles', 'enable_animations', 'reduce_motion']
            filtered_prefs = {k: v for k, v in preferences.items() if k in valid_keys}
            
            # Save preferences (placeholder - replace with actual database update)
            # update_user_preferences(user_id, filtered_prefs)
            
            return jsonify({
                'success': True,
                'message': 'Preferences updated successfully'
            })
        except Exception as e:
            logging.error(f"Error updating user preferences: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to update preferences'
            })
    
    else:  # GET request
        try:
            # Get user preferences (placeholder - replace with actual database query)
            preferences = {
                'enable_3d_effects': True,
                'enable_particles': True,
                'enable_animations': True,
                'reduce_motion': False
            }
            
            return jsonify({
                'success': True,
                'preferences': preferences
            })
        except Exception as e:
            logging.error(f"Error fetching user preferences: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to fetch preferences'
            })

@cinematic_bp.route('/api/performance-metrics', methods=['POST'])
@login_required
def api_performance_metrics():
    """API endpoint to collect performance metrics"""
    try:
        metrics = request.get_json()
        
        # Log performance metrics for monitoring
        logging.info(f"3D Performance Metrics: {metrics}")
        
        # You could store these in a database for analysis
        # store_performance_metrics(session.get('user_id'), metrics)
        
        return jsonify({
            'success': True,
            'message': 'Metrics recorded'
        })
    except Exception as e:
        logging.error(f"Error recording performance metrics: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to record metrics'
        })

@cinematic_bp.route('/api/feedback', methods=['POST'])
@login_required
def api_feedback():
    """API endpoint for 3D experience feedback"""
    try:
        feedback_data = request.get_json()
        user_id = session.get('user_id')
        
        # Validate feedback data
        required_fields = ['rating', 'experience_type', 'comments']
        if not all(field in feedback_data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Missing required feedback fields'
            })
        
        # Store feedback (placeholder - replace with actual database insert)
        # store_user_feedback(user_id, feedback_data)
        
        logging.info(f"3D Experience Feedback from user {user_id}: {feedback_data}")
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your feedback!'
        })
    except Exception as e:
        logging.error(f"Error storing feedback: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to submit feedback'
        })

@cinematic_bp.route('/settings')
@login_required
def settings():
    """3D Experience Settings Page"""
    try:
        user_name = session.get('user_name', 'User')
        
        # Get current user preferences
        preferences = {
            'enable_3d_effects': True,
            'enable_particles': True,
            'enable_animations': True,
            'reduce_motion': False,
            'particle_density': 'medium',
            'animation_speed': 'normal'
        }
        
        return render_template('cinematic_settings.html',
                             user_name=user_name,
                             preferences=preferences,
                             page_title="3D Experience Settings")
    except Exception as e:
        logging.error(f"Error loading cinematic settings: {e}")
        return redirect(url_for('cinematic.dashboard'))

@cinematic_bp.route('/demo')
def demo():
    """3D Effects Demo Page"""
    try:
        return render_template('cinematic_demo.html',
                             page_title="3D Cinematic Demo - MyPrabh")
    except Exception as e:
        logging.error(f"Error loading cinematic demo: {e}")
        return redirect(url_for('cinematic.landing'))

# Error handlers for cinematic routes
@cinematic_bp.errorhandler(404)
def not_found_error(error):
    """Custom 404 page for cinematic routes"""
    return render_template('cinematic_404.html'), 404

@cinematic_bp.errorhandler(500)
def internal_error(error):
    """Custom 500 page for cinematic routes"""
    return render_template('cinematic_500.html'), 500

# Context processor for cinematic templates
@cinematic_bp.context_processor
def inject_cinematic_context():
    """Inject common context for all cinematic templates"""
    return {
        'cinematic_mode': True,
        'version': '1.0.0',
        'enable_debug': False  # Set to True for development
    }

# Template filters for cinematic routes
@cinematic_bp.app_template_filter('format_number')
def format_number(value):
    """Format numbers for display (e.g., 1247 -> 1.2K)"""
    try:
        num = float(value)
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return str(int(num))
    except (ValueError, TypeError):
        return str(value)

@cinematic_bp.app_template_filter('time_ago')
def time_ago(datetime_obj):
    """Convert datetime to human-readable time ago format"""
    try:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        diff = now - datetime_obj
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "Just now"
    except Exception:
        return "Unknown"

# Register the blueprint in your main app.py:
# from routes.cinematic_routes import cinematic_bp
# app.register_blueprint(cinematic_bp)
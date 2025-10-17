"""
Memory Management Routes for My Prabh
Handles memory upload, management, and retrieval endpoints
"""

from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
import os
from datetime import datetime
from werkzeug.utils import secure_filename

# Import memory services
try:
    from services.memory.memory_manager import MemoryManager
    from services.memory.memory_upload_service import MemoryUploadService
    from services.memory.enhanced_ai_service import EnhancedAIService
    from services.memory.personalization_engine import PersonalizationEngine
    from services.memory.emotional_intelligence_service import EmotionalIntelligenceService
    from services.memory.memory_models import SourceType, RetentionPolicy, PrivacyLevel
    from services.firestore_db import firestore_db
    
    # Initialize services
    memory_manager = MemoryManager()
    upload_service = MemoryUploadService()
    personalization_engine = PersonalizationEngine()
    emotional_service = EmotionalIntelligenceService()
    
    MEMORY_SERVICES_AVAILABLE = True
    print("✅ Memory services loaded successfully")
    
except ImportError as e:
    print(f"⚠️ Memory services not available: {e}")
    MEMORY_SERVICES_AVAILABLE = False
    memory_manager = None
    upload_service = None
    personalization_engine = None
    emotional_service = None

# Create blueprint
memory_bp = Blueprint('memory', __name__, url_prefix='/memory')

def is_authenticated():
    """Check if user is authenticated"""
    return 'user_id' in session and session.get('user_id')

def require_auth():
    """Decorator to require authentication"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    return None

def require_memory_services():
    """Check if memory services are available"""
    if not MEMORY_SERVICES_AVAILABLE:
        return jsonify({'error': 'Memory services not available'}), 503
    return None

# ============================================================================
# MEMORY UPLOAD ROUTES
# ============================================================================

@memory_bp.route('/upload')
def upload_page():
    """Memory upload page"""
    auth_check = require_auth()
    if auth_check:
        return redirect(url_for('login_page'))
    
    try:
        # Get user's companions
        user_prabhs = []
        if firestore_db:
            user_prabhs = firestore_db.get_user_prabhs(session['user_id'])
        
        return render_template('memory_upload.html', 
                             user_prabhs=user_prabhs,
                             user_name=session.get('user_name', 'User'))
    except Exception as e:
        print(f"Error loading upload page: {e}")
        return render_template('memory_upload.html', 
                             user_prabhs=[],
                             user_name=session.get('user_name', 'User'))

@memory_bp.route('/api/upload', methods=['POST'])
def upload_memory():
    """Upload memory file"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get form data
        companion_id = request.form.get('companion_id')
        retention_policy = request.form.get('retention_policy', 'long_term')
        privacy_level = request.form.get('privacy_level', 'private')
        
        if not companion_id:
            return jsonify({'error': 'Companion ID is required'}), 400
        
        # Verify companion ownership
        companion = firestore_db.get_prabh_by_id(companion_id, session['user_id'])
        if not companion:
            return jsonify({'error': 'Companion not found or access denied'}), 404
        
        # Read file data
        file_data = file.read()
        file_type = file.content_type or 'application/octet-stream'
        filename = secure_filename(file.filename)
        
        # Upload and process file
        session_id = upload_service.upload_and_process_file(
            user_id=session['user_id'],
            companion_id=companion_id,
            file_data=file_data,
            file_type=file_type,
            filename=filename,
            metadata={
                'retention_policy': retention_policy,
                'privacy_level': privacy_level,
                'uploaded_at': datetime.now().isoformat(),
                'original_filename': file.filename
            }
        )
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': f'File "{filename}" uploaded and processed successfully'
        })
        
    except Exception as e:
        print(f"Error uploading memory: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# MEMORY MANAGEMENT ROUTES
# ============================================================================

@memory_bp.route('/manage')
def manage_page():
    """Memory management dashboard"""
    auth_check = require_auth()
    if auth_check:
        return redirect(url_for('login_page'))
    
    try:
        # Get user's companions
        user_prabhs = []
        if firestore_db:
            user_prabhs = firestore_db.get_user_prabhs(session['user_id'])
        
        # Get memory statistics
        memory_stats = {}
        if MEMORY_SERVICES_AVAILABLE:
            memory_stats = memory_manager.get_user_memory_stats(session['user_id'])
        
        return render_template('memory_manage.html',
                             user_prabhs=user_prabhs,
                             memory_stats=memory_stats,
                             user_name=session.get('user_name', 'User'))
    except Exception as e:
        print(f"Error loading memory management page: {e}")
        return render_template('memory_manage.html',
                             user_prabhs=[],
                             memory_stats={},
                             user_name=session.get('user_name', 'User'))

@memory_bp.route('/api/stats/<companion_id>')
def get_memory_stats(companion_id):
    """Get memory statistics for a companion"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        # Verify companion ownership
        companion = firestore_db.get_prabh_by_id(companion_id, session['user_id'])
        if not companion:
            return jsonify({'error': 'Companion not found'}), 404
        
        # Get memory statistics
        stats = memory_manager.get_user_memory_stats(session['user_id'], companion_id)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        print(f"Error getting memory stats: {e}")
        return jsonify({'error': str(e)}), 500

@memory_bp.route('/api/search', methods=['POST'])
def search_memories():
    """Search memories by text"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        companion_id = data.get('companion_id')
        limit = min(int(data.get('limit', 20)), 50)  # Max 50 results
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        if not companion_id:
            return jsonify({'error': 'Companion ID is required'}), 400
        
        # Verify companion ownership
        companion = firestore_db.get_prabh_by_id(companion_id, session['user_id'])
        if not companion:
            return jsonify({'error': 'Companion not found'}), 404
        
        # Search memories
        results = memory_manager.search_memories_by_text(
            user_id=session['user_id'],
            companion_id=companion_id,
            search_text=query,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'results': results,
            'query': query,
            'total_results': len(results)
        })
        
    except Exception as e:
        print(f"Error searching memories: {e}")
        return jsonify({'error': str(e)}), 500

@memory_bp.route('/api/delete/<memory_id>', methods=['DELETE'])
def delete_memory(memory_id):
    """Delete a specific memory"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        # Delete memory
        success = memory_manager.delete_memory(memory_id, session['user_id'])
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Memory deleted successfully'
            })
        else:
            return jsonify({'error': 'Memory not found or access denied'}), 404
            
    except Exception as e:
        print(f"Error deleting memory: {e}")
        return jsonify({'error': str(e)}), 500

@memory_bp.route('/api/delete-all/<companion_id>', methods=['DELETE'])
def delete_all_memories(companion_id):
    """Delete all memories for a companion"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        # Verify companion ownership
        companion = firestore_db.get_prabh_by_id(companion_id, session['user_id'])
        if not companion:
            return jsonify({'error': 'Companion not found'}), 404
        
        # Delete all memories
        success = memory_manager.delete_all_user_memories(session['user_id'], companion_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'All memories deleted successfully'
            })
        else:
            return jsonify({'error': 'Failed to delete memories'}), 500
            
    except Exception as e:
        print(f"Error deleting all memories: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# PERSONALIZATION ROUTES
# ============================================================================

@memory_bp.route('/api/personality/<companion_id>')
def get_personality_profile(companion_id):
    """Get personality profile for a companion"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        # Verify companion ownership
        companion = firestore_db.get_prabh_by_id(companion_id, session['user_id'])
        if not companion:
            return jsonify({'error': 'Companion not found'}), 404
        
        # Get personality profile
        profile = personalization_engine.get_personality_profile(session['user_id'], companion_id)
        
        if profile:
            return jsonify({
                'success': True,
                'profile': profile.to_dict()
            })
        else:
            return jsonify({
                'success': True,
                'profile': None,
                'message': 'No personality profile found. Upload more memories to generate one.'
            })
            
    except Exception as e:
        print(f"Error getting personality profile: {e}")
        return jsonify({'error': str(e)}), 500

@memory_bp.route('/api/insights/<companion_id>')
def get_personalization_insights(companion_id):
    """Get personalization insights for a companion"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        # Verify companion ownership
        companion = firestore_db.get_prabh_by_id(companion_id, session['user_id'])
        if not companion:
            return jsonify({'error': 'Companion not found'}), 404
        
        # Get personalization insights (this would be implemented in enhanced_ai_service)
        insights = {
            'memory_insights': {
                'total_memories': 0,
                'content_richness': 'low'
            },
            'personality_insights': [],
            'personalization_level': 'basic',
            'recommendations': ['Upload more memories to improve personalization']
        }
        
        return jsonify({
            'success': True,
            'insights': insights
        })
        
    except Exception as e:
        print(f"Error getting personalization insights: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# COMPANION PERSONALIZATION ROUTES
# ============================================================================

@memory_bp.route('/personalize/<companion_id>')
def personalize_companion(companion_id):
    """Companion personalization page"""
    auth_check = require_auth()
    if auth_check:
        return redirect(url_for('login_page'))
    
    try:
        # Verify companion ownership
        companion = firestore_db.get_prabh_by_id(companion_id, session['user_id'])
        if not companion:
            return redirect(url_for('memory.manage_page'))
        
        return render_template('companion_personalization.html',
                             companion=companion,
                             user_name=session.get('user_name', 'User'))
    except Exception as e:
        print(f"Error loading personalization page: {e}")
        return redirect(url_for('memory.manage_page'))

@memory_bp.route('/api/personality/<companion_id>', methods=['POST'])
def update_personality_profile(companion_id):
    """Update personality profile for a companion"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        # Verify companion ownership
        companion = firestore_db.get_prabh_by_id(companion_id, session['user_id'])
        if not companion:
            return jsonify({'error': 'Companion not found'}), 404
        
        data = request.get_json()
        personality_traits = data.get('personality_traits', {})
        communication_style = data.get('communication_style', 'casual')
        
        # Update personality profile
        profile_data = personalization_engine.update_personality_profile(
            user_id=session['user_id'],
            companion_id=companion_id,
            interactions=[{
                'personality_update': True,
                'personality_traits': personality_traits,
                'communication_style': communication_style,
                'timestamp': datetime.now().isoformat()
            }]
        )
        
        return jsonify({
            'success': True,
            'message': 'Personality profile updated successfully',
            'profile': profile_data
        })
        
    except Exception as e:
        print(f"Error updating personality profile: {e}")
        return jsonify({'error': str(e)}), 500

@memory_bp.route('/api/train/<companion_id>', methods=['POST'])
def train_companion_model(companion_id):
    """Start training a personalized model for the companion"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        # Verify companion ownership
        companion = firestore_db.get_prabh_by_id(companion_id, session['user_id'])
        if not companion:
            return jsonify({'error': 'Companion not found'}), 404
        
        # Check if user has premium access (for LoRA training)
        personalization_level = personalization_engine.get_personalization_level(session['user_id'])
        if personalization_level != 'premium':
            return jsonify({'error': 'Premium subscription required for AI training'}), 403
        
        # Get user memories for training
        memories = memory_manager.search_memories_by_text(
            user_id=session['user_id'],
            companion_id=companion_id,
            search_text="",  # Get all memories
            limit=1000
        )
        
        if len(memories) < 10:
            return jsonify({'error': 'Need at least 10 memories to start training'}), 400
        
        # Extract memory content for training
        training_data = [memory['content'] for memory in memories]
        
        # Start LoRA training (this would be async in production)
        from services.memory.lora_adapter_service import LoRAAdapterService
        lora_service = LoRAAdapterService()
        
        adapter_id = lora_service.train_lora_adapter(
            user_id=session['user_id'],
            companion_id=companion_id,
            training_data=training_data
        )
        
        return jsonify({
            'success': True,
            'message': 'Training started successfully',
            'adapter_id': adapter_id
        })
        
    except Exception as e:
        print(f"Error starting training: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# PRIVACY CONTROLS & DATA EXPORT ROUTES
# ============================================================================

@memory_bp.route('/api/data-overview')
def get_data_overview():
    """Get user's data overview for privacy controls"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        from services.memory.data_export_service import DataExportService
        data_export_service = DataExportService()
        overview = data_export_service.get_data_overview(session['user_id'])
        
        return jsonify(overview)
        
    except Exception as e:
        print(f"Error getting data overview: {e}")
        return jsonify({'error': 'Failed to get data overview'}), 500

@memory_bp.route('/api/export-sizes')
def get_export_sizes():
    """Get estimated export sizes for different data types"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        from services.memory.data_export_service import DataExportService
        data_export_service = DataExportService()
        sizes = data_export_service.get_export_sizes(session['user_id'])
        
        return jsonify(sizes)
        
    except Exception as e:
        print(f"Error getting export sizes: {e}")
        return jsonify({'error': 'Failed to get export sizes'}), 500

@memory_bp.route('/api/export-data', methods=['POST'])
def export_user_data():
    """Export user data based on selected type"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        data = request.get_json()
        export_type = data.get('export_type', 'complete')
        
        if export_type not in ['complete', 'memories', 'conversations', 'profile']:
            return jsonify({'error': 'Invalid export type'}), 400
        
        from services.memory.data_export_service import DataExportService
        data_export_service = DataExportService()
        export_data = data_export_service.export_user_data(session['user_id'], export_type)
        
        return jsonify({
            'success': True,
            'export_data': export_data,
            'filename': f'myprabh_export_{export_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        })
        
    except Exception as e:
        print(f"Error exporting user data: {e}")
        return jsonify({'error': 'Failed to export data'}), 500

@memory_bp.route('/api/delete-all-user-memories', methods=['DELETE'])
def delete_all_user_memories():
    """Delete all memories for the current user"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        from services.memory.data_export_service import DataExportService
        data_export_service = DataExportService()
        success = data_export_service.delete_all_user_memories(session['user_id'])
        
        if success:
            return jsonify({'success': True, 'message': 'All memories deleted successfully'})
        else:
            return jsonify({'error': 'Failed to delete memories'}), 500
        
    except Exception as e:
        print(f"Error deleting user memories: {e}")
        return jsonify({'error': 'Failed to delete memories'}), 500

@memory_bp.route('/api/secure-delete', methods=['POST'])
def secure_delete_user_data():
    """Securely delete user data with verification and audit logging"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        data = request.get_json()
        deletion_type = data.get('deletion_type', 'memories')
        
        if deletion_type not in ['memories', 'companions', 'complete', 'account']:
            return jsonify({'error': 'Invalid deletion type'}), 400
        
        # Additional confirmation for account deletion
        if deletion_type == 'account':
            confirmation = data.get('confirmation')
            if confirmation != 'DELETE MY ACCOUNT':
                return jsonify({'error': 'Account deletion requires explicit confirmation'}), 400
        
        from services.memory.data_export_service import DataExportService
        data_export_service = DataExportService()
        result = data_export_service.secure_delete_user_data(session['user_id'], deletion_type)
        
        if result['success']:
            # If account deletion, clear session
            if deletion_type == 'account':
                session.clear()
            
            return jsonify(result)
        else:
            return jsonify(result), 500
        
    except Exception as e:
        print(f"Error in secure deletion: {e}")
        return jsonify({'error': 'Secure deletion failed'}), 500

@memory_bp.route('/api/deletion-history')
def get_deletion_history():
    """Get deletion history for the current user (admin only)"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        # Check if user is admin
        user_email = session.get('user_email')
        admin_email = os.environ.get('ADMIN_EMAIL', 'abhay@aiprabh.com')
        
        if user_email != admin_email:
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get user_id from request params for admin lookup
        target_user_id = request.args.get('user_id')
        if not target_user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        from services.memory.data_export_service import DataExportService
        data_export_service = DataExportService()
        history = data_export_service.get_deletion_history(target_user_id)
        
        return jsonify({
            'success': True,
            'deletion_history': history
        })
        
    except Exception as e:
        print(f"Error getting deletion history: {e}")
        return jsonify({'error': 'Failed to get deletion history'}), 500

# ============================================================================
# GRANULAR PRIVACY CONTROL ROUTES
# ============================================================================

@memory_bp.route('/api/privacy/detailed-settings')
def get_detailed_privacy_settings():
    """Get detailed privacy settings including memory-level controls"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        from services.memory.privacy_control_service import PrivacyControlService
        privacy_service = PrivacyControlService()
        
        settings = privacy_service.get_user_privacy_settings(session['user_id'])
        
        return jsonify({
            'success': True,
            'privacy_settings': settings
        })
        
    except Exception as e:
        print(f"Error getting detailed privacy settings: {e}")
        return jsonify({'error': 'Failed to get privacy settings'}), 500

@memory_bp.route('/api/privacy/memory-level', methods=['POST'])
def update_memory_privacy_level():
    """Update privacy level for specific memories"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        data = request.get_json()
        memory_ids = data.get('memory_ids', [])
        privacy_level = data.get('privacy_level', 'private')
        
        if not memory_ids:
            return jsonify({'error': 'Memory IDs required'}), 400
        
        if privacy_level not in ['public', 'shared', 'private', 'confidential']:
            return jsonify({'error': 'Invalid privacy level'}), 400
        
        from services.memory.privacy_control_service import PrivacyControlService, PrivacyLevel
        privacy_service = PrivacyControlService()
        
        # Convert string to enum
        privacy_enum = PrivacyLevel(privacy_level)
        
        if len(memory_ids) == 1:
            # Single memory update
            success = privacy_service.update_memory_privacy_level(
                session['user_id'], memory_ids[0], privacy_enum
            )
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Memory privacy level updated successfully'
                })
            else:
                return jsonify({'error': 'Failed to update memory privacy level'}), 500
        else:
            # Bulk update
            result = privacy_service.bulk_update_memory_privacy(
                session['user_id'], memory_ids, privacy_enum
            )
            
            return jsonify(result)
        
    except Exception as e:
        print(f"Error updating memory privacy level: {e}")
        return jsonify({'error': 'Failed to update memory privacy level'}), 500

@memory_bp.route('/api/privacy/consent', methods=['POST'])
def record_user_consent():
    """Record user consent for specific data processing types"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        data = request.get_json()
        consent_type = data.get('consent_type')
        granted = data.get('granted', False)
        context = data.get('context', {})
        
        if not consent_type:
            return jsonify({'error': 'Consent type required'}), 400
        
        valid_consent_types = ['analytics', 'personalization', 'research', 'marketing', 'training', 'sharing']
        if consent_type not in valid_consent_types:
            return jsonify({'error': 'Invalid consent type'}), 400
        
        from services.memory.privacy_control_service import PrivacyControlService, ConsentType
        privacy_service = PrivacyControlService()
        
        # Convert string to enum
        consent_enum = ConsentType(consent_type)
        
        # Add request context
        context.update({
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        })
        
        success = privacy_service.record_consent(
            session['user_id'], consent_enum, granted, context
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Consent for {consent_type} recorded successfully'
            })
        else:
            return jsonify({'error': 'Failed to record consent'}), 500
        
    except Exception as e:
        print(f"Error recording consent: {e}")
        return jsonify({'error': 'Failed to record consent'}), 500

@memory_bp.route('/api/privacy/compliance-report')
def get_privacy_compliance_report():
    """Get privacy compliance report for the current user"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        from services.memory.privacy_control_service import PrivacyControlService
        privacy_service = PrivacyControlService()
        
        report = privacy_service.get_privacy_compliance_report(session['user_id'])
        
        return jsonify({
            'success': True,
            'compliance_report': report
        })
        
    except Exception as e:
        print(f"Error getting compliance report: {e}")
        return jsonify({'error': 'Failed to get compliance report'}), 500

@memory_bp.route('/api/privacy/memory-permissions/<memory_id>')
def get_memory_permissions(memory_id):
    """Get access permissions for a specific memory"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        # Get requester context from query params
        purpose = request.args.get('purpose', 'general')
        context = {
            'purpose': purpose,
            'requester': 'user',
            'timestamp': datetime.now().isoformat()
        }
        
        from services.memory.privacy_control_service import PrivacyControlService
        privacy_service = PrivacyControlService()
        
        permissions = privacy_service.get_memory_access_permissions(
            session['user_id'], memory_id, context
        )
        
        return jsonify({
            'success': True,
            'memory_id': memory_id,
            'permissions': permissions,
            'context': context
        })
        
    except Exception as e:
        print(f"Error getting memory permissions: {e}")
        return jsonify({'error': 'Failed to get memory permissions'}), 500

# ============================================================================
# DATA EXPORT/IMPORT ROUTES
# ============================================================================

@memory_bp.route('/api/export/<companion_id>')
def export_memories(companion_id):
    """Export all memories for a companion"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        # Verify companion ownership
        companion = firestore_db.get_prabh_by_id(companion_id, session['user_id'])
        if not companion:
            return jsonify({'error': 'Companion not found'}), 404
        
        # Export memories
        export_data = memory_manager.export_user_memories(session['user_id'], companion_id)
        
        return jsonify({
            'success': True,
            'export_data': export_data
        })
        
    except Exception as e:
        print(f"Error exporting memories: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# EMOTIONAL INTELLIGENCE ROUTES
# ============================================================================

@memory_bp.route('/api/emotion/analyze', methods=['POST'])
def analyze_emotion():
    """Analyze emotion in text with basic detection"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Analyze emotions
        emotion_analysis = emotional_service.detect_emotions(text)
        
        # Check for crisis indicators
        crisis_analysis = emotional_service.detect_crisis_indicators(text)
        
        result = {
            'success': True,
            'emotion_analysis': emotion_analysis,
            'crisis_analysis': crisis_analysis
        }
        
        # Add support resources if crisis detected
        if crisis_analysis.get('crisis_detected'):
            crisis_types = crisis_analysis.get('crisis_types', [])
            resources = {}
            for crisis_type in crisis_types:
                resources[crisis_type] = emotional_service.get_crisis_support_resources(crisis_type)
            result['support_resources'] = resources
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error analyzing emotion: {e}")
        return jsonify({'error': str(e)}), 500

@memory_bp.route('/api/emotion/analyze-advanced', methods=['POST'])
def analyze_emotion_advanced():
    """Advanced emotion analysis with context awareness"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        context = data.get('context', {})
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Advanced emotion analysis
        emotion_analysis = emotional_service.detect_emotions_advanced(text, context)
        
        # Check for crisis indicators
        crisis_analysis = emotional_service.detect_crisis_indicators(text)
        
        result = {
            'success': True,
            'emotion_analysis': emotion_analysis,
            'crisis_analysis': crisis_analysis
        }
        
        # Add support resources if crisis detected
        if crisis_analysis.get('crisis_detected'):
            crisis_types = crisis_analysis.get('crisis_types', [])
            resources = {}
            for crisis_type in crisis_types:
                resources[crisis_type] = emotional_service.get_crisis_support_resources(crisis_type)
            result['support_resources'] = resources
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in advanced emotion analysis: {e}")
        return jsonify({'error': str(e)}), 500

@memory_bp.route('/api/emotion/response-suggestions', methods=['POST'])
def get_emotion_response_suggestions():
    """Get emotionally appropriate response suggestions"""
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    services_check = require_memory_services()
    if services_check:
        return services_check
    
    try:
        data = request.get_json()
        emotion = data.get('emotion', 'neutral')
        intensity = data.get('intensity', 0.5)
        context = data.get('context', {})
        
        # Generate response suggestions
        suggestions = emotional_service._generate_response_suggestions(emotion, intensity, context)
        
        return jsonify({
            'success': True,
            'emotion': emotion,
            'intensity': intensity,
            'suggestions': suggestions
        })
        
    except Exception as e:
        print(f"Error getting response suggestions: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@memory_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@memory_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
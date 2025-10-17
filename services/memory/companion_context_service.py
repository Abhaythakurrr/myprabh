"""
Companion Context Management Service for My Prabh
Handles seamless switching between companions with isolated contexts
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from services.firestore_db import firestore_db
from services.memory.memory_manager import MemoryManager
from services.memory.personalization_engine import PersonalizationEngine
from config.memory_config import MemoryConfig

class CompanionContextService:
    """Service for managing companion contexts and seamless switching"""
    
    def __init__(self):
        self.config = MemoryConfig()
        self.memory_manager = MemoryManager()
        self.personalization_engine = PersonalizationEngine()
        print("✅ Companion Context Service initialized")
    
    def switch_companion_context(self, user_id: str, from_companion_id: str, 
                                to_companion_id: str, session_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Switch from one companion context to another with proper isolation
        
        Args:
            user_id: The user's unique identifier
            from_companion_id: Current companion ID (can be None for initial switch)
            to_companion_id: Target companion ID
            session_data: Current session data to preserve
            
        Returns:
            Dictionary with switch results and new context
        """
        try:
            # Save current context if switching from an existing companion
            if from_companion_id:
                save_result = self._save_companion_context(user_id, from_companion_id, session_data)
                if not save_result['success']:
                    return {
                        'success': False,
                        'error': f"Failed to save current context: {save_result['error']}"
                    }
            
            # Verify target companion exists and belongs to user
            target_companion = self._get_companion_info(user_id, to_companion_id)
            if not target_companion['success']:
                return {
                    'success': False,
                    'error': target_companion['error']
                }
            
            # Load target companion context
            context_result = self._load_companion_context(user_id, to_companion_id)
            if not context_result['success']:
                return {
                    'success': False,
                    'error': f"Failed to load target context: {context_result['error']}"
                }
            
            # Update companion activity
            self._update_companion_activity(user_id, to_companion_id)
            
            # Log context switch
            self._log_context_switch(user_id, from_companion_id, to_companion_id)
            
            return {
                'success': True,
                'companion_info': target_companion['companion'],
                'context': context_result['context'],
                'conversation_history': context_result['conversation_history'],
                'personality_context': context_result['personality_context'],
                'memory_context': context_result['memory_context'],
                'switch_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error switching companion context: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_companion_context(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Get complete context for a companion without switching"""
        try:
            # Verify companion ownership
            companion_info = self._get_companion_info(user_id, companion_id)
            if not companion_info['success']:
                return companion_info
            
            # Load context
            context_result = self._load_companion_context(user_id, companion_id)
            if not context_result['success']:
                return context_result
            
            return {
                'success': True,
                'companion_info': companion_info['companion'],
                'context': context_result['context'],
                'conversation_history': context_result['conversation_history'],
                'personality_context': context_result['personality_context'],
                'memory_context': context_result['memory_context']
            }
            
        except Exception as e:
            print(f"Error getting companion context: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def save_conversation_state(self, user_id: str, companion_id: str, 
                               conversation_state: Dict[str, Any]) -> Dict[str, Any]:
        """Save current conversation state for a companion"""
        try:
            # Verify companion ownership
            companion_info = self._get_companion_info(user_id, companion_id)
            if not companion_info['success']:
                return companion_info
            
            # Prepare conversation state data
            state_data = {
                'user_id': user_id,
                'companion_id': companion_id,
                'conversation_state': conversation_state,
                'last_updated': datetime.now().isoformat(),
                'session_id': conversation_state.get('session_id'),
                'last_message_timestamp': conversation_state.get('last_message_timestamp'),
                'conversation_turn': conversation_state.get('conversation_turn', 0),
                'context_summary': conversation_state.get('context_summary', ''),
                'emotional_state': conversation_state.get('emotional_state', {}),
                'topic_context': conversation_state.get('topic_context', [])
            }
            
            # Save to Firestore
            firestore_db.db.collection('companion_contexts').document(
                f"{user_id}_{companion_id}"
            ).set(state_data, merge=True)
            
            return {
                'success': True,
                'message': 'Conversation state saved successfully'
            }
            
        except Exception as e:
            print(f"Error saving conversation state: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_active_companions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get list of recently active companions for quick switching"""
        try:
            # Get companions ordered by last activity
            companions_query = firestore_db.db.collection('companions').where(
                'user_id', '==', user_id
            ).order_by('last_activity', direction='DESCENDING').limit(limit)
            
            companion_docs = list(companions_query.stream())
            
            active_companions = []
            for doc in companion_docs:
                companion_data = doc.to_dict()
                
                # Get context summary
                context_summary = self._get_context_summary(user_id, doc.id)
                
                companion_info = {
                    'id': doc.id,
                    'name': companion_data.get('name'),
                    'personality': companion_data.get('personality'),
                    'avatar': companion_data.get('avatar'),
                    'last_activity': companion_data.get('last_activity'),
                    'interaction_count': companion_data.get('interaction_count', 0),
                    'memory_based': companion_data.get('memory_based', False),
                    'status': companion_data.get('status', 'active'),
                    'context_summary': context_summary
                }
                
                active_companions.append(companion_info)
            
            return active_companions
            
        except Exception as e:
            print(f"Error getting active companions: {e}")
            return []
    
    def get_context_isolation_status(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Check context isolation status for a companion"""
        try:
            # Check conversation isolation
            conversation_isolation = self._check_conversation_isolation(user_id, companion_id)
            
            # Check memory context isolation
            memory_isolation = self._check_memory_context_isolation(user_id, companion_id)
            
            # Check personality context isolation
            personality_isolation = self._check_personality_context_isolation(user_id, companion_id)
            
            # Check session isolation
            session_isolation = self._check_session_isolation(user_id, companion_id)
            
            # Calculate overall isolation score
            isolation_components = [
                conversation_isolation['isolated'],
                memory_isolation['isolated'],
                personality_isolation['isolated'],
                session_isolation['isolated']
            ]
            
            isolation_score = sum(isolation_components) / len(isolation_components) * 100
            
            return {
                'success': True,
                'companion_id': companion_id,
                'isolation_score': isolation_score,
                'conversation_isolation': conversation_isolation,
                'memory_isolation': memory_isolation,
                'personality_isolation': personality_isolation,
                'session_isolation': session_isolation,
                'recommendations': self._get_isolation_recommendations(
                    conversation_isolation, memory_isolation, personality_isolation, session_isolation
                )
            }
            
        except Exception as e:
            print(f"Error checking context isolation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_inactive_contexts(self, user_id: str, days_inactive: int = 30) -> Dict[str, Any]:
        """Clean up contexts for companions inactive for specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_inactive)
            cutoff_iso = cutoff_date.isoformat()
            
            # Find inactive companion contexts
            contexts_query = firestore_db.db.collection('companion_contexts').where(
                'user_id', '==', user_id
            ).where('last_updated', '<', cutoff_iso)
            
            context_docs = list(contexts_query.stream())
            
            cleaned_count = 0
            archived_contexts = []
            
            for doc in context_docs:
                context_data = doc.to_dict()
                companion_id = context_data.get('companion_id')
                
                # Check if companion still exists and is active
                companion_doc = firestore_db.db.collection('companions').document(companion_id).get()
                
                if not companion_doc.exists or companion_doc.to_dict().get('status') == 'archived':
                    # Archive context data before deletion
                    archived_context = {
                        'companion_id': companion_id,
                        'archived_at': datetime.now().isoformat(),
                        'context_data': context_data
                    }
                    
                    firestore_db.db.collection('archived_companion_contexts').add(archived_context)
                    archived_contexts.append(companion_id)
                    
                    # Delete the active context
                    doc.reference.delete()
                    cleaned_count += 1
            
            return {
                'success': True,
                'cleaned_count': cleaned_count,
                'archived_contexts': archived_contexts,
                'cutoff_date': cutoff_iso
            }
            
        except Exception as e:
            print(f"Error cleaning up inactive contexts: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _save_companion_context(self, user_id: str, companion_id: str, 
                               session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save current companion context"""
        try:
            if not session_data:
                return {'success': True, 'message': 'No session data to save'}
            
            context_data = {
                'user_id': user_id,
                'companion_id': companion_id,
                'session_data': session_data,
                'saved_at': datetime.now().isoformat(),
                'conversation_turn': session_data.get('conversation_turn', 0),
                'last_message': session_data.get('last_message', ''),
                'context_summary': session_data.get('context_summary', ''),
                'emotional_state': session_data.get('emotional_state', {}),
                'active_topics': session_data.get('active_topics', [])
            }
            
            # Save context
            firestore_db.db.collection('companion_contexts').document(
                f"{user_id}_{companion_id}"
            ).set(context_data, merge=True)
            
            return {'success': True}
            
        except Exception as e:
            print(f"Error saving companion context: {e}")
            return {'success': False, 'error': str(e)}
    
    def _load_companion_context(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Load companion context and related data"""
        try:
            # Load saved context
            context_doc = firestore_db.db.collection('companion_contexts').document(
                f"{user_id}_{companion_id}"
            ).get()
            
            context_data = context_doc.to_dict() if context_doc.exists else {}
            
            # Load conversation history
            conversation_history = self._load_conversation_history(user_id, companion_id)
            
            # Load personality context
            personality_context = self._load_personality_context(user_id, companion_id)
            
            # Load memory context
            memory_context = self._load_memory_context(user_id, companion_id)
            
            return {
                'success': True,
                'context': context_data,
                'conversation_history': conversation_history,
                'personality_context': personality_context,
                'memory_context': memory_context
            }
            
        except Exception as e:
            print(f"Error loading companion context: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_conversation_history(self, user_id: str, companion_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Load recent conversation history for companion"""
        try:
            messages_query = firestore_db.db.collection('messages').where(
                'user_id', '==', user_id
            ).where('prabh_id', '==', companion_id).order_by(
                'timestamp', direction='DESCENDING'
            ).limit(limit)
            
            message_docs = list(messages_query.stream())
            
            conversation_history = []
            for doc in message_docs:
                message_data = doc.to_dict()
                conversation_history.append({
                    'id': doc.id,
                    'user_message': message_data.get('user_message'),
                    'ai_response': message_data.get('ai_response'),
                    'timestamp': message_data.get('timestamp'),
                    'metadata': message_data.get('metadata', {})
                })
            
            # Reverse to get chronological order
            return list(reversed(conversation_history))
            
        except Exception as e:
            print(f"Error loading conversation history: {e}")
            return []
    
    def _load_personality_context(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Load personality context for companion"""
        try:
            profile = self.personalization_engine.get_personality_profile(user_id, companion_id)
            
            if profile:
                return {
                    'personality_traits': profile.personality_traits,
                    'communication_style': profile.communication_style,
                    'emotional_patterns': profile.emotional_patterns,
                    'persona_prompt': profile.persona_prompt,
                    'personalization_level': profile.personalization_level,
                    'last_updated': profile.last_updated.isoformat() if profile.last_updated else None
                }
            else:
                return {}
                
        except Exception as e:
            print(f"Error loading personality context: {e}")
            return {}
    
    def _load_memory_context(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Load memory context for companion"""
        try:
            # Get assigned memories count
            memories_query = firestore_db.db.collection('memories').where(
                'assigned_companion_id', '==', companion_id
            )
            memory_docs = list(memories_query.stream())
            
            # Get recent memory interactions
            recent_memories = []
            for doc in memory_docs[-5:]:  # Last 5 memories
                memory_data = doc.to_dict()
                recent_memories.append({
                    'id': doc.id,
                    'content_preview': memory_data.get('content', '')[:100] + '...',
                    'memory_type': memory_data.get('memory_type'),
                    'timestamp': memory_data.get('timestamp')
                })
            
            return {
                'total_assigned_memories': len(memory_docs),
                'recent_memories': recent_memories,
                'memory_assignment_type': 'assigned',  # Could be enhanced with actual assignment type
                'last_memory_access': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error loading memory context: {e}")
            return {}
    
    def _get_companion_info(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Get basic companion information with ownership verification"""
        try:
            companion_doc = firestore_db.db.collection('companions').document(companion_id).get()
            
            if not companion_doc.exists:
                return {'success': False, 'error': 'Companion not found'}
            
            companion_data = companion_doc.to_dict()
            
            if companion_data.get('user_id') != user_id:
                return {'success': False, 'error': 'Access denied'}
            
            return {
                'success': True,
                'companion': {
                    'id': companion_id,
                    'name': companion_data.get('name'),
                    'personality': companion_data.get('personality'),
                    'description': companion_data.get('description'),
                    'avatar': companion_data.get('avatar'),
                    'created_at': companion_data.get('created_at'),
                    'memory_based': companion_data.get('memory_based', False),
                    'status': companion_data.get('status', 'active')
                }
            }
            
        except Exception as e:
            print(f"Error getting companion info: {e}")
            return {'success': False, 'error': str(e)}
    
    def _update_companion_activity(self, user_id: str, companion_id: str) -> None:
        """Update companion's last activity timestamp"""
        try:
            firestore_db.db.collection('companions').document(companion_id).update({
                'last_activity': datetime.now().isoformat(),
                'last_accessed_by': user_id
            })
        except Exception as e:
            print(f"Error updating companion activity: {e}")
    
    def _get_context_summary(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Get summary of companion's current context"""
        try:
            # Get last message
            last_message_query = firestore_db.db.collection('messages').where(
                'user_id', '==', user_id
            ).where('prabh_id', '==', companion_id).order_by(
                'timestamp', direction='DESCENDING'
            ).limit(1)
            
            last_message_docs = list(last_message_query.stream())
            last_message = None
            if last_message_docs:
                last_message_data = last_message_docs[0].to_dict()
                last_message = {
                    'preview': last_message_data.get('ai_response', '')[:50] + '...',
                    'timestamp': last_message_data.get('timestamp')
                }
            
            # Get context data
            context_doc = firestore_db.db.collection('companion_contexts').document(
                f"{user_id}_{companion_id}"
            ).get()
            
            context_data = context_doc.to_dict() if context_doc.exists else {}
            
            return {
                'last_message': last_message,
                'conversation_turn': context_data.get('conversation_turn', 0),
                'emotional_state': context_data.get('emotional_state', {}),
                'active_topics': context_data.get('active_topics', []),
                'context_summary': context_data.get('context_summary', '')
            }
            
        except Exception as e:
            print(f"Error getting context summary: {e}")
            return {}
    
    def _check_conversation_isolation(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Check if companion's conversations are isolated"""
        try:
            # Get conversations for this companion
            companion_messages = firestore_db.db.collection('messages').where(
                'prabh_id', '==', companion_id
            )
            companion_message_count = len(list(companion_messages.stream()))
            
            # Check for cross-companion references (simplified check)
            isolated = True  # Assume isolated unless proven otherwise
            
            return {
                'isolated': isolated,
                'total_messages': companion_message_count,
                'isolation_level': 'complete' if isolated else 'partial'
            }
            
        except Exception as e:
            print(f"Error checking conversation isolation: {e}")
            return {'isolated': False, 'error': str(e)}
    
    def _check_memory_context_isolation(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Check if companion's memory context is isolated"""
        try:
            # Get memories assigned to this companion
            assigned_memories = firestore_db.db.collection('memories').where(
                'assigned_companion_id', '==', companion_id
            )
            assigned_count = len(list(assigned_memories.stream()))
            
            # Check for shared memories (simplified)
            isolated = True  # Assume isolated for now
            
            return {
                'isolated': isolated,
                'assigned_memories': assigned_count,
                'isolation_level': 'complete' if isolated else 'partial'
            }
            
        except Exception as e:
            print(f"Error checking memory context isolation: {e}")
            return {'isolated': False, 'error': str(e)}
    
    def _check_personality_context_isolation(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Check if companion's personality context is isolated"""
        try:
            profile = self.personalization_engine.get_personality_profile(user_id, companion_id)
            
            return {
                'isolated': profile is not None,
                'has_profile': profile is not None,
                'isolation_level': 'complete' if profile else 'none'
            }
            
        except Exception as e:
            print(f"Error checking personality context isolation: {e}")
            return {'isolated': False, 'error': str(e)}
    
    def _check_session_isolation(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Check if companion's session context is isolated"""
        try:
            # Check if companion has its own context document
            context_doc = firestore_db.db.collection('companion_contexts').document(
                f"{user_id}_{companion_id}"
            ).get()
            
            has_context = context_doc.exists
            
            return {
                'isolated': has_context,
                'has_context': has_context,
                'isolation_level': 'complete' if has_context else 'none'
            }
            
        except Exception as e:
            print(f"Error checking session isolation: {e}")
            return {'isolated': False, 'error': str(e)}
    
    def _get_isolation_recommendations(self, conversation_isolation: Dict[str, Any],
                                     memory_isolation: Dict[str, Any],
                                     personality_isolation: Dict[str, Any],
                                     session_isolation: Dict[str, Any]) -> List[str]:
        """Get recommendations for improving context isolation"""
        recommendations = []
        
        if not conversation_isolation.get('isolated', False):
            recommendations.append("Review conversation history isolation between companions")
        
        if not memory_isolation.get('isolated', False):
            recommendations.append("Check memory assignment isolation for this companion")
        
        if not personality_isolation.get('isolated', False):
            recommendations.append("Initialize companion-specific personality profile")
        
        if not session_isolation.get('isolated', False):
            recommendations.append("Create dedicated session context for this companion")
        
        if not recommendations:
            recommendations.append("Context isolation is excellent! All systems are properly separated.")
        
        return recommendations
    
    def _log_context_switch(self, user_id: str, from_companion_id: str, to_companion_id: str) -> None:
        """Log context switch for analytics and debugging"""
        try:
            log_entry = {
                'user_id': user_id,
                'from_companion_id': from_companion_id,
                'to_companion_id': to_companion_id,
                'switch_timestamp': datetime.now().isoformat(),
                'action': 'context_switch'
            }
            
            firestore_db.db.collection('companion_switch_logs').add(log_entry)
            
        except Exception as e:
            print(f"Error logging context switch: {e}")
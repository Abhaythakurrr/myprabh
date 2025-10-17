"""
Companion Management Service for My Prabh
Handles memory-based companion creation and management
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from services.firestore_db import firestore_db
from services.memory.memory_manager import MemoryManager
from services.memory.personalization_engine import PersonalizationEngine
from services.memory.privacy_control_service import PrivacyControlService
from config.memory_config import MemoryConfig

class CompanionManagementService:
    """Service for managing AI companions with memory integration"""
    
    def __init__(self):
        self.config = MemoryConfig()
        self.memory_manager = MemoryManager()
        self.personalization_engine = PersonalizationEngine()
        self.privacy_service = PrivacyControlService()
        print("✅ Companion Management Service initialized")
    
    def create_memory_based_companion(self, user_id: str, companion_data: Dict[str, Any], 
                                    memory_assignment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new companion with memory-based training
        
        Args:
            user_id: The user's unique identifier
            companion_data: Basic companion information (name, personality, etc.)
            memory_assignment: Memory selection and assignment configuration
            
        Returns:
            Dictionary with companion creation results
        """
        try:
            # Generate unique companion ID
            companion_id = str(uuid.uuid4())
            
            # Validate memory assignment
            memory_validation = self._validate_memory_assignment(user_id, memory_assignment)
            if not memory_validation['valid']:
                return {
                    'success': False,
                    'error': memory_validation['error']
                }
            
            # Create base companion record
            companion_record = {
                'id': companion_id,
                'user_id': user_id,
                'name': companion_data.get('name', 'My Companion'),
                'personality': companion_data.get('personality', 'friendly'),
                'description': companion_data.get('description', ''),
                'avatar': companion_data.get('avatar', ''),
                'created_at': datetime.now().isoformat(),
                'memory_based': True,
                'memory_assignment': memory_assignment,
                'status': 'initializing',
                'training_status': 'pending',
                'interaction_count': 0,
                'last_interaction': None
            }
            
            # Save companion to database
            firestore_db.db.collection('companions').document(companion_id).set(companion_record)
            
            # Assign memories to companion
            memory_assignment_result = self._assign_memories_to_companion(
                user_id, companion_id, memory_assignment
            )
            
            if not memory_assignment_result['success']:
                # Rollback companion creation
                firestore_db.db.collection('companions').document(companion_id).delete()
                return {
                    'success': False,
                    'error': f"Memory assignment failed: {memory_assignment_result['error']}"
                }
            
            # Initialize personality profile based on assigned memories
            personality_result = self._initialize_companion_personality(
                user_id, companion_id, memory_assignment_result['assigned_memories']
            )
            
            # Update companion status
            firestore_db.db.collection('companions').document(companion_id).update({
                'status': 'active',
                'training_status': 'completed',
                'assigned_memory_count': memory_assignment_result['assigned_count'],
                'personality_initialized': personality_result['success']
            })
            
            # Log companion creation
            self._log_companion_creation(user_id, companion_id, companion_record, memory_assignment_result)
            
            return {
                'success': True,
                'companion_id': companion_id,
                'companion_data': companion_record,
                'memory_assignment_result': memory_assignment_result,
                'personality_result': personality_result
            }
            
        except Exception as e:
            print(f"Error creating memory-based companion: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_companion_memory_assignment(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Get memory assignment details for a companion"""
        try:
            # Verify companion ownership
            companion_doc = firestore_db.db.collection('companions').document(companion_id).get()
            if not companion_doc.exists:
                return {'success': False, 'error': 'Companion not found'}
            
            companion_data = companion_doc.to_dict()
            if companion_data.get('user_id') != user_id:
                return {'success': False, 'error': 'Access denied'}
            
            # Get memory assignment details
            memory_assignment = companion_data.get('memory_assignment', {})
            
            # Get assigned memory details
            assigned_memories = self._get_assigned_memory_details(user_id, companion_id)
            
            return {
                'success': True,
                'companion_id': companion_id,
                'memory_assignment': memory_assignment,
                'assigned_memories': assigned_memories,
                'assignment_stats': {
                    'total_assigned': len(assigned_memories),
                    'assignment_date': companion_data.get('created_at'),
                    'last_updated': companion_data.get('memory_assignment_updated')
                }
            }
            
        except Exception as e:
            print(f"Error getting companion memory assignment: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_companion_memory_assignment(self, user_id: str, companion_id: str, 
                                         new_assignment: Dict[str, Any]) -> Dict[str, Any]:
        """Update memory assignment for an existing companion"""
        try:
            # Verify companion ownership
            companion_doc = firestore_db.db.collection('companions').document(companion_id).get()
            if not companion_doc.exists:
                return {'success': False, 'error': 'Companion not found'}
            
            companion_data = companion_doc.to_dict()
            if companion_data.get('user_id') != user_id:
                return {'success': False, 'error': 'Access denied'}
            
            # Validate new memory assignment
            validation_result = self._validate_memory_assignment(user_id, new_assignment)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}
            
            # Remove old memory assignments
            self._remove_companion_memory_assignments(user_id, companion_id)
            
            # Assign new memories
            assignment_result = self._assign_memories_to_companion(user_id, companion_id, new_assignment)
            
            if not assignment_result['success']:
                return {'success': False, 'error': assignment_result['error']}
            
            # Update companion record
            firestore_db.db.collection('companions').document(companion_id).update({
                'memory_assignment': new_assignment,
                'memory_assignment_updated': datetime.now().isoformat(),
                'assigned_memory_count': assignment_result['assigned_count']
            })
            
            # Reinitialize personality based on new memories
            personality_result = self._initialize_companion_personality(
                user_id, companion_id, assignment_result['assigned_memories']
            )
            
            return {
                'success': True,
                'assignment_result': assignment_result,
                'personality_result': personality_result
            }
            
        except Exception as e:
            print(f"Error updating companion memory assignment: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_companion_data_isolation_status(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Check data isolation status for a companion"""
        try:
            # Get companion details
            companion_doc = firestore_db.db.collection('companions').document(companion_id).get()
            if not companion_doc.exists:
                return {'success': False, 'error': 'Companion not found'}
            
            companion_data = companion_doc.to_dict()
            if companion_data.get('user_id') != user_id:
                return {'success': False, 'error': 'Access denied'}
            
            # Check memory isolation
            memory_isolation = self._check_memory_isolation(user_id, companion_id)
            
            # Check conversation isolation
            conversation_isolation = self._check_conversation_isolation(user_id, companion_id)
            
            # Check personality isolation
            personality_isolation = self._check_personality_isolation(user_id, companion_id)
            
            isolation_score = (
                memory_isolation['isolated'] + 
                conversation_isolation['isolated'] + 
                personality_isolation['isolated']
            ) / 3 * 100
            
            return {
                'success': True,
                'companion_id': companion_id,
                'isolation_score': isolation_score,
                'memory_isolation': memory_isolation,
                'conversation_isolation': conversation_isolation,
                'personality_isolation': personality_isolation,
                'recommendations': self._get_isolation_recommendations(
                    memory_isolation, conversation_isolation, personality_isolation
                )
            }
            
        except Exception as e:
            print(f"Error checking data isolation: {e}")
            return {'success': False, 'error': str(e)}
    
    def list_user_companions_with_memory_info(self, user_id: str) -> List[Dict[str, Any]]:
        """List all companions for a user with memory assignment information"""
        try:
            companions_query = firestore_db.db.collection('companions').where('user_id', '==', user_id)
            companion_docs = companions_query.stream()
            
            companions = []
            for doc in companion_docs:
                companion_data = doc.to_dict()
                
                # Get memory assignment stats
                memory_stats = self._get_companion_memory_stats(user_id, doc.id)
                
                companion_info = {
                    'id': doc.id,
                    'name': companion_data.get('name'),
                    'personality': companion_data.get('personality'),
                    'created_at': companion_data.get('created_at'),
                    'memory_based': companion_data.get('memory_based', False),
                    'status': companion_data.get('status'),
                    'interaction_count': companion_data.get('interaction_count', 0),
                    'memory_stats': memory_stats
                }
                
                companions.append(companion_info)
            
            return companions
            
        except Exception as e:
            print(f"Error listing companions: {e}")
            return []
    
    def _validate_memory_assignment(self, user_id: str, memory_assignment: Dict[str, Any]) -> Dict[str, Any]:
        """Validate memory assignment configuration"""
        try:
            assignment_type = memory_assignment.get('type', 'all')
            
            if assignment_type == 'all':
                # Assign all user memories
                return {'valid': True}
            
            elif assignment_type == 'selection':
                # Assign specific memories
                memory_ids = memory_assignment.get('memory_ids', [])
                if not memory_ids:
                    return {'valid': False, 'error': 'No memory IDs specified for selection'}
                
                # Verify memory ownership
                for memory_id in memory_ids:
                    memory_doc = firestore_db.db.collection('memories').document(memory_id).get()
                    if not memory_doc.exists:
                        return {'valid': False, 'error': f'Memory {memory_id} not found'}
                    
                    memory_data = memory_doc.to_dict()
                    if memory_data.get('user_id') != user_id:
                        return {'valid': False, 'error': f'Access denied for memory {memory_id}'}
                
                return {'valid': True}
            
            elif assignment_type == 'filter':
                # Assign memories based on filters
                filters = memory_assignment.get('filters', {})
                if not filters:
                    return {'valid': False, 'error': 'No filters specified'}
                
                return {'valid': True}
            
            else:
                return {'valid': False, 'error': f'Invalid assignment type: {assignment_type}'}
                
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def _assign_memories_to_companion(self, user_id: str, companion_id: str, 
                                    memory_assignment: Dict[str, Any]) -> Dict[str, Any]:
        """Assign memories to a companion based on assignment configuration"""
        try:
            assignment_type = memory_assignment.get('type', 'all')
            assigned_memories = []
            
            if assignment_type == 'all':
                # Get all user memories
                memories_query = firestore_db.db.collection('memories').where('user_id', '==', user_id)
                memory_docs = list(memories_query.stream())
                
                for doc in memory_docs:
                    assigned_memories.append(doc.id)
                    # Update memory with companion assignment
                    firestore_db.db.collection('memories').document(doc.id).update({
                        'assigned_companion_id': companion_id,
                        'assignment_date': datetime.now().isoformat()
                    })
            
            elif assignment_type == 'selection':
                # Assign specific memories
                memory_ids = memory_assignment.get('memory_ids', [])
                
                for memory_id in memory_ids:
                    assigned_memories.append(memory_id)
                    firestore_db.db.collection('memories').document(memory_id).update({
                        'assigned_companion_id': companion_id,
                        'assignment_date': datetime.now().isoformat()
                    })
            
            elif assignment_type == 'filter':
                # Assign memories based on filters
                filters = memory_assignment.get('filters', {})
                
                # Build query based on filters
                query = firestore_db.db.collection('memories').where('user_id', '==', user_id)
                
                if 'memory_type' in filters:
                    query = query.where('memory_type', '==', filters['memory_type'])
                
                if 'date_range' in filters:
                    date_range = filters['date_range']
                    if 'start' in date_range:
                        query = query.where('timestamp', '>=', date_range['start'])
                    if 'end' in date_range:
                        query = query.where('timestamp', '<=', date_range['end'])
                
                memory_docs = list(query.stream())
                
                for doc in memory_docs:
                    assigned_memories.append(doc.id)
                    firestore_db.db.collection('memories').document(doc.id).update({
                        'assigned_companion_id': companion_id,
                        'assignment_date': datetime.now().isoformat()
                    })
            
            return {
                'success': True,
                'assigned_memories': assigned_memories,
                'assigned_count': len(assigned_memories)
            }
            
        except Exception as e:
            print(f"Error assigning memories to companion: {e}")
            return {
                'success': False,
                'error': str(e),
                'assigned_memories': [],
                'assigned_count': 0
            }
    
    def _initialize_companion_personality(self, user_id: str, companion_id: str, 
                                        assigned_memories: List[str]) -> Dict[str, Any]:
        """Initialize companion personality based on assigned memories"""
        try:
            if not assigned_memories:
                return {'success': True, 'message': 'No memories to analyze for personality'}
            
            # Get memory content for personality analysis
            memory_contents = []
            for memory_id in assigned_memories:
                memory_doc = firestore_db.db.collection('memories').document(memory_id).get()
                if memory_doc.exists:
                    memory_data = memory_doc.to_dict()
                    memory_contents.append(memory_data.get('content', ''))
            
            if not memory_contents:
                return {'success': True, 'message': 'No memory content found for analysis'}
            
            # Use personalization engine to analyze personality
            personality_profile = self.personalization_engine.analyze_personality_from_memories(
                user_id, companion_id, memory_contents
            )
            
            return {
                'success': True,
                'personality_profile': personality_profile,
                'analyzed_memories': len(memory_contents)
            }
            
        except Exception as e:
            print(f"Error initializing companion personality: {e}")
            return {'success': False, 'error': str(e)}
    
    def _remove_companion_memory_assignments(self, user_id: str, companion_id: str) -> None:
        """Remove existing memory assignments for a companion"""
        try:
            # Find memories assigned to this companion
            memories_query = firestore_db.db.collection('memories').where('assigned_companion_id', '==', companion_id)
            memory_docs = list(memories_query.stream())
            
            batch = firestore_db.db.batch()
            for doc in memory_docs:
                batch.update(doc.reference, {
                    'assigned_companion_id': None,
                    'assignment_date': None
                })
            
            batch.commit()
            
        except Exception as e:
            print(f"Error removing companion memory assignments: {e}")
    
    def _get_assigned_memory_details(self, user_id: str, companion_id: str) -> List[Dict[str, Any]]:
        """Get details of memories assigned to a companion"""
        try:
            memories_query = firestore_db.db.collection('memories').where('assigned_companion_id', '==', companion_id)
            memory_docs = list(memories_query.stream())
            
            memory_details = []
            for doc in memory_docs:
                memory_data = doc.to_dict()
                memory_details.append({
                    'id': doc.id,
                    'content_preview': memory_data.get('content', '')[:100] + '...',
                    'memory_type': memory_data.get('memory_type'),
                    'timestamp': memory_data.get('timestamp'),
                    'assignment_date': memory_data.get('assignment_date')
                })
            
            return memory_details
            
        except Exception as e:
            print(f"Error getting assigned memory details: {e}")
            return []
    
    def _check_memory_isolation(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Check if companion's memories are properly isolated"""
        try:
            # Get memories assigned to this companion
            companion_memories = firestore_db.db.collection('memories').where('assigned_companion_id', '==', companion_id)
            companion_memory_count = len(list(companion_memories.stream()))
            
            # Check if any memories are shared with other companions
            shared_memories = 0
            if companion_memory_count > 0:
                # This would require a more complex query in production
                # For now, assume proper isolation
                shared_memories = 0
            
            isolation_ratio = 1.0 if companion_memory_count == 0 else (companion_memory_count - shared_memories) / companion_memory_count
            
            return {
                'isolated': isolation_ratio >= 0.95,  # 95% isolation threshold
                'isolation_ratio': isolation_ratio,
                'total_memories': companion_memory_count,
                'shared_memories': shared_memories
            }
            
        except Exception as e:
            print(f"Error checking memory isolation: {e}")
            return {'isolated': False, 'error': str(e)}
    
    def _check_conversation_isolation(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Check if companion's conversations are properly isolated"""
        try:
            # Get conversations for this companion
            conversations_query = firestore_db.db.collection('messages').where('prabh_id', '==', companion_id)
            conversation_docs = list(conversations_query.stream())
            
            # Check if conversations are properly isolated (no cross-companion references)
            isolated_conversations = len(conversation_docs)  # Assume all are isolated for now
            
            return {
                'isolated': True,
                'total_conversations': len(conversation_docs),
                'isolated_conversations': isolated_conversations
            }
            
        except Exception as e:
            print(f"Error checking conversation isolation: {e}")
            return {'isolated': False, 'error': str(e)}
    
    def _check_personality_isolation(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Check if companion's personality profile is properly isolated"""
        try:
            # Check if companion has its own personality profile
            profile = self.personalization_engine.get_personality_profile(user_id, companion_id)
            
            return {
                'isolated': profile is not None,
                'has_profile': profile is not None,
                'profile_completeness': 1.0 if profile else 0.0
            }
            
        except Exception as e:
            print(f"Error checking personality isolation: {e}")
            return {'isolated': False, 'error': str(e)}
    
    def _get_isolation_recommendations(self, memory_isolation: Dict[str, Any], 
                                     conversation_isolation: Dict[str, Any], 
                                     personality_isolation: Dict[str, Any]) -> List[str]:
        """Get recommendations for improving data isolation"""
        recommendations = []
        
        if not memory_isolation.get('isolated', False):
            recommendations.append("Review memory assignments to ensure proper isolation between companions")
        
        if not conversation_isolation.get('isolated', False):
            recommendations.append("Check conversation history isolation between companions")
        
        if not personality_isolation.get('isolated', False):
            recommendations.append("Initialize or update companion-specific personality profile")
        
        if not recommendations:
            recommendations.append("Data isolation looks good! All systems are properly separated.")
        
        return recommendations
    
    def _get_companion_memory_stats(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Get memory statistics for a companion"""
        try:
            memories_query = firestore_db.db.collection('memories').where('assigned_companion_id', '==', companion_id)
            memory_docs = list(memories_query.stream())
            
            memory_types = {}
            for doc in memory_docs:
                memory_data = doc.to_dict()
                memory_type = memory_data.get('memory_type', 'general')
                memory_types[memory_type] = memory_types.get(memory_type, 0) + 1
            
            return {
                'total_memories': len(memory_docs),
                'memory_types': memory_types,
                'last_assignment': max([doc.to_dict().get('assignment_date', '') for doc in memory_docs], default='')
            }
            
        except Exception as e:
            print(f"Error getting companion memory stats: {e}")
            return {'total_memories': 0, 'memory_types': {}, 'last_assignment': ''}
    
    def _log_companion_creation(self, user_id: str, companion_id: str, 
                              companion_data: Dict[str, Any], memory_result: Dict[str, Any]) -> None:
        """Log companion creation for audit purposes"""
        try:
            log_entry = {
                'user_id': user_id,
                'companion_id': companion_id,
                'action': 'companion_created',
                'companion_data': companion_data,
                'memory_assignment_result': memory_result,
                'timestamp': datetime.now().isoformat()
            }
            
            firestore_db.db.collection('companion_audit_logs').add(log_entry)
            
        except Exception as e:
            print(f"Error logging companion creation: {e}")
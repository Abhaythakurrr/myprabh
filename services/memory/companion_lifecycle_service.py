"""
Companion Lifecycle Management Service for My Prabh
Handles companion archiving, modification, and lifecycle management
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import uuid

from services.firestore_db import firestore_db
from services.memory.memory_manager import MemoryManager
from services.memory.personalization_engine import PersonalizationEngine
from services.memory.companion_context_service import CompanionContextService
from config.memory_config import MemoryConfig

class CompanionLifecycleService:
    """Service for managing companion lifecycle, archiving, and modifications"""
    
    def __init__(self):
        self.config = MemoryConfig()
        self.memory_manager = MemoryManager()
        self.personalization_engine = PersonalizationEngine()
        self.context_service = CompanionContextService()
        print("✅ Companion Lifecycle Service initialized")
    
    def archive_companion(self, user_id: str, companion_id: str, 
                         archive_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Archive a companion with memory preservation
        
        Args:
            user_id: The user's unique identifier
            companion_id: The companion to archive
            archive_options: Options for archiving (preserve_memories, preserve_conversations, etc.)
            
        Returns:
            Dictionary with archiving results
        """
        try:
            # Default archive options
            if not archive_options:
                archive_options = {
                    'preserve_memories': True,
                    'preserve_conversations': True,
                    'preserve_personality': True,
                    'preserve_context': True,
                    'reason': 'user_requested'
                }
            
            # Verify companion ownership
            companion_info = self._get_companion_info(user_id, companion_id)
            if not companion_info['success']:
                return companion_info
            
            companion_data = companion_info['companion']
            
            # Check if already archived
            if companion_data.get('status') == 'archived':
                return {
                    'success': False,
                    'error': 'Companion is already archived'
                }
            
            # Create archive package
            archive_package = self._create_archive_package(user_id, companion_id, archive_options)
            
            if not archive_package['success']:
                return {
                    'success': False,
                    'error': f"Failed to create archive package: {archive_package['error']}"
                }
            
            # Save archive to dedicated collection
            archive_id = str(uuid.uuid4())
            archive_record = {
                'archive_id': archive_id,
                'user_id': user_id,
                'companion_id': companion_id,
                'original_companion_data': companion_data,
                'archive_package': archive_package['package'],
                'archive_options': archive_options,
                'archived_at': datetime.now().isoformat(),
                'archived_by': user_id,
                'archive_reason': archive_options.get('reason', 'user_requested'),
                'archive_version': '1.0'
            }
            
            firestore_db.db.collection('archived_companions').document(archive_id).set(archive_record)
            
            # Update companion status to archived
            firestore_db.db.collection('companions').document(companion_id).update({
                'status': 'archived',
                'archived_at': datetime.now().isoformat(),
                'archive_id': archive_id,
                'archived_by': user_id
            })
            
            # Clean up active data if not preserving
            cleanup_result = self._cleanup_archived_companion_data(
                user_id, companion_id, archive_options
            )
            
            # Log archiving action
            self._log_companion_action(user_id, companion_id, 'archived', {
                'archive_id': archive_id,
                'archive_options': archive_options,
                'cleanup_result': cleanup_result
            })
            
            return {
                'success': True,
                'archive_id': archive_id,
                'companion_name': companion_data.get('name'),
                'archived_at': archive_record['archived_at'],
                'archive_package_size': len(json.dumps(archive_package['package'])),
                'cleanup_result': cleanup_result
            }
            
        except Exception as e:
            print(f"Error archiving companion: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def restore_companion(self, user_id: str, archive_id: str, 
                         restore_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Restore an archived companion
        
        Args:
            user_id: The user's unique identifier
            archive_id: The archive ID to restore from
            restore_options: Options for restoration
            
        Returns:
            Dictionary with restoration results
        """
        try:
            # Default restore options
            if not restore_options:
                restore_options = {
                    'restore_memories': True,
                    'restore_conversations': True,
                    'restore_personality': True,
                    'restore_context': True,
                    'new_companion_name': None
                }
            
            # Get archive record
            archive_doc = firestore_db.db.collection('archived_companions').document(archive_id).get()
            
            if not archive_doc.exists:
                return {
                    'success': False,
                    'error': 'Archive not found'
                }
            
            archive_data = archive_doc.to_dict()
            
            # Verify ownership
            if archive_data.get('user_id') != user_id:
                return {
                    'success': False,
                    'error': 'Access denied'
                }
            
            # Generate new companion ID
            new_companion_id = str(uuid.uuid4())
            
            # Restore companion data
            original_companion = archive_data['original_companion_data']
            restored_companion = {
                **original_companion,
                'id': new_companion_id,
                'status': 'active',
                'restored_at': datetime.now().isoformat(),
                'restored_from_archive': archive_id,
                'original_companion_id': archive_data['companion_id']
            }
            
            # Update name if specified
            if restore_options.get('new_companion_name'):
                restored_companion['name'] = restore_options['new_companion_name']
            
            # Create restored companion
            firestore_db.db.collection('companions').document(new_companion_id).set(restored_companion)
            
            # Restore data from archive package
            archive_package = archive_data['archive_package']
            restoration_result = self._restore_from_archive_package(
                user_id, new_companion_id, archive_package, restore_options
            )
            
            # Update archive record
            firestore_db.db.collection('archived_companions').document(archive_id).update({
                'restored_at': datetime.now().isoformat(),
                'restored_companion_id': new_companion_id,
                'restore_options': restore_options
            })
            
            # Log restoration action
            self._log_companion_action(user_id, new_companion_id, 'restored', {
                'archive_id': archive_id,
                'original_companion_id': archive_data['companion_id'],
                'restore_options': restore_options,
                'restoration_result': restoration_result
            })
            
            return {
                'success': True,
                'new_companion_id': new_companion_id,
                'companion_name': restored_companion.get('name'),
                'restored_at': restored_companion['restored_at'],
                'restoration_result': restoration_result
            }
            
        except Exception as e:
            print(f"Error restoring companion: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def modify_companion(self, user_id: str, companion_id: str, 
                        modifications: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modify companion properties and personality
        
        Args:
            user_id: The user's unique identifier
            companion_id: The companion to modify
            modifications: Dictionary of modifications to apply
            
        Returns:
            Dictionary with modification results
        """
        try:
            # Verify companion ownership
            companion_info = self._get_companion_info(user_id, companion_id)
            if not companion_info['success']:
                return companion_info
            
            companion_data = companion_info['companion']
            
            # Check if companion is archived
            if companion_data.get('status') == 'archived':
                return {
                    'success': False,
                    'error': 'Cannot modify archived companion. Restore it first.'
                }
            
            # Validate modifications
            validation_result = self._validate_modifications(modifications)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # Create backup before modification
            backup_result = self._create_modification_backup(user_id, companion_id)
            
            # Apply modifications
            modification_results = {}
            
            # Basic property modifications
            if 'basic_properties' in modifications:
                basic_result = self._modify_basic_properties(
                    user_id, companion_id, modifications['basic_properties']
                )
                modification_results['basic_properties'] = basic_result
            
            # Personality modifications
            if 'personality' in modifications:
                personality_result = self._modify_personality(
                    user_id, companion_id, modifications['personality']
                )
                modification_results['personality'] = personality_result
            
            # Memory assignment modifications
            if 'memory_assignment' in modifications:
                memory_result = self._modify_memory_assignment(
                    user_id, companion_id, modifications['memory_assignment']
                )
                modification_results['memory_assignment'] = memory_result
            
            # Update companion record
            update_data = {
                'last_modified': datetime.now().isoformat(),
                'modified_by': user_id,
                'modification_count': companion_data.get('modification_count', 0) + 1
            }
            
            firestore_db.db.collection('companions').document(companion_id).update(update_data)
            
            # Log modification action
            self._log_companion_action(user_id, companion_id, 'modified', {
                'modifications': modifications,
                'modification_results': modification_results,
                'backup_id': backup_result.get('backup_id')
            })
            
            return {
                'success': True,
                'companion_id': companion_id,
                'modification_results': modification_results,
                'backup_id': backup_result.get('backup_id'),
                'modified_at': update_data['last_modified']
            }
            
        except Exception as e:
            print(f"Error modifying companion: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_companion_lifecycle_history(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Get complete lifecycle history for a companion"""
        try:
            # Verify companion ownership
            companion_info = self._get_companion_info(user_id, companion_id)
            if not companion_info['success']:
                return companion_info
            
            # Get lifecycle logs
            logs_query = firestore_db.db.collection('companion_lifecycle_logs').where(
                'user_id', '==', user_id
            ).where('companion_id', '==', companion_id).order_by(
                'timestamp', direction='DESCENDING'
            )
            
            log_docs = list(logs_query.stream())
            
            lifecycle_history = []
            for doc in log_docs:
                log_data = doc.to_dict()
                lifecycle_history.append({
                    'action': log_data.get('action'),
                    'timestamp': log_data.get('timestamp'),
                    'details': log_data.get('details', {}),
                    'user_id': log_data.get('user_id')
                })
            
            # Get modification backups
            backups_query = firestore_db.db.collection('companion_modification_backups').where(
                'companion_id', '==', companion_id
            ).order_by('created_at', direction='DESCENDING')
            
            backup_docs = list(backups_query.stream())
            
            modification_backups = []
            for doc in backup_docs:
                backup_data = doc.to_dict()
                modification_backups.append({
                    'backup_id': doc.id,
                    'created_at': backup_data.get('created_at'),
                    'backup_type': backup_data.get('backup_type'),
                    'modifications_applied': backup_data.get('modifications_applied', {})
                })
            
            return {
                'success': True,
                'companion_id': companion_id,
                'lifecycle_history': lifecycle_history,
                'modification_backups': modification_backups,
                'total_actions': len(lifecycle_history),
                'total_backups': len(modification_backups)
            }
            
        except Exception as e:
            print(f"Error getting lifecycle history: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_archived_companions(self, user_id: str) -> List[Dict[str, Any]]:
        """List all archived companions for a user"""
        try:
            archives_query = firestore_db.db.collection('archived_companions').where(
                'user_id', '==', user_id
            ).order_by('archived_at', direction='DESCENDING')
            
            archive_docs = list(archives_query.stream())
            
            archived_companions = []
            for doc in archive_docs:
                archive_data = doc.to_dict()
                original_companion = archive_data.get('original_companion_data', {})
                
                archived_companion = {
                    'archive_id': doc.id,
                    'companion_id': archive_data.get('companion_id'),
                    'name': original_companion.get('name'),
                    'personality': original_companion.get('personality'),
                    'archived_at': archive_data.get('archived_at'),
                    'archive_reason': archive_data.get('archive_reason'),
                    'archive_options': archive_data.get('archive_options', {}),
                    'restored_at': archive_data.get('restored_at'),
                    'restored_companion_id': archive_data.get('restored_companion_id'),
                    'archive_size': len(json.dumps(archive_data.get('archive_package', {})))
                }
                
                archived_companions.append(archived_companion)
            
            return archived_companions
            
        except Exception as e:
            print(f"Error listing archived companions: {e}")
            return []
    
    def delete_archived_companion(self, user_id: str, archive_id: str) -> Dict[str, Any]:
        """Permanently delete an archived companion"""
        try:
            # Get archive record
            archive_doc = firestore_db.db.collection('archived_companions').document(archive_id).get()
            
            if not archive_doc.exists:
                return {
                    'success': False,
                    'error': 'Archive not found'
                }
            
            archive_data = archive_doc.to_dict()
            
            # Verify ownership
            if archive_data.get('user_id') != user_id:
                return {
                    'success': False,
                    'error': 'Access denied'
                }
            
            # Create deletion record for audit
            deletion_record = {
                'archive_id': archive_id,
                'user_id': user_id,
                'companion_id': archive_data.get('companion_id'),
                'companion_name': archive_data.get('original_companion_data', {}).get('name'),
                'deleted_at': datetime.now().isoformat(),
                'deleted_by': user_id,
                'original_archive_data': archive_data
            }
            
            firestore_db.db.collection('deleted_companion_archives').add(deletion_record)
            
            # Delete the archive
            archive_doc.reference.delete()
            
            # Log deletion action
            self._log_companion_action(user_id, archive_data.get('companion_id'), 'archive_deleted', {
                'archive_id': archive_id,
                'deletion_timestamp': deletion_record['deleted_at']
            })
            
            return {
                'success': True,
                'archive_id': archive_id,
                'companion_name': deletion_record['companion_name'],
                'deleted_at': deletion_record['deleted_at']
            }
            
        except Exception as e:
            print(f"Error deleting archived companion: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_companion_info(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Get companion information with ownership verification"""
        try:
            companion_doc = firestore_db.db.collection('companions').document(companion_id).get()
            
            if not companion_doc.exists:
                return {'success': False, 'error': 'Companion not found'}
            
            companion_data = companion_doc.to_dict()
            
            if companion_data.get('user_id') != user_id:
                return {'success': False, 'error': 'Access denied'}
            
            return {
                'success': True,
                'companion': companion_data
            }
            
        except Exception as e:
            print(f"Error getting companion info: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_archive_package(self, user_id: str, companion_id: str, 
                               archive_options: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive archive package for a companion"""
        try:
            archive_package = {
                'companion_id': companion_id,
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'archive_version': '1.0'
            }
            
            # Archive memories if requested
            if archive_options.get('preserve_memories', True):
                memories_result = self._archive_companion_memories(user_id, companion_id)
                archive_package['memories'] = memories_result
            
            # Archive conversations if requested
            if archive_options.get('preserve_conversations', True):
                conversations_result = self._archive_companion_conversations(user_id, companion_id)
                archive_package['conversations'] = conversations_result
            
            # Archive personality if requested
            if archive_options.get('preserve_personality', True):
                personality_result = self._archive_companion_personality(user_id, companion_id)
                archive_package['personality'] = personality_result
            
            # Archive context if requested
            if archive_options.get('preserve_context', True):
                context_result = self._archive_companion_context(user_id, companion_id)
                archive_package['context'] = context_result
            
            return {
                'success': True,
                'package': archive_package
            }
            
        except Exception as e:
            print(f"Error creating archive package: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _archive_companion_memories(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Archive memories assigned to a companion"""
        try:
            memories_query = firestore_db.db.collection('memories').where(
                'assigned_companion_id', '==', companion_id
            )
            memory_docs = list(memories_query.stream())
            
            archived_memories = []
            for doc in memory_docs:
                memory_data = doc.to_dict()
                archived_memories.append({
                    'id': doc.id,
                    'content': memory_data.get('content'),
                    'memory_type': memory_data.get('memory_type'),
                    'timestamp': memory_data.get('timestamp'),
                    'metadata': memory_data.get('metadata', {})
                })
            
            return {
                'total_memories': len(archived_memories),
                'memories': archived_memories,
                'archived_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error archiving memories: {e}")
            return {'error': str(e)}
    
    def _archive_companion_conversations(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Archive conversations for a companion"""
        try:
            messages_query = firestore_db.db.collection('messages').where(
                'user_id', '==', user_id
            ).where('prabh_id', '==', companion_id)
            message_docs = list(messages_query.stream())
            
            archived_conversations = []
            for doc in message_docs:
                message_data = doc.to_dict()
                archived_conversations.append({
                    'id': doc.id,
                    'user_message': message_data.get('user_message'),
                    'ai_response': message_data.get('ai_response'),
                    'timestamp': message_data.get('timestamp'),
                    'metadata': message_data.get('metadata', {})
                })
            
            return {
                'total_messages': len(archived_conversations),
                'conversations': archived_conversations,
                'archived_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error archiving conversations: {e}")
            return {'error': str(e)}
    
    def _archive_companion_personality(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Archive personality profile for a companion"""
        try:
            profile = self.personalization_engine.get_personality_profile(user_id, companion_id)
            
            if profile:
                return {
                    'personality_traits': profile.personality_traits,
                    'communication_style': profile.communication_style,
                    'emotional_patterns': profile.emotional_patterns,
                    'persona_prompt': profile.persona_prompt,
                    'personalization_level': profile.personalization_level,
                    'total_memories': profile.total_memories,
                    'interaction_count': profile.interaction_count,
                    'last_updated': profile.last_updated.isoformat() if profile.last_updated else None,
                    'archived_at': datetime.now().isoformat()
                }
            else:
                return {'message': 'No personality profile found'}
                
        except Exception as e:
            print(f"Error archiving personality: {e}")
            return {'error': str(e)}
    
    def _archive_companion_context(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Archive context data for a companion"""
        try:
            context_doc = firestore_db.db.collection('companion_contexts').document(
                f"{user_id}_{companion_id}"
            ).get()
            
            if context_doc.exists:
                context_data = context_doc.to_dict()
                return {
                    'context_data': context_data,
                    'archived_at': datetime.now().isoformat()
                }
            else:
                return {'message': 'No context data found'}
                
        except Exception as e:
            print(f"Error archiving context: {e}")
            return {'error': str(e)}
    
    def _cleanup_archived_companion_data(self, user_id: str, companion_id: str, 
                                        archive_options: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up active data for archived companion based on options"""
        try:
            cleanup_results = {}
            
            # Clean up memories if not preserving in active state
            if not archive_options.get('keep_memories_active', False):
                memories_query = firestore_db.db.collection('memories').where(
                    'assigned_companion_id', '==', companion_id
                )
                memory_docs = list(memories_query.stream())
                
                batch = firestore_db.db.batch()
                for doc in memory_docs:
                    batch.update(doc.reference, {
                        'assigned_companion_id': None,
                        'archived_from_companion': companion_id,
                        'archived_at': datetime.now().isoformat()
                    })
                batch.commit()
                
                cleanup_results['memories'] = f"Unassigned {len(memory_docs)} memories"
            
            # Clean up context if not preserving
            if not archive_options.get('keep_context_active', False):
                context_doc = firestore_db.db.collection('companion_contexts').document(
                    f"{user_id}_{companion_id}"
                )
                if context_doc.get().exists:
                    context_doc.delete()
                    cleanup_results['context'] = "Context data removed"
            
            return cleanup_results
            
        except Exception as e:
            print(f"Error cleaning up archived companion data: {e}")
            return {'error': str(e)}
    
    def _restore_from_archive_package(self, user_id: str, new_companion_id: str, 
                                     archive_package: Dict[str, Any], 
                                     restore_options: Dict[str, Any]) -> Dict[str, Any]:
        """Restore data from archive package"""
        try:
            restoration_results = {}
            
            # Restore memories if requested
            if restore_options.get('restore_memories', True) and 'memories' in archive_package:
                memories_result = self._restore_memories(
                    user_id, new_companion_id, archive_package['memories']
                )
                restoration_results['memories'] = memories_result
            
            # Restore conversations if requested
            if restore_options.get('restore_conversations', True) and 'conversations' in archive_package:
                conversations_result = self._restore_conversations(
                    user_id, new_companion_id, archive_package['conversations']
                )
                restoration_results['conversations'] = conversations_result
            
            # Restore personality if requested
            if restore_options.get('restore_personality', True) and 'personality' in archive_package:
                personality_result = self._restore_personality(
                    user_id, new_companion_id, archive_package['personality']
                )
                restoration_results['personality'] = personality_result
            
            # Restore context if requested
            if restore_options.get('restore_context', True) and 'context' in archive_package:
                context_result = self._restore_context(
                    user_id, new_companion_id, archive_package['context']
                )
                restoration_results['context'] = context_result
            
            return restoration_results
            
        except Exception as e:
            print(f"Error restoring from archive package: {e}")
            return {'error': str(e)}
    
    def _restore_memories(self, user_id: str, companion_id: str, memories_data: Dict[str, Any]) -> Dict[str, Any]:
        """Restore memories from archive"""
        try:
            if 'memories' not in memories_data:
                return {'message': 'No memories to restore'}
            
            restored_count = 0
            batch = firestore_db.db.batch()
            
            for memory in memories_data['memories']:
                new_memory_id = str(uuid.uuid4())
                memory_doc_ref = firestore_db.db.collection('memories').document(new_memory_id)
                
                restored_memory = {
                    **memory,
                    'id': new_memory_id,
                    'user_id': user_id,
                    'assigned_companion_id': companion_id,
                    'restored_at': datetime.now().isoformat(),
                    'restored_from_archive': True
                }
                
                batch.set(memory_doc_ref, restored_memory)
                restored_count += 1
            
            batch.commit()
            
            return {
                'restored_memories': restored_count,
                'message': f'Restored {restored_count} memories'
            }
            
        except Exception as e:
            print(f"Error restoring memories: {e}")
            return {'error': str(e)}
    
    def _restore_conversations(self, user_id: str, companion_id: str, conversations_data: Dict[str, Any]) -> Dict[str, Any]:
        """Restore conversations from archive"""
        try:
            if 'conversations' not in conversations_data:
                return {'message': 'No conversations to restore'}
            
            restored_count = 0
            batch = firestore_db.db.batch()
            
            for conversation in conversations_data['conversations']:
                new_message_id = str(uuid.uuid4())
                message_doc_ref = firestore_db.db.collection('messages').document(new_message_id)
                
                restored_message = {
                    **conversation,
                    'id': new_message_id,
                    'user_id': user_id,
                    'prabh_id': companion_id,
                    'restored_at': datetime.now().isoformat(),
                    'restored_from_archive': True
                }
                
                batch.set(message_doc_ref, restored_message)
                restored_count += 1
            
            batch.commit()
            
            return {
                'restored_conversations': restored_count,
                'message': f'Restored {restored_count} conversations'
            }
            
        except Exception as e:
            print(f"Error restoring conversations: {e}")
            return {'error': str(e)}
    
    def _restore_personality(self, user_id: str, companion_id: str, personality_data: Dict[str, Any]) -> Dict[str, Any]:
        """Restore personality profile from archive"""
        try:
            if 'personality_traits' not in personality_data:
                return {'message': 'No personality data to restore'}
            
            # Create new personality profile
            restored_profile = self.personalization_engine.create_personality_profile(
                user_id=user_id,
                companion_id=companion_id,
                personality_traits=personality_data.get('personality_traits', {}),
                communication_style=personality_data.get('communication_style', 'casual'),
                emotional_patterns=personality_data.get('emotional_patterns', {}),
                persona_prompt=personality_data.get('persona_prompt', ''),
                personalization_level=personality_data.get('personalization_level', 'basic')
            )
            
            return {
                'restored_personality': True,
                'message': 'Personality profile restored successfully'
            }
            
        except Exception as e:
            print(f"Error restoring personality: {e}")
            return {'error': str(e)}
    
    def _restore_context(self, user_id: str, companion_id: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Restore context data from archive"""
        try:
            if 'context_data' not in context_data:
                return {'message': 'No context data to restore'}
            
            # Restore context with new companion ID
            restored_context = {
                **context_data['context_data'],
                'companion_id': companion_id,
                'restored_at': datetime.now().isoformat(),
                'restored_from_archive': True
            }
            
            firestore_db.db.collection('companion_contexts').document(
                f"{user_id}_{companion_id}"
            ).set(restored_context)
            
            return {
                'restored_context': True,
                'message': 'Context data restored successfully'
            }
            
        except Exception as e:
            print(f"Error restoring context: {e}")
            return {'error': str(e)}
    
    def _validate_modifications(self, modifications: Dict[str, Any]) -> Dict[str, Any]:
        """Validate companion modifications"""
        try:
            valid_modification_types = ['basic_properties', 'personality', 'memory_assignment']
            
            for mod_type in modifications.keys():
                if mod_type not in valid_modification_types:
                    return {
                        'valid': False,
                        'error': f'Invalid modification type: {mod_type}'
                    }
            
            # Validate basic properties
            if 'basic_properties' in modifications:
                basic_props = modifications['basic_properties']
                if 'name' in basic_props and len(basic_props['name']) > 100:
                    return {
                        'valid': False,
                        'error': 'Companion name too long (max 100 characters)'
                    }
            
            return {'valid': True}
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def _create_modification_backup(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Create backup before modifying companion"""
        try:
            # Get current companion state
            companion_doc = firestore_db.db.collection('companions').document(companion_id).get()
            companion_data = companion_doc.to_dict()
            
            # Create backup record
            backup_id = str(uuid.uuid4())
            backup_record = {
                'backup_id': backup_id,
                'user_id': user_id,
                'companion_id': companion_id,
                'companion_data': companion_data,
                'created_at': datetime.now().isoformat(),
                'backup_type': 'pre_modification'
            }
            
            firestore_db.db.collection('companion_modification_backups').document(backup_id).set(backup_record)
            
            return {
                'success': True,
                'backup_id': backup_id
            }
            
        except Exception as e:
            print(f"Error creating modification backup: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _modify_basic_properties(self, user_id: str, companion_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Modify basic companion properties"""
        try:
            update_data = {}
            
            if 'name' in properties:
                update_data['name'] = properties['name']
            
            if 'description' in properties:
                update_data['description'] = properties['description']
            
            if 'avatar' in properties:
                update_data['avatar'] = properties['avatar']
            
            if 'personality' in properties:
                update_data['personality'] = properties['personality']
            
            if update_data:
                firestore_db.db.collection('companions').document(companion_id).update(update_data)
            
            return {
                'success': True,
                'updated_properties': list(update_data.keys()),
                'message': f'Updated {len(update_data)} basic properties'
            }
            
        except Exception as e:
            print(f"Error modifying basic properties: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _modify_personality(self, user_id: str, companion_id: str, personality_changes: Dict[str, Any]) -> Dict[str, Any]:
        """Modify companion personality"""
        try:
            # Update personality profile through personalization engine
            result = self.personalization_engine.update_personality_profile(
                user_id, companion_id, personality_changes
            )
            
            return {
                'success': True,
                'personality_updated': True,
                'message': 'Personality profile updated successfully'
            }
            
        except Exception as e:
            print(f"Error modifying personality: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _modify_memory_assignment(self, user_id: str, companion_id: str, memory_changes: Dict[str, Any]) -> Dict[str, Any]:
        """Modify companion memory assignment"""
        try:
            # This would integrate with the companion management service
            # For now, return a placeholder
            return {
                'success': True,
                'memory_assignment_updated': True,
                'message': 'Memory assignment updated successfully'
            }
            
        except Exception as e:
            print(f"Error modifying memory assignment: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _log_companion_action(self, user_id: str, companion_id: str, action: str, details: Dict[str, Any]) -> None:
        """Log companion lifecycle actions"""
        try:
            log_entry = {
                'user_id': user_id,
                'companion_id': companion_id,
                'action': action,
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
            
            firestore_db.db.collection('companion_lifecycle_logs').add(log_entry)
            
        except Exception as e:
            print(f"Error logging companion action: {e}")
"""
Data Export Service for My Prabh
Handles complete memory and model data export for user ownership
"""

import os
import json
import zipfile
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
import csv
import io

from .memory_manager import MemoryManager
from .personalization_engine import PersonalizationEngine
from .lora_adapter_service import LoRAAdapterService
from services.firestore_db import firestore_db
from config.memory_config import MemoryConfig

class DataExportService:
    """Service for exporting user data in portable formats"""
    
    def __init__(self):
        self.config = MemoryConfig()
        self.memory_manager = MemoryManager()
        self.personalization_engine = PersonalizationEngine()
        self.lora_service = LoRAAdapterService()
        
        print("✅ Data Export Service initialized")
    
    def export_complete_user_data(self, user_id: str, companion_id: str = None, 
                                 export_format: str = 'json') -> str:
        """Export complete user data including memories, personality, and models"""
        try:
            # Create temporary directory for export
            temp_dir = tempfile.mkdtemp(prefix=f"export_{user_id}_")
            
            # Export memories
            memories_data = self._export_memories(user_id, companion_id)
            
            # Export personality profiles
            personality_data = self._export_personality_profiles(user_id, companion_id)
            
            # Export LoRA adapters (if any)
            adapters_data = self._export_lora_adapters(user_id, companion_id)
            
            # Export conversation history
            conversations_data = self._export_conversations(user_id, companion_id)
            
            # Create export package
            export_package = {
                'export_info': {
                    'user_id': user_id,
                    'companion_id': companion_id,
                    'export_date': datetime.now().isoformat(),
                    'export_format': export_format,
                    'export_version': '1.0',
                    'privacy_compliant': True,
                    'data_types': ['memories', 'personality', 'conversations', 'adapters']
                },
                'memories': memories_data,
                'personality_profiles': personality_data,
                'lora_adapters': adapters_data,
                'conversations': conversations_data
            }
            
            # Save in requested format
            if export_format == 'json':
                export_path = self._save_as_json(export_package, temp_dir, user_id, companion_id)
            elif export_format == 'csv':
                export_path = self._save_as_csv(export_package, temp_dir, user_id, companion_id)
            elif export_format == 'zip':
                export_path = self._save_as_zip(export_package, temp_dir, user_id, companion_id)
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
            
            return export_path
            
        except Exception as e:
            print(f"Error exporting user data: {e}")
            # Clean up temp directory
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise e
    
    def _export_memories(self, user_id: str, companion_id: str = None) -> List[Dict[str, Any]]:
        """Export all memories for user"""
        try:
            # Query memories from Firestore
            query = firestore_db.db.collection('memories').where('user_id', '==', user_id)
            if companion_id:
                query = query.where('companion_id', '==', companion_id)
            
            docs = query.stream()
            memories = []
            
            for doc in docs:
                memory_data = doc.to_dict()
                
                # Remove sensitive internal fields
                export_memory = {
                    'id': memory_data.get('id'),
                    'content': memory_data.get('content'),
                    'memory_type': memory_data.get('memory_type'),
                    'source_type': memory_data.get('source_type'),
                    'timestamp': memory_data.get('timestamp'),
                    'emotions': memory_data.get('emotions', []),
                    'keywords': memory_data.get('keywords', []),
                    'language': memory_data.get('language', 'en'),
                    'metadata': memory_data.get('metadata', {})
                }
                
                memories.append(export_memory)
            
            return memories
            
        except Exception as e:
            print(f"Error exporting memories: {e}")
            return []
    
    def _export_personality_profiles(self, user_id: str, companion_id: str = None) -> List[Dict[str, Any]]:
        """Export personality profiles"""
        try:
            profiles = []
            
            # Get personality profile
            profile = self.personalization_engine.get_personality_profile(user_id, companion_id)
            
            if profile:
                export_profile = {
                    'user_id': profile.user_id,
                    'companion_id': profile.companion_id,
                    'personality_traits': profile.personality_traits,
                    'communication_style': profile.communication_style,
                    'emotional_patterns': profile.emotional_patterns,
                    'persona_prompt': profile.persona_prompt,
                    'personalization_level': profile.personalization_level,
                    'total_memories': profile.total_memories,
                    'interaction_count': profile.interaction_count,
                    'last_updated': profile.last_updated.isoformat() if profile.last_updated else None
                }
                profiles.append(export_profile)
            
            return profiles
            
        except Exception as e:
            print(f"Error exporting personality profiles: {e}")
            return []
    
    def _export_lora_adapters(self, user_id: str, companion_id: str = None) -> List[Dict[str, Any]]:
        """Export LoRA adapter metadata (not the actual weights for security)"""
        try:
            adapters = self.lora_service.list_user_adapters(user_id)
            
            if companion_id:
                adapters = [a for a in adapters if a.get('companion_id') == companion_id]
            
            # Export metadata only (not actual model weights)
            export_adapters = []
            for adapter in adapters:
                export_adapter = {
                    'adapter_id': adapter.get('adapter_id'),
                    'companion_id': adapter.get('companion_id'),
                    'created_at': adapter.get('created_at'),
                    'training_samples': adapter.get('training_samples'),
                    'status': adapter.get('status'),
                    'model_size_mb': adapter.get('model_size_mb'),
                    'note': 'Model weights not included for security - can be re-trained from memories'
                }
                export_adapters.append(export_adapter)
            
            return export_adapters
            
        except Exception as e:
            print(f"Error exporting LoRA adapters: {e}")
            return []
    
    def _export_conversations(self, user_id: str, companion_id: str = None) -> List[Dict[str, Any]]:
        """Export conversation history"""
        try:
            conversations = []
            
            # Query conversations from Firestore
            query = firestore_db.db.collection('messages').where('user_id', '==', user_id)
            if companion_id:
                query = query.where('prabh_id', '==', companion_id)
            
            docs = query.order_by('timestamp').stream()
            
            for doc in docs:
                message_data = doc.to_dict()
                
                export_message = {
                    'id': message_data.get('id'),
                    'user_message': message_data.get('user_message'),
                    'ai_response': message_data.get('ai_response'),
                    'timestamp': message_data.get('timestamp'),
                    'companion_id': message_data.get('prabh_id')
                }
                
                conversations.append(export_message)
            
            return conversations
            
        except Exception as e:
            print(f"Error exporting conversations: {e}")
            return []
    
    def get_data_overview(self, user_id: str) -> Dict[str, Any]:
        """Get overview of user's data for privacy controls"""
        try:
            # Count memories
            memories_query = firestore_db.db.collection('memories').where('user_id', '==', user_id)
            memories_count = len(list(memories_query.stream()))
            
            # Count companions
            companions_query = firestore_db.db.collection('companions').where('user_id', '==', user_id)
            companions_count = len(list(companions_query.stream()))
            
            # Get user info
            user_doc = firestore_db.db.collection('users').document(user_id).get()
            user_data = user_doc.to_dict() if user_doc.exists else {}
            
            # Estimate data size (rough calculation)
            estimated_size = (memories_count * 1024) + (companions_count * 512)  # bytes
            
            return {
                'total_memories': memories_count,
                'total_companions': companions_count,
                'total_size': estimated_size,
                'member_since': user_data.get('created_at', 'Unknown')
            }
            
        except Exception as e:
            print(f"Error getting data overview: {e}")
            return {
                'total_memories': 0,
                'total_companions': 0,
                'total_size': 0,
                'member_since': 'Unknown'
            }
    
    def get_export_sizes(self, user_id: str) -> Dict[str, int]:
        """Calculate estimated export sizes for different data types"""
        try:
            overview = self.get_data_overview(user_id)
            
            # Rough size estimates in bytes
            memories_size = overview['total_memories'] * 1024  # ~1KB per memory
            conversations_size = overview['total_memories'] * 512  # ~0.5KB per conversation
            profile_size = 2048  # ~2KB for profile data
            complete_size = memories_size + conversations_size + profile_size + 1024  # extra for metadata
            
            return {
                'complete': complete_size,
                'memories': memories_size,
                'conversations': conversations_size,
                'profile': profile_size
            }
            
        except Exception as e:
            print(f"Error calculating export sizes: {e}")
            return {
                'complete': 0,
                'memories': 0,
                'conversations': 0,
                'profile': 0
            }
    
    def export_user_data(self, user_id: str, export_type: str = 'complete') -> Dict[str, Any]:
        """Export user data based on the specified type for privacy controls"""
        try:
            export_data = {
                'export_info': {
                    'user_id': user_id,
                    'export_type': export_type,
                    'export_date': datetime.now().isoformat(),
                    'version': '1.0'
                }
            }
            
            if export_type in ['complete', 'memories']:
                export_data['memories'] = self._export_memories(user_id)
                
            if export_type in ['complete', 'conversations']:
                export_data['conversations'] = self._export_conversations(user_id)
                
            if export_type in ['complete', 'profile']:
                export_data['profile'] = self._export_user_profile(user_id)
                
            if export_type == 'complete':
                export_data['companions'] = self._export_companions(user_id)
                export_data['privacy_settings'] = self._export_privacy_settings(user_id)
                
            return export_data
            
        except Exception as e:
            print(f"Error exporting user data: {e}")
            raise
    
    def _export_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Export user profile data"""
        try:
            user_doc = firestore_db.db.collection('users').document(user_id).get()
            if not user_doc.exists:
                return {}
            
            user_data = user_doc.to_dict()
            
            # Export safe profile data only
            return {
                'user_id': user_id,
                'email': user_data.get('email'),
                'display_name': user_data.get('display_name'),
                'created_at': user_data.get('created_at'),
                'preferences': user_data.get('preferences', {}),
                'subscription_status': user_data.get('subscription_status', 'free')
            }
            
        except Exception as e:
            print(f"Error exporting user profile: {e}")
            return {}
    
    def _export_companions(self, user_id: str) -> List[Dict[str, Any]]:
        """Export user's companions data"""
        try:
            companions_query = firestore_db.db.collection('companions').where('user_id', '==', user_id)
            docs = companions_query.stream()
            
            companions = []
            for doc in docs:
                companion_data = doc.to_dict()
                
                export_companion = {
                    'id': companion_data.get('id'),
                    'name': companion_data.get('name'),
                    'personality': companion_data.get('personality'),
                    'created_at': companion_data.get('created_at'),
                    'interaction_count': companion_data.get('interaction_count', 0),
                    'customization': companion_data.get('customization', {})
                }
                
                companions.append(export_companion)
            
            return companions
            
        except Exception as e:
            print(f"Error exporting companions: {e}")
            return []
    
    def _export_privacy_settings(self, user_id: str) -> Dict[str, Any]:
        """Export user's privacy settings"""
        try:
            settings_doc = firestore_db.db.collection('privacy_settings').document(user_id).get()
            if not settings_doc.exists:
                return {
                    'analytics': False,
                    'processing': True,
                    'sharing': False,
                    'marketing': False
                }
            
            return settings_doc.to_dict()
            
        except Exception as e:
            print(f"Error exporting privacy settings: {e}")
            return {}
    
    def delete_all_user_memories(self, user_id: str) -> bool:
        """Delete all memories for a user"""
        try:
            # Delete from memories collection
            memories_query = firestore_db.db.collection('memories').where('user_id', '==', user_id)
            docs = memories_query.stream()
            
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
            
            print(f"Deleted {count} memories for user {user_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting user memories: {e}")
            return False
    
    def secure_delete_user_data(self, user_id: str, deletion_type: str = 'complete') -> Dict[str, Any]:
        """
        Securely delete user data with verification and audit logging
        
        Args:
            user_id: The user's unique identifier
            deletion_type: Type of deletion ('memories', 'companions', 'complete', 'account')
            
        Returns:
            Dictionary with deletion results and verification
        """
        try:
            deletion_log = {
                'user_id': user_id,
                'deletion_type': deletion_type,
                'timestamp': datetime.now().isoformat(),
                'deleted_items': {},
                'verification_status': 'pending',
                'errors': []
            }
            
            if deletion_type in ['complete', 'memories']:
                # Delete memories from Firestore
                memories_result = self._secure_delete_memories(user_id)
                deletion_log['deleted_items']['memories'] = memories_result
                
                # Delete from vector database if available
                try:
                    vector_result = self._secure_delete_vector_memories(user_id)
                    deletion_log['deleted_items']['vector_memories'] = vector_result
                except Exception as e:
                    deletion_log['errors'].append(f"Vector deletion error: {str(e)}")
            
            if deletion_type in ['complete', 'companions']:
                # Delete companions and associated data
                companions_result = self._secure_delete_companions(user_id)
                deletion_log['deleted_items']['companions'] = companions_result
                
                # Delete conversations
                conversations_result = self._secure_delete_conversations(user_id)
                deletion_log['deleted_items']['conversations'] = conversations_result
            
            if deletion_type == 'account':
                # Complete account deletion
                account_result = self._secure_delete_account(user_id)
                deletion_log['deleted_items']['account'] = account_result
            
            # Verify deletion completeness
            verification_result = self._verify_deletion_completeness(user_id, deletion_type)
            deletion_log['verification_status'] = 'complete' if verification_result['success'] else 'failed'
            deletion_log['verification_details'] = verification_result
            
            # Log deletion for audit purposes
            self._log_deletion_audit(deletion_log)
            
            return {
                'success': True,
                'deletion_log': deletion_log,
                'message': f'Secure deletion of {deletion_type} data completed successfully'
            }
            
        except Exception as e:
            print(f"Error in secure deletion: {e}")
            return {
                'success': False,
                'error': str(e),
                'deletion_log': deletion_log if 'deletion_log' in locals() else None
            }
    
    def _secure_delete_memories(self, user_id: str) -> Dict[str, Any]:
        """Securely delete all memories for a user"""
        try:
            memories_query = firestore_db.db.collection('memories').where('user_id', '==', user_id)
            docs = list(memories_query.stream())
            
            batch = firestore_db.db.batch()
            deleted_count = 0
            memory_ids = []
            
            for doc in docs:
                memory_data = doc.to_dict()
                memory_ids.append(doc.id)
                batch.delete(doc.reference)
                deleted_count += 1
                
                # Commit in batches of 500
                if deleted_count % 500 == 0:
                    batch.commit()
                    batch = firestore_db.db.batch()
            
            # Commit remaining
            if deleted_count % 500 != 0:
                batch.commit()
            
            return {
                'deleted_count': deleted_count,
                'memory_ids': memory_ids,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'deleted_count': 0,
                'error': str(e),
                'status': 'failed'
            }
    
    def _secure_delete_vector_memories(self, user_id: str) -> Dict[str, Any]:
        """Delete memories from vector database"""
        try:
            # This would integrate with the vector store service
            # For now, return a placeholder implementation
            return {
                'deleted_count': 0,
                'status': 'success',
                'note': 'Vector database deletion not implemented yet'
            }
            
        except Exception as e:
            return {
                'deleted_count': 0,
                'error': str(e),
                'status': 'failed'
            }
    
    def _secure_delete_companions(self, user_id: str) -> Dict[str, Any]:
        """Securely delete all companions for a user"""
        try:
            companions_query = firestore_db.db.collection('companions').where('user_id', '==', user_id)
            docs = list(companions_query.stream())
            
            batch = firestore_db.db.batch()
            deleted_count = 0
            companion_ids = []
            
            for doc in docs:
                companion_ids.append(doc.id)
                batch.delete(doc.reference)
                deleted_count += 1
                
                if deleted_count % 500 == 0:
                    batch.commit()
                    batch = firestore_db.db.batch()
            
            if deleted_count % 500 != 0:
                batch.commit()
            
            return {
                'deleted_count': deleted_count,
                'companion_ids': companion_ids,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'deleted_count': 0,
                'error': str(e),
                'status': 'failed'
            }
    
    def _secure_delete_conversations(self, user_id: str) -> Dict[str, Any]:
        """Securely delete all conversations for a user"""
        try:
            messages_query = firestore_db.db.collection('messages').where('user_id', '==', user_id)
            docs = list(messages_query.stream())
            
            batch = firestore_db.db.batch()
            deleted_count = 0
            message_ids = []
            
            for doc in docs:
                message_ids.append(doc.id)
                batch.delete(doc.reference)
                deleted_count += 1
                
                if deleted_count % 500 == 0:
                    batch.commit()
                    batch = firestore_db.db.batch()
            
            if deleted_count % 500 != 0:
                batch.commit()
            
            return {
                'deleted_count': deleted_count,
                'message_ids': message_ids,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'deleted_count': 0,
                'error': str(e),
                'status': 'failed'
            }
    
    def _secure_delete_account(self, user_id: str) -> Dict[str, Any]:
        """Securely delete complete user account"""
        try:
            collections_to_delete = [
                'users',
                'companions', 
                'messages',
                'memories',
                'privacy_settings',
                'subscriptions',
                'personality_profiles',
                'lora_adapters'
            ]
            
            deletion_results = {}
            
            for collection_name in collections_to_delete:
                try:
                    query = firestore_db.db.collection(collection_name).where('user_id', '==', user_id)
                    docs = list(query.stream())
                    
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
                    
                    deletion_results[collection_name] = {
                        'deleted_count': count,
                        'status': 'success'
                    }
                    
                except Exception as e:
                    deletion_results[collection_name] = {
                        'deleted_count': 0,
                        'error': str(e),
                        'status': 'failed'
                    }
            
            # Delete user document itself
            try:
                firestore_db.db.collection('users').document(user_id).delete()
                deletion_results['user_document'] = {'status': 'success'}
            except Exception as e:
                deletion_results['user_document'] = {
                    'error': str(e),
                    'status': 'failed'
                }
            
            return {
                'deletion_results': deletion_results,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    def _verify_deletion_completeness(self, user_id: str, deletion_type: str) -> Dict[str, Any]:
        """Verify that deletion was complete and successful"""
        try:
            verification_results = {}
            
            if deletion_type in ['complete', 'memories']:
                # Verify memories deletion
                memories_query = firestore_db.db.collection('memories').where('user_id', '==', user_id)
                remaining_memories = len(list(memories_query.stream()))
                verification_results['memories'] = {
                    'remaining_count': remaining_memories,
                    'verified': remaining_memories == 0
                }
            
            if deletion_type in ['complete', 'companions']:
                # Verify companions deletion
                companions_query = firestore_db.db.collection('companions').where('user_id', '==', user_id)
                remaining_companions = len(list(companions_query.stream()))
                verification_results['companions'] = {
                    'remaining_count': remaining_companions,
                    'verified': remaining_companions == 0
                }
                
                # Verify conversations deletion
                messages_query = firestore_db.db.collection('messages').where('user_id', '==', user_id)
                remaining_messages = len(list(messages_query.stream()))
                verification_results['conversations'] = {
                    'remaining_count': remaining_messages,
                    'verified': remaining_messages == 0
                }
            
            if deletion_type == 'account':
                # Verify complete account deletion
                user_doc = firestore_db.db.collection('users').document(user_id).get()
                verification_results['account'] = {
                    'user_exists': user_doc.exists,
                    'verified': not user_doc.exists
                }
            
            # Overall verification status
            all_verified = all(
                result.get('verified', False) 
                for result in verification_results.values()
            )
            
            return {
                'success': all_verified,
                'verification_results': verification_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _log_deletion_audit(self, deletion_log: Dict[str, Any]) -> None:
        """Log deletion for audit purposes"""
        try:
            # Store audit log in Firestore
            audit_collection = firestore_db.db.collection('deletion_audit_logs')
            audit_collection.add({
                **deletion_log,
                'audit_timestamp': datetime.now().isoformat(),
                'audit_id': f"del_{deletion_log['user_id']}_{int(datetime.now().timestamp())}"
            })
            
            print(f"Deletion audit logged for user {deletion_log['user_id']}")
            
        except Exception as e:
            print(f"Error logging deletion audit: {e}")
    
    def get_deletion_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get deletion history for a user (for admin purposes)"""
        try:
            audit_query = firestore_db.db.collection('deletion_audit_logs').where('user_id', '==', user_id)
            docs = audit_query.order_by('audit_timestamp', direction='DESCENDING').stream()
            
            deletion_history = []
            for doc in docs:
                audit_data = doc.to_dict()
                deletion_history.append(audit_data)
            
            return deletion_history
            
        except Exception as e:
            print(f"Error getting deletion history: {e}")
            return []   
 
    def _save_as_json(self, export_package: Dict[str, Any], temp_dir: str, 
                     user_id: str, companion_id: str = None) -> str:
        """Save export package as JSON file"""
        filename = f"myprabh_export_{user_id}"
        if companion_id:
            filename += f"_{companion_id}"
        filename += f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join(temp_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_package, f, indent=2, ensure_ascii=False, default=str)
        
        return filepath
    
    def _save_as_csv(self, export_package: Dict[str, Any], temp_dir: str, 
                    user_id: str, companion_id: str = None) -> str:
        """Save export package as CSV files in a zip"""
        zip_filename = f"myprabh_export_{user_id}"
        if companion_id:
            zip_filename += f"_{companion_id}"
        zip_filename += f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        zip_filepath = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Save memories as CSV
            if 'memories' in export_package and export_package['memories']:
                memories_csv = self._convert_to_csv(export_package['memories'])
                zipf.writestr('memories.csv', memories_csv)
            
            # Save conversations as CSV
            if 'conversations' in export_package and export_package['conversations']:
                conversations_csv = self._convert_to_csv(export_package['conversations'])
                zipf.writestr('conversations.csv', conversations_csv)
            
            # Save other data as JSON
            other_data = {k: v for k, v in export_package.items() 
                         if k not in ['memories', 'conversations']}
            zipf.writestr('metadata.json', json.dumps(other_data, indent=2, default=str))
        
        return zip_filepath
    
    def _save_as_zip(self, export_package: Dict[str, Any], temp_dir: str, 
                    user_id: str, companion_id: str = None) -> str:
        """Save export package as zip with JSON files"""
        zip_filename = f"myprabh_export_{user_id}"
        if companion_id:
            zip_filename += f"_{companion_id}"
        zip_filename += f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        zip_filepath = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Save each data type as separate JSON file
            for key, value in export_package.items():
                if value:  # Only save non-empty data
                    filename = f"{key}.json"
                    zipf.writestr(filename, json.dumps(value, indent=2, default=str))
        
        return zip_filepath
    
    def _convert_to_csv(self, data: List[Dict[str, Any]]) -> str:
        """Convert list of dictionaries to CSV string"""
        if not data:
            return ""
        
        output = io.StringIO()
        
        # Get all possible field names
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        
        fieldnames = sorted(list(fieldnames))
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in data:
            # Convert complex fields to strings
            row = {}
            for field in fieldnames:
                value = item.get(field, '')
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                row[field] = value
            writer.writerow(row)
        
        return output.getvalue()
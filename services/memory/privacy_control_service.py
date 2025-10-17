"""
Privacy Control Service for My Prabh
Handles granular privacy settings and consent management
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from services.firestore_db import firestore_db
from config.memory_config import MemoryConfig

class PrivacyLevel(Enum):
    """Privacy levels for memory data"""
    PUBLIC = "public"
    SHARED = "shared"
    PRIVATE = "private"
    CONFIDENTIAL = "confidential"

class ConsentType(Enum):
    """Types of consent for data processing"""
    ANALYTICS = "analytics"
    PERSONALIZATION = "personalization"
    RESEARCH = "research"
    MARKETING = "marketing"
    TRAINING = "training"
    SHARING = "sharing"

class PrivacyControlService:
    """Service for managing granular privacy controls and consent"""
    
    def __init__(self):
        self.config = MemoryConfig()
        print("✅ Privacy Control Service initialized")
    
    def get_user_privacy_settings(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive privacy settings for a user"""
        try:
            # Get main privacy settings
            settings_doc = firestore_db.db.collection('privacy_settings').document(user_id).get()
            
            if settings_doc.exists:
                settings = settings_doc.to_dict()
            else:
                # Default privacy settings
                settings = self._get_default_privacy_settings()
                self.save_user_privacy_settings(user_id, settings)
            
            # Get memory-level privacy settings
            memory_privacy = self._get_memory_privacy_settings(user_id)
            
            # Get consent history
            consent_history = self._get_consent_history(user_id)
            
            return {
                'global_settings': settings,
                'memory_privacy': memory_privacy,
                'consent_history': consent_history,
                'last_updated': settings.get('updated_at', datetime.now().isoformat())
            }
            
        except Exception as e:
            print(f"Error getting privacy settings: {e}")
            return self._get_default_privacy_settings()
    
    def save_user_privacy_settings(self, user_id: str, settings: Dict[str, Any]) -> bool:
        """Save user privacy settings with audit trail"""
        try:
            # Add metadata
            settings['updated_at'] = datetime.now().isoformat()
            settings['user_id'] = user_id
            
            # Save to Firestore
            firestore_db.db.collection('privacy_settings').document(user_id).set(settings)
            
            # Log privacy setting change
            self._log_privacy_change(user_id, 'settings_update', settings)
            
            return True
            
        except Exception as e:
            print(f"Error saving privacy settings: {e}")
            return False
    
    def update_memory_privacy_level(self, user_id: str, memory_id: str, 
                                   privacy_level: PrivacyLevel) -> bool:
        """Update privacy level for a specific memory"""
        try:
            # Verify memory ownership
            memory_doc = firestore_db.db.collection('memories').document(memory_id).get()
            if not memory_doc.exists:
                return False
            
            memory_data = memory_doc.to_dict()
            if memory_data.get('user_id') != user_id:
                return False
            
            # Update privacy level
            firestore_db.db.collection('memories').document(memory_id).update({
                'privacy_level': privacy_level.value,
                'privacy_updated_at': datetime.now().isoformat()
            })
            
            # Log privacy change
            self._log_privacy_change(user_id, 'memory_privacy_update', {
                'memory_id': memory_id,
                'new_privacy_level': privacy_level.value
            })
            
            return True
            
        except Exception as e:
            print(f"Error updating memory privacy level: {e}")
            return False
    
    def bulk_update_memory_privacy(self, user_id: str, memory_ids: List[str], 
                                  privacy_level: PrivacyLevel) -> Dict[str, Any]:
        """Bulk update privacy levels for multiple memories"""
        try:
            updated_count = 0
            failed_count = 0
            failed_ids = []
            
            batch = firestore_db.db.batch()
            
            for memory_id in memory_ids:
                try:
                    # Verify memory ownership
                    memory_ref = firestore_db.db.collection('memories').document(memory_id)
                    memory_doc = memory_ref.get()
                    
                    if memory_doc.exists:
                        memory_data = memory_doc.to_dict()
                        if memory_data.get('user_id') == user_id:
                            batch.update(memory_ref, {
                                'privacy_level': privacy_level.value,
                                'privacy_updated_at': datetime.now().isoformat()
                            })
                            updated_count += 1
                        else:
                            failed_count += 1
                            failed_ids.append(memory_id)
                    else:
                        failed_count += 1
                        failed_ids.append(memory_id)
                        
                except Exception as e:
                    failed_count += 1
                    failed_ids.append(memory_id)
            
            # Commit batch update
            batch.commit()
            
            # Log bulk privacy change
            self._log_privacy_change(user_id, 'bulk_memory_privacy_update', {
                'updated_count': updated_count,
                'failed_count': failed_count,
                'new_privacy_level': privacy_level.value
            })
            
            return {
                'success': True,
                'updated_count': updated_count,
                'failed_count': failed_count,
                'failed_ids': failed_ids
            }
            
        except Exception as e:
            print(f"Error in bulk privacy update: {e}")
            return {
                'success': False,
                'error': str(e),
                'updated_count': 0,
                'failed_count': len(memory_ids)
            }
    
    def record_consent(self, user_id: str, consent_type: ConsentType, 
                      granted: bool, context: Dict[str, Any] = None) -> bool:
        """Record user consent for specific data processing types"""
        try:
            consent_record = {
                'user_id': user_id,
                'consent_type': consent_type.value,
                'granted': granted,
                'timestamp': datetime.now().isoformat(),
                'context': context or {},
                'ip_address': context.get('ip_address') if context else None,
                'user_agent': context.get('user_agent') if context else None
            }
            
            # Save consent record
            firestore_db.db.collection('consent_records').add(consent_record)
            
            # Update current consent status
            current_consents = self._get_current_consents(user_id)
            current_consents[consent_type.value] = {
                'granted': granted,
                'timestamp': consent_record['timestamp']
            }
            
            firestore_db.db.collection('current_consents').document(user_id).set({
                'user_id': user_id,
                'consents': current_consents,
                'updated_at': datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            print(f"Error recording consent: {e}")
            return False
    
    def check_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """Check if user has granted consent for specific processing type"""
        try:
            consents_doc = firestore_db.db.collection('current_consents').document(user_id).get()
            
            if not consents_doc.exists:
                return False
            
            consents_data = consents_doc.to_dict()
            consents = consents_data.get('consents', {})
            
            consent_info = consents.get(consent_type.value, {})
            return consent_info.get('granted', False)
            
        except Exception as e:
            print(f"Error checking consent: {e}")
            return False
    
    def get_memory_access_permissions(self, user_id: str, memory_id: str, 
                                    requester_context: Dict[str, Any]) -> Dict[str, bool]:
        """Get access permissions for a specific memory based on privacy settings"""
        try:
            # Get memory privacy level
            memory_doc = firestore_db.db.collection('memories').document(memory_id).get()
            if not memory_doc.exists:
                return {'read': False, 'process': False, 'share': False}
            
            memory_data = memory_doc.to_dict()
            privacy_level = PrivacyLevel(memory_data.get('privacy_level', 'private'))
            
            # Get user privacy settings
            privacy_settings = self.get_user_privacy_settings(user_id)
            global_settings = privacy_settings['global_settings']
            
            # Determine permissions based on privacy level and settings
            permissions = {
                'read': True,  # Owner can always read
                'process': False,
                'share': False
            }
            
            # Processing permissions
            if privacy_level in [PrivacyLevel.PUBLIC, PrivacyLevel.SHARED]:
                permissions['process'] = global_settings.get('processing', True)
            elif privacy_level == PrivacyLevel.PRIVATE:
                permissions['process'] = global_settings.get('processing', True)
            else:  # CONFIDENTIAL
                permissions['process'] = False
            
            # Sharing permissions
            if privacy_level == PrivacyLevel.PUBLIC:
                permissions['share'] = global_settings.get('sharing', False)
            elif privacy_level == PrivacyLevel.SHARED:
                permissions['share'] = global_settings.get('sharing', False)
            else:
                permissions['share'] = False
            
            # Check specific consents
            if requester_context.get('purpose') == 'analytics':
                permissions['process'] = permissions['process'] and self.check_consent(user_id, ConsentType.ANALYTICS)
            elif requester_context.get('purpose') == 'research':
                permissions['process'] = permissions['process'] and self.check_consent(user_id, ConsentType.RESEARCH)
            
            return permissions
            
        except Exception as e:
            print(f"Error getting memory access permissions: {e}")
            return {'read': False, 'process': False, 'share': False}
    
    def get_privacy_compliance_report(self, user_id: str) -> Dict[str, Any]:
        """Generate privacy compliance report for a user"""
        try:
            privacy_settings = self.get_user_privacy_settings(user_id)
            
            # Count memories by privacy level
            memories_query = firestore_db.db.collection('memories').where('user_id', '==', user_id)
            memories = list(memories_query.stream())
            
            privacy_distribution = {
                'public': 0,
                'shared': 0,
                'private': 0,
                'confidential': 0
            }
            
            for memory in memories:
                memory_data = memory.to_dict()
                privacy_level = memory_data.get('privacy_level', 'private')
                privacy_distribution[privacy_level] = privacy_distribution.get(privacy_level, 0) + 1
            
            # Get consent summary
            consent_summary = self._get_consent_summary(user_id)
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(privacy_settings, consent_summary)
            
            return {
                'user_id': user_id,
                'report_date': datetime.now().isoformat(),
                'privacy_settings': privacy_settings['global_settings'],
                'memory_privacy_distribution': privacy_distribution,
                'consent_summary': consent_summary,
                'compliance_score': compliance_score,
                'recommendations': self._get_privacy_recommendations(privacy_settings, privacy_distribution)
            }
            
        except Exception as e:
            print(f"Error generating compliance report: {e}")
            return {
                'error': str(e),
                'report_date': datetime.now().isoformat()
            }
    
    def _get_default_privacy_settings(self) -> Dict[str, Any]:
        """Get default privacy settings for new users"""
        return {
            'analytics': False,
            'processing': True,
            'sharing': False,
            'marketing': False,
            'training': False,
            'retention_policy': 'standard',
            'data_minimization': True,
            'encryption_required': True,
            'created_at': datetime.now().isoformat()
        }
    
    def _get_memory_privacy_settings(self, user_id: str) -> Dict[str, Any]:
        """Get memory-level privacy settings"""
        try:
            memories_query = firestore_db.db.collection('memories').where('user_id', '==', user_id)
            memories = list(memories_query.stream())
            
            privacy_levels = {}
            for memory in memories:
                memory_data = memory.to_dict()
                privacy_levels[memory.id] = memory_data.get('privacy_level', 'private')
            
            return privacy_levels
            
        except Exception as e:
            print(f"Error getting memory privacy settings: {e}")
            return {}
    
    def _get_consent_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get consent history for a user"""
        try:
            consent_query = firestore_db.db.collection('consent_records').where('user_id', '==', user_id)
            consent_docs = consent_query.order_by('timestamp', direction='DESCENDING').limit(50).stream()
            
            consent_history = []
            for doc in consent_docs:
                consent_data = doc.to_dict()
                consent_history.append(consent_data)
            
            return consent_history
            
        except Exception as e:
            print(f"Error getting consent history: {e}")
            return []
    
    def _get_current_consents(self, user_id: str) -> Dict[str, Any]:
        """Get current consent status for a user"""
        try:
            consents_doc = firestore_db.db.collection('current_consents').document(user_id).get()
            
            if consents_doc.exists:
                return consents_doc.to_dict().get('consents', {})
            else:
                return {}
                
        except Exception as e:
            print(f"Error getting current consents: {e}")
            return {}
    
    def _get_consent_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of current consents"""
        try:
            current_consents = self._get_current_consents(user_id)
            
            summary = {}
            for consent_type in ConsentType:
                consent_info = current_consents.get(consent_type.value, {})
                summary[consent_type.value] = {
                    'granted': consent_info.get('granted', False),
                    'timestamp': consent_info.get('timestamp')
                }
            
            return summary
            
        except Exception as e:
            print(f"Error getting consent summary: {e}")
            return {}
    
    def _calculate_compliance_score(self, privacy_settings: Dict[str, Any], 
                                   consent_summary: Dict[str, Any]) -> float:
        """Calculate privacy compliance score (0-100)"""
        try:
            score = 0.0
            max_score = 100.0
            
            # Privacy settings score (40 points)
            global_settings = privacy_settings.get('global_settings', {})
            if global_settings.get('data_minimization', False):
                score += 10
            if global_settings.get('encryption_required', False):
                score += 10
            if not global_settings.get('analytics', True):  # Privacy-friendly default
                score += 10
            if not global_settings.get('sharing', True):  # Privacy-friendly default
                score += 10
            
            # Consent management score (30 points)
            explicit_consents = sum(1 for consent in consent_summary.values() 
                                  if consent.get('timestamp') is not None)
            consent_score = min(30, explicit_consents * 5)
            score += consent_score
            
            # Memory privacy score (30 points)
            memory_privacy = privacy_settings.get('memory_privacy', {})
            if memory_privacy:
                private_memories = sum(1 for level in memory_privacy.values() 
                                     if level in ['private', 'confidential'])
                total_memories = len(memory_privacy)
                if total_memories > 0:
                    privacy_ratio = private_memories / total_memories
                    score += privacy_ratio * 30
            else:
                score += 15  # Default score if no memories
            
            return min(max_score, score)
            
        except Exception as e:
            print(f"Error calculating compliance score: {e}")
            return 0.0
    
    def _get_privacy_recommendations(self, privacy_settings: Dict[str, Any], 
                                   privacy_distribution: Dict[str, int]) -> List[str]:
        """Get privacy recommendations for the user"""
        recommendations = []
        
        global_settings = privacy_settings.get('global_settings', {})
        
        # Check for privacy improvements
        if global_settings.get('analytics', False):
            recommendations.append("Consider disabling analytics for better privacy")
        
        if global_settings.get('sharing', False):
            recommendations.append("Consider disabling data sharing for enhanced privacy")
        
        # Check memory privacy distribution
        total_memories = sum(privacy_distribution.values())
        if total_memories > 0:
            public_ratio = privacy_distribution.get('public', 0) / total_memories
            if public_ratio > 0.3:
                recommendations.append("Consider making some public memories private for better privacy control")
        
        if not recommendations:
            recommendations.append("Your privacy settings look good! Keep reviewing them regularly.")
        
        return recommendations
    
    def _log_privacy_change(self, user_id: str, change_type: str, details: Dict[str, Any]) -> None:
        """Log privacy setting changes for audit purposes"""
        try:
            log_entry = {
                'user_id': user_id,
                'change_type': change_type,
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
            
            firestore_db.db.collection('privacy_audit_logs').add(log_entry)
            
        except Exception as e:
            print(f"Error logging privacy change: {e}")
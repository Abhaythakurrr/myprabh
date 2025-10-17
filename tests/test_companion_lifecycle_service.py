"""
Unit tests for Companion Lifecycle Service
Tests companion archiving, restoration, and modification
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import uuid
import json

from services.memory.companion_lifecycle_service import CompanionLifecycleService

class TestCompanionLifecycleService(unittest.TestCase):
    """Test cases for CompanionLifecycleService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = CompanionLifecycleService()
        self.test_user_id = "test_user_123"
        self.test_companion_id = str(uuid.uuid4())
        self.test_archive_id = str(uuid.uuid4())
        
        # Mock dependencies
        self.mock_firestore = Mock()
        self.mock_memory_manager = Mock()
        self.mock_personalization_engine = Mock()
        self.mock_context_service = Mock()
        
        # Patch the dependencies
        self.firestore_patcher = patch('services.memory.companion_lifecycle_service.firestore_db', self.mock_firestore)
        self.memory_patcher = patch.object(self.service, 'memory_manager', self.mock_memory_manager)
        self.personalization_patcher = patch.object(self.service, 'personalization_engine', self.mock_personalization_engine)
        self.context_patcher = patch.object(self.service, 'context_service', self.mock_context_service)
        
        self.firestore_patcher.start()
        self.memory_patcher.start()
        self.personalization_patcher.start()
        self.context_patcher.start()
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.firestore_patcher.stop()
        self.memory_patcher.stop()
        self.personalization_patcher.stop()
        self.context_patcher.stop()
    
    def test_archive_companion_success(self):
        """Test successful companion archiving"""
        # Arrange
        archive_options = {
            'preserve_memories': True,
            'preserve_conversations': True,
            'preserve_personality': True,
            'preserve_context': True,
            'reason': 'user_requested'
        }
        
        # Mock get companion info
        self.service._get_companion_info = Mock(return_value={
            'success': True,
            'companion': {
                'id': self.test_companion_id,
                'name': 'Test Companion',
                'status': 'active'
            }
        })
        
        # Mock create archive package
        self.service._create_archive_package = Mock(return_value={
            'success': True,
            'package': {
                'memories': {'total_memories': 5},
                'conversations': {'total_messages': 10},
                'personality': {'traits': ['friendly']},
                'context': {'context_data': {}}
            }
        })
        
        # Mock cleanup
        self.service._cleanup_archived_companion_data = Mock(return_value={
            'memories': 'Unassigned 5 memories',
            'context': 'Context data removed'
        })
        
        # Mock Firestore operations
        mock_doc_ref = Mock()
        self.mock_firestore.db.collection.return_value.document.return_value = mock_doc_ref
        
        # Mock logging
        self.service._log_companion_action = Mock()
        
        # Act
        result = self.service.archive_companion(self.test_user_id, self.test_companion_id, archive_options)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertIn('archive_id', result)
        self.assertIn('companion_name', result)
        self.assertIn('archived_at', result)
        self.assertIn('archive_package_size', result)
        
        # Verify method calls
        self.service._get_companion_info.assert_called_once_with(self.test_user_id, self.test_companion_id)
        self.service._create_archive_package.assert_called_once()
        mock_doc_ref.set.assert_called_once()
        mock_doc_ref.update.assert_called_once()
    
    def test_archive_companion_already_archived(self):
        """Test archiving a companion that's already archived"""
        # Arrange
        self.service._get_companion_info = Mock(return_value={
            'success': True,
            'companion': {
                'id': self.test_companion_id,
                'name': 'Test Companion',
                'status': 'archived'
            }
        })
        
        # Act
        result = self.service.archive_companion(self.test_user_id, self.test_companion_id)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Companion is already archived')
    
    def test_archive_companion_not_found(self):
        """Test archiving a non-existent companion"""
        # Arrange
        self.service._get_companion_info = Mock(return_value={
            'success': False,
            'error': 'Companion not found'
        })
        
        # Act
        result = self.service.archive_companion(self.test_user_id, self.test_companion_id)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Companion not found')
    
    def test_restore_companion_success(self):
        """Test successful companion restoration"""
        # Arrange
        restore_options = {
            'restore_memories': True,
            'restore_conversations': True,
            'restore_personality': True,
            'restore_context': True,
            'new_companion_name': 'Restored Companion'
        }
        
        # Mock archive document
        mock_archive_doc = Mock()
        mock_archive_doc.exists = True
        mock_archive_doc.to_dict.return_value = {
            'user_id': self.test_user_id,
            'companion_id': self.test_companion_id,
            'original_companion_data': {
                'name': 'Original Companion',
                'personality': 'friendly'
            },
            'archive_package': {
                'memories': {'memories': [{'id': 'mem1', 'content': 'test'}]},
                'conversations': {'conversations': [{'id': 'conv1', 'message': 'hello'}]},
                'personality': {'personality_traits': {'openness': 0.8}},
                'context': {'context_data': {'session': 'data'}}
            }
        }
        
        self.mock_firestore.db.collection.return_value.document.return_value.get.return_value = mock_archive_doc
        
        # Mock restoration methods
        self.service._restore_from_archive_package = Mock(return_value={
            'memories': {'restored_memories': 1},
            'conversations': {'restored_conversations': 1},
            'personality': {'restored_personality': True},
            'context': {'restored_context': True}
        })
        
        # Mock Firestore operations
        mock_doc_ref = Mock()
        self.mock_firestore.db.collection.return_value.document.return_value = mock_doc_ref
        
        # Mock logging
        self.service._log_companion_action = Mock()
        
        # Act
        result = self.service.restore_companion(self.test_user_id, self.test_archive_id, restore_options)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertIn('new_companion_id', result)
        self.assertEqual(result['companion_name'], 'Restored Companion')
        self.assertIn('restored_at', result)
        self.assertIn('restoration_result', result)
        
        # Verify method calls
        mock_doc_ref.set.assert_called_once()
        mock_archive_doc.reference.update = Mock()  # This would be called in real implementation
    
    def test_restore_companion_archive_not_found(self):
        """Test restoring from non-existent archive"""
        # Arrange
        mock_archive_doc = Mock()
        mock_archive_doc.exists = False
        
        self.mock_firestore.db.collection.return_value.document.return_value.get.return_value = mock_archive_doc
        
        # Act
        result = self.service.restore_companion(self.test_user_id, self.test_archive_id)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Archive not found')
    
    def test_restore_companion_access_denied(self):
        """Test restoring archive with wrong user"""
        # Arrange
        mock_archive_doc = Mock()
        mock_archive_doc.exists = True
        mock_archive_doc.to_dict.return_value = {
            'user_id': 'different_user',
            'companion_id': self.test_companion_id
        }
        
        self.mock_firestore.db.collection.return_value.document.return_value.get.return_value = mock_archive_doc
        
        # Act
        result = self.service.restore_companion(self.test_user_id, self.test_archive_id)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Access denied')
    
    def test_modify_companion_success(self):
        """Test successful companion modification"""
        # Arrange
        modifications = {
            'basic_properties': {
                'name': 'Modified Companion',
                'description': 'Updated description'
            },
            'personality': {
                'communication_style': 'formal',
                'personality_traits': {'openness': 0.9}
            }
        }
        
        # Mock get companion info
        self.service._get_companion_info = Mock(return_value={
            'success': True,
            'companion': {
                'id': self.test_companion_id,
                'name': 'Original Companion',
                'status': 'active',
                'modification_count': 0
            }
        })
        
        # Mock validation
        self.service._validate_modifications = Mock(return_value={'valid': True})
        
        # Mock backup creation
        self.service._create_modification_backup = Mock(return_value={
            'success': True,
            'backup_id': 'backup_123'
        })
        
        # Mock modification methods
        self.service._modify_basic_properties = Mock(return_value={
            'success': True,
            'updated_properties': ['name', 'description']
        })
        
        self.service._modify_personality = Mock(return_value={
            'success': True,
            'personality_updated': True
        })
        
        # Mock Firestore update
        mock_doc_ref = Mock()
        self.mock_firestore.db.collection.return_value.document.return_value = mock_doc_ref
        
        # Mock logging
        self.service._log_companion_action = Mock()
        
        # Act
        result = self.service.modify_companion(self.test_user_id, self.test_companion_id, modifications)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['companion_id'], self.test_companion_id)
        self.assertIn('modification_results', result)
        self.assertIn('backup_id', result)
        self.assertIn('modified_at', result)
        
        # Verify method calls
        self.service._validate_modifications.assert_called_once_with(modifications)
        self.service._create_modification_backup.assert_called_once()
        self.service._modify_basic_properties.assert_called_once()
        self.service._modify_personality.assert_called_once()
        mock_doc_ref.update.assert_called_once()
    
    def test_modify_companion_archived(self):
        """Test modifying an archived companion"""
        # Arrange
        modifications = {'basic_properties': {'name': 'New Name'}}
        
        self.service._get_companion_info = Mock(return_value={
            'success': True,
            'companion': {
                'id': self.test_companion_id,
                'status': 'archived'
            }
        })
        
        # Act
        result = self.service.modify_companion(self.test_user_id, self.test_companion_id, modifications)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn('Cannot modify archived companion', result['error'])
    
    def test_modify_companion_invalid_modifications(self):
        """Test modifying companion with invalid modifications"""
        # Arrange
        modifications = {'invalid_type': {'some': 'data'}}
        
        self.service._get_companion_info = Mock(return_value={
            'success': True,
            'companion': {'status': 'active'}
        })
        
        self.service._validate_modifications = Mock(return_value={
            'valid': False,
            'error': 'Invalid modification type: invalid_type'
        })
        
        # Act
        result = self.service.modify_companion(self.test_user_id, self.test_companion_id, modifications)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Invalid modification type: invalid_type')
    
    def test_get_companion_lifecycle_history(self):
        """Test getting companion lifecycle history"""
        # Arrange
        self.service._get_companion_info = Mock(return_value={
            'success': True,
            'companion': {'id': self.test_companion_id}
        })
        
        # Mock lifecycle logs
        mock_log1 = Mock()
        mock_log1.to_dict.return_value = {
            'action': 'created',
            'timestamp': datetime.now().isoformat(),
            'details': {'initial_setup': True},
            'user_id': self.test_user_id
        }
        
        mock_log2 = Mock()
        mock_log2.to_dict.return_value = {
            'action': 'modified',
            'timestamp': datetime.now().isoformat(),
            'details': {'modifications': {'name': 'Updated Name'}},
            'user_id': self.test_user_id
        }
        
        # Mock backup documents
        mock_backup1 = Mock()
        mock_backup1.id = 'backup_1'
        mock_backup1.to_dict.return_value = {
            'created_at': datetime.now().isoformat(),
            'backup_type': 'pre_modification',
            'modifications_applied': {'name': 'change'}
        }
        
        # Mock Firestore queries
        mock_logs_query = Mock()
        mock_logs_query.stream.return_value = [mock_log1, mock_log2]
        
        mock_backups_query = Mock()
        mock_backups_query.stream.return_value = [mock_backup1]
        
        self.mock_firestore.db.collection.return_value.where.return_value.where.return_value.order_by.return_value = mock_logs_query
        self.mock_firestore.db.collection.return_value.where.return_value.order_by.return_value = mock_backups_query
        
        # Act
        result = self.service.get_companion_lifecycle_history(self.test_user_id, self.test_companion_id)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['companion_id'], self.test_companion_id)
        self.assertEqual(len(result['lifecycle_history']), 2)
        self.assertEqual(len(result['modification_backups']), 1)
        self.assertEqual(result['total_actions'], 2)
        self.assertEqual(result['total_backups'], 1)
    
    def test_list_archived_companions(self):
        """Test listing archived companions"""
        # Arrange
        mock_archive1 = Mock()
        mock_archive1.id = 'archive_1'
        mock_archive1.to_dict.return_value = {
            'companion_id': 'comp_1',
            'original_companion_data': {
                'name': 'Archived Companion 1',
                'personality': 'friendly'
            },
            'archived_at': datetime.now().isoformat(),
            'archive_reason': 'user_requested',
            'archive_options': {'preserve_memories': True},
            'archive_package': {'memories': [], 'conversations': []}
        }
        
        mock_archive2 = Mock()
        mock_archive2.id = 'archive_2'
        mock_archive2.to_dict.return_value = {
            'companion_id': 'comp_2',
            'original_companion_data': {
                'name': 'Archived Companion 2',
                'personality': 'helpful'
            },
            'archived_at': datetime.now().isoformat(),
            'archive_reason': 'inactive',
            'archive_options': {'preserve_conversations': True},
            'restored_at': datetime.now().isoformat(),
            'restored_companion_id': 'comp_2_restored',
            'archive_package': {'memories': [], 'conversations': []}
        }
        
        # Mock Firestore query
        mock_query = Mock()
        mock_query.stream.return_value = [mock_archive1, mock_archive2]
        self.mock_firestore.db.collection.return_value.where.return_value.order_by.return_value = mock_query
        
        # Act
        result = self.service.list_archived_companions(self.test_user_id)
        
        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Archived Companion 1')
        self.assertEqual(result[1]['name'], 'Archived Companion 2')
        self.assertIsNone(result[0]['restored_at'])
        self.assertIsNotNone(result[1]['restored_at'])
    
    def test_delete_archived_companion_success(self):
        """Test successful deletion of archived companion"""
        # Arrange
        mock_archive_doc = Mock()
        mock_archive_doc.exists = True
        mock_archive_doc.to_dict.return_value = {
            'user_id': self.test_user_id,
            'companion_id': self.test_companion_id,
            'original_companion_data': {
                'name': 'Deleted Companion'
            }
        }
        mock_archive_doc.reference = Mock()
        
        self.mock_firestore.db.collection.return_value.document.return_value.get.return_value = mock_archive_doc
        
        # Mock deletion record creation
        mock_deletion_collection = Mock()
        self.mock_firestore.db.collection.return_value = mock_deletion_collection
        
        # Mock logging
        self.service._log_companion_action = Mock()
        
        # Act
        result = self.service.delete_archived_companion(self.test_user_id, self.test_archive_id)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['archive_id'], self.test_archive_id)
        self.assertEqual(result['companion_name'], 'Deleted Companion')
        self.assertIn('deleted_at', result)
        
        # Verify deletion
        mock_archive_doc.reference.delete.assert_called_once()
    
    def test_create_archive_package(self):
        """Test creating archive package"""
        # Arrange
        archive_options = {
            'preserve_memories': True,
            'preserve_conversations': True,
            'preserve_personality': True,
            'preserve_context': True
        }
        
        # Mock archive methods
        self.service._archive_companion_memories = Mock(return_value={
            'total_memories': 5,
            'memories': [{'id': 'mem1', 'content': 'test'}]
        })
        
        self.service._archive_companion_conversations = Mock(return_value={
            'total_messages': 10,
            'conversations': [{'id': 'conv1', 'message': 'hello'}]
        })
        
        self.service._archive_companion_personality = Mock(return_value={
            'personality_traits': {'openness': 0.8}
        })
        
        self.service._archive_companion_context = Mock(return_value={
            'context_data': {'session': 'data'}
        })
        
        # Act
        result = self.service._create_archive_package(self.test_user_id, self.test_companion_id, archive_options)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertIn('package', result)
        
        package = result['package']
        self.assertIn('memories', package)
        self.assertIn('conversations', package)
        self.assertIn('personality', package)
        self.assertIn('context', package)
        self.assertEqual(package['companion_id'], self.test_companion_id)
        self.assertEqual(package['user_id'], self.test_user_id)
    
    def test_validate_modifications_valid(self):
        """Test validation of valid modifications"""
        # Arrange
        modifications = {
            'basic_properties': {
                'name': 'Valid Name',
                'description': 'Valid description'
            },
            'personality': {
                'communication_style': 'casual'
            }
        }
        
        # Act
        result = self.service._validate_modifications(modifications)
        
        # Assert
        self.assertTrue(result['valid'])
    
    def test_validate_modifications_invalid_type(self):
        """Test validation of invalid modification type"""
        # Arrange
        modifications = {
            'invalid_type': {
                'some': 'data'
            }
        }
        
        # Act
        result = self.service._validate_modifications(modifications)
        
        # Assert
        self.assertFalse(result['valid'])
        self.assertIn('Invalid modification type', result['error'])
    
    def test_validate_modifications_name_too_long(self):
        """Test validation of name that's too long"""
        # Arrange
        modifications = {
            'basic_properties': {
                'name': 'x' * 101  # 101 characters, exceeds limit of 100
            }
        }
        
        # Act
        result = self.service._validate_modifications(modifications)
        
        # Assert
        self.assertFalse(result['valid'])
        self.assertIn('name too long', result['error'])

if __name__ == '__main__':
    unittest.main()
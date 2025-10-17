"""
Unit tests for Companion Management Service
Tests memory-based companion creation and data isolation
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import uuid

from services.memory.companion_management_service import CompanionManagementService

class TestCompanionManagementService(unittest.TestCase):
    """Test cases for CompanionManagementService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = CompanionManagementService()
        self.test_user_id = "test_user_123"
        self.test_companion_id = str(uuid.uuid4())
        
        # Mock dependencies
        self.mock_firestore = Mock()
        self.mock_memory_manager = Mock()
        self.mock_personalization_engine = Mock()
        self.mock_privacy_service = Mock()
        
        # Patch the dependencies
        self.firestore_patcher = patch('services.memory.companion_management_service.firestore_db', self.mock_firestore)
        self.memory_patcher = patch.object(self.service, 'memory_manager', self.mock_memory_manager)
        self.personalization_patcher = patch.object(self.service, 'personalization_engine', self.mock_personalization_engine)
        self.privacy_patcher = patch.object(self.service, 'privacy_service', self.mock_privacy_service)
        
        self.firestore_patcher.start()
        self.memory_patcher.start()
        self.personalization_patcher.start()
        self.privacy_patcher.start()
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.firestore_patcher.stop()
        self.memory_patcher.stop()
        self.personalization_patcher.stop()
        self.privacy_patcher.stop()
    
    def test_create_memory_based_companion_success(self):
        """Test successful creation of memory-based companion"""
        # Arrange
        companion_data = {
            'name': 'Test Companion',
            'personality': 'friendly',
            'description': 'A test companion'
        }
        memory_assignment = {'type': 'all'}
        
        # Mock validation success
        self.service._validate_memory_assignment = Mock(return_value={'valid': True})
        
        # Mock memory assignment success
        self.service._assign_memories_to_companion = Mock(return_value={
            'success': True,
            'assigned_memories': ['mem1', 'mem2'],
            'assigned_count': 2
        })
        
        # Mock personality initialization success
        self.service._initialize_companion_personality = Mock(return_value={
            'success': True,
            'personality_profile': {'traits': ['friendly']}
        })
        
        # Mock Firestore operations
        mock_doc_ref = Mock()
        self.mock_firestore.db.collection.return_value.document.return_value = mock_doc_ref
        
        # Act
        result = self.service.create_memory_based_companion(
            self.test_user_id, companion_data, memory_assignment
        )
        
        # Assert
        self.assertTrue(result['success'])
        self.assertIn('companion_id', result)
        self.assertEqual(result['memory_assignment_result']['assigned_count'], 2)
        
        # Verify Firestore calls
        self.mock_firestore.db.collection.assert_called_with('companions')
        mock_doc_ref.set.assert_called_once()
        mock_doc_ref.update.assert_called_once()
    
    def test_create_memory_based_companion_validation_failure(self):
        """Test companion creation with invalid memory assignment"""
        # Arrange
        companion_data = {'name': 'Test Companion'}
        memory_assignment = {'type': 'invalid'}
        
        # Mock validation failure
        self.service._validate_memory_assignment = Mock(return_value={
            'valid': False,
            'error': 'Invalid assignment type'
        })
        
        # Act
        result = self.service.create_memory_based_companion(
            self.test_user_id, companion_data, memory_assignment
        )
        
        # Assert
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Invalid assignment type')
    
    def test_validate_memory_assignment_all_type(self):
        """Test validation of 'all' memory assignment type"""
        # Arrange
        memory_assignment = {'type': 'all'}
        
        # Act
        result = self.service._validate_memory_assignment(self.test_user_id, memory_assignment)
        
        # Assert
        self.assertTrue(result['valid'])
    
    def test_validate_memory_assignment_selection_type(self):
        """Test validation of 'selection' memory assignment type"""
        # Arrange
        memory_assignment = {
            'type': 'selection',
            'memory_ids': ['mem1', 'mem2']
        }
        
        # Mock memory existence checks
        mock_doc1 = Mock()
        mock_doc1.exists = True
        mock_doc1.to_dict.return_value = {'user_id': self.test_user_id}
        
        mock_doc2 = Mock()
        mock_doc2.exists = True
        mock_doc2.to_dict.return_value = {'user_id': self.test_user_id}
        
        self.mock_firestore.db.collection.return_value.document.side_effect = [
            Mock(get=Mock(return_value=mock_doc1)),
            Mock(get=Mock(return_value=mock_doc2))
        ]
        
        # Act
        result = self.service._validate_memory_assignment(self.test_user_id, memory_assignment)
        
        # Assert
        self.assertTrue(result['valid'])
    
    def test_validate_memory_assignment_selection_no_ids(self):
        """Test validation failure when no memory IDs provided for selection"""
        # Arrange
        memory_assignment = {
            'type': 'selection',
            'memory_ids': []
        }
        
        # Act
        result = self.service._validate_memory_assignment(self.test_user_id, memory_assignment)
        
        # Assert
        self.assertFalse(result['valid'])
        self.assertIn('No memory IDs specified', result['error'])
    
    def test_validate_memory_assignment_filter_type(self):
        """Test validation of 'filter' memory assignment type"""
        # Arrange
        memory_assignment = {
            'type': 'filter',
            'filters': {'memory_type': 'emotional'}
        }
        
        # Act
        result = self.service._validate_memory_assignment(self.test_user_id, memory_assignment)
        
        # Assert
        self.assertTrue(result['valid'])
    
    def test_assign_memories_all_type(self):
        """Test assigning all memories to companion"""
        # Arrange
        memory_assignment = {'type': 'all'}
        
        # Mock memory documents
        mock_doc1 = Mock()
        mock_doc1.id = 'mem1'
        mock_doc2 = Mock()
        mock_doc2.id = 'mem2'
        
        self.mock_firestore.db.collection.return_value.where.return_value.stream.return_value = [
            mock_doc1, mock_doc2
        ]
        
        # Mock document update
        mock_update = Mock()
        self.mock_firestore.db.collection.return_value.document.return_value.update = mock_update
        
        # Act
        result = self.service._assign_memories_to_companion(
            self.test_user_id, self.test_companion_id, memory_assignment
        )
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['assigned_count'], 2)
        self.assertEqual(result['assigned_memories'], ['mem1', 'mem2'])
    
    def test_assign_memories_selection_type(self):
        """Test assigning selected memories to companion"""
        # Arrange
        memory_assignment = {
            'type': 'selection',
            'memory_ids': ['mem1', 'mem2']
        }
        
        # Mock document update
        mock_update = Mock()
        self.mock_firestore.db.collection.return_value.document.return_value.update = mock_update
        
        # Act
        result = self.service._assign_memories_to_companion(
            self.test_user_id, self.test_companion_id, memory_assignment
        )
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['assigned_count'], 2)
        self.assertEqual(result['assigned_memories'], ['mem1', 'mem2'])
    
    def test_get_companion_memory_assignment_success(self):
        """Test getting companion memory assignment details"""
        # Arrange
        mock_companion_doc = Mock()
        mock_companion_doc.exists = True
        mock_companion_doc.to_dict.return_value = {
            'user_id': self.test_user_id,
            'memory_assignment': {'type': 'all'},
            'created_at': datetime.now().isoformat()
        }
        
        self.mock_firestore.db.collection.return_value.document.return_value.get.return_value = mock_companion_doc
        
        # Mock assigned memory details
        self.service._get_assigned_memory_details = Mock(return_value=[
            {'id': 'mem1', 'content_preview': 'Test memory 1...'}
        ])
        
        # Act
        result = self.service.get_companion_memory_assignment(self.test_user_id, self.test_companion_id)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['companion_id'], self.test_companion_id)
        self.assertIn('memory_assignment', result)
        self.assertIn('assigned_memories', result)
    
    def test_get_companion_memory_assignment_not_found(self):
        """Test getting memory assignment for non-existent companion"""
        # Arrange
        mock_companion_doc = Mock()
        mock_companion_doc.exists = False
        
        self.mock_firestore.db.collection.return_value.document.return_value.get.return_value = mock_companion_doc
        
        # Act
        result = self.service.get_companion_memory_assignment(self.test_user_id, self.test_companion_id)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Companion not found')
    
    def test_get_companion_memory_assignment_access_denied(self):
        """Test getting memory assignment with wrong user"""
        # Arrange
        mock_companion_doc = Mock()
        mock_companion_doc.exists = True
        mock_companion_doc.to_dict.return_value = {
            'user_id': 'different_user',
            'memory_assignment': {'type': 'all'}
        }
        
        self.mock_firestore.db.collection.return_value.document.return_value.get.return_value = mock_companion_doc
        
        # Act
        result = self.service.get_companion_memory_assignment(self.test_user_id, self.test_companion_id)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Access denied')
    
    def test_check_memory_isolation(self):
        """Test checking memory isolation for a companion"""
        # Arrange
        mock_memory_docs = [Mock(), Mock(), Mock()]  # 3 memories
        self.mock_firestore.db.collection.return_value.where.return_value.stream.return_value = mock_memory_docs
        
        # Act
        result = self.service._check_memory_isolation(self.test_user_id, self.test_companion_id)
        
        # Assert
        self.assertTrue(result['isolated'])
        self.assertEqual(result['total_memories'], 3)
        self.assertEqual(result['shared_memories'], 0)
        self.assertEqual(result['isolation_ratio'], 1.0)
    
    def test_check_conversation_isolation(self):
        """Test checking conversation isolation for a companion"""
        # Arrange
        mock_conversation_docs = [Mock(), Mock()]  # 2 conversations
        self.mock_firestore.db.collection.return_value.where.return_value.stream.return_value = mock_conversation_docs
        
        # Act
        result = self.service._check_conversation_isolation(self.test_user_id, self.test_companion_id)
        
        # Assert
        self.assertTrue(result['isolated'])
        self.assertEqual(result['total_conversations'], 2)
        self.assertEqual(result['isolated_conversations'], 2)
    
    def test_check_personality_isolation(self):
        """Test checking personality isolation for a companion"""
        # Arrange
        mock_profile = Mock()
        self.mock_personalization_engine.get_personality_profile.return_value = mock_profile
        
        # Act
        result = self.service._check_personality_isolation(self.test_user_id, self.test_companion_id)
        
        # Assert
        self.assertTrue(result['isolated'])
        self.assertTrue(result['has_profile'])
        self.assertEqual(result['profile_completeness'], 1.0)
    
    def test_get_companion_data_isolation_status(self):
        """Test getting complete data isolation status"""
        # Arrange
        mock_companion_doc = Mock()
        mock_companion_doc.exists = True
        mock_companion_doc.to_dict.return_value = {'user_id': self.test_user_id}
        
        self.mock_firestore.db.collection.return_value.document.return_value.get.return_value = mock_companion_doc
        
        # Mock isolation checks
        self.service._check_memory_isolation = Mock(return_value={'isolated': True})
        self.service._check_conversation_isolation = Mock(return_value={'isolated': True})
        self.service._check_personality_isolation = Mock(return_value={'isolated': True})
        self.service._get_isolation_recommendations = Mock(return_value=['All good!'])
        
        # Act
        result = self.service.get_companion_data_isolation_status(self.test_user_id, self.test_companion_id)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['isolation_score'], 100.0)
        self.assertIn('memory_isolation', result)
        self.assertIn('conversation_isolation', result)
        self.assertIn('personality_isolation', result)
        self.assertIn('recommendations', result)
    
    def test_list_user_companions_with_memory_info(self):
        """Test listing companions with memory information"""
        # Arrange
        mock_doc1 = Mock()
        mock_doc1.id = 'comp1'
        mock_doc1.to_dict.return_value = {
            'name': 'Companion 1',
            'personality': 'friendly',
            'created_at': datetime.now().isoformat(),
            'memory_based': True,
            'status': 'active',
            'interaction_count': 5
        }
        
        mock_doc2 = Mock()
        mock_doc2.id = 'comp2'
        mock_doc2.to_dict.return_value = {
            'name': 'Companion 2',
            'personality': 'helpful',
            'created_at': datetime.now().isoformat(),
            'memory_based': False,
            'status': 'active',
            'interaction_count': 3
        }
        
        self.mock_firestore.db.collection.return_value.where.return_value.stream.return_value = [
            mock_doc1, mock_doc2
        ]
        
        # Mock memory stats
        self.service._get_companion_memory_stats = Mock(return_value={
            'total_memories': 10,
            'memory_types': {'emotional': 5, 'general': 5},
            'last_assignment': '2024-01-01'
        })
        
        # Act
        result = self.service.list_user_companions_with_memory_info(self.test_user_id)
        
        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Companion 1')
        self.assertEqual(result[1]['name'], 'Companion 2')
        self.assertIn('memory_stats', result[0])
        self.assertIn('memory_stats', result[1])

if __name__ == '__main__':
    unittest.main()
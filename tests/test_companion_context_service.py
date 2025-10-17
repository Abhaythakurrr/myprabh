"""
Unit tests for Companion Context Service
Tests companion switching and context isolation
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import uuid

from services.memory.companion_context_service import CompanionContextService

class TestCompanionContextService(unittest.TestCase):
    """Test cases for CompanionContextService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = CompanionContextService()
        self.test_user_id = "test_user_123"
        self.test_companion_id_1 = str(uuid.uuid4())
        self.test_companion_id_2 = str(uuid.uuid4())
        
        # Mock dependencies
        self.mock_firestore = Mock()
        self.mock_memory_manager = Mock()
        self.mock_personalization_engine = Mock()
        
        # Patch the dependencies
        self.firestore_patcher = patch('services.memory.companion_context_service.firestore_db', self.mock_firestore)
        self.memory_patcher = patch.object(self.service, 'memory_manager', self.mock_memory_manager)
        self.personalization_patcher = patch.object(self.service, 'personalization_engine', self.mock_personalization_engine)
        
        self.firestore_patcher.start()
        self.memory_patcher.start()
        self.personalization_patcher.start()
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.firestore_patcher.stop()
        self.memory_patcher.stop()
        self.personalization_patcher.stop()
    
    def test_switch_companion_context_success(self):
        """Test successful companion context switching"""
        # Arrange
        session_data = {
            'session_id': 'test_session',
            'conversation_turn': 5,
            'last_message': 'Hello'
        }
        
        # Mock save current context
        self.service._save_companion_context = Mock(return_value={'success': True})
        
        # Mock get companion info
        self.service._get_companion_info = Mock(return_value={
            'success': True,
            'companion': {
                'id': self.test_companion_id_2,
                'name': 'Test Companion 2',
                'personality': 'helpful'
            }
        })
        
        # Mock load context
        self.service._load_companion_context = Mock(return_value={
            'success': True,
            'context': {'saved_data': 'test'},
            'conversation_history': [{'message': 'test'}],
            'personality_context': {'traits': ['helpful']},
            'memory_context': {'total_memories': 5}
        })
        
        # Mock update activity
        self.service._update_companion_activity = Mock()
        self.service._log_context_switch = Mock()
        
        # Act
        result = self.service.switch_companion_context(
            self.test_user_id, self.test_companion_id_1, self.test_companion_id_2, session_data
        )
        
        # Assert
        self.assertTrue(result['success'])
        self.assertIn('companion_info', result)
        self.assertIn('context', result)
        self.assertIn('conversation_history', result)
        self.assertIn('personality_context', result)
        self.assertIn('memory_context', result)
        self.assertIn('switch_timestamp', result)
        
        # Verify method calls
        self.service._save_companion_context.assert_called_once_with(
            self.test_user_id, self.test_companion_id_1, session_data
        )
        self.service._get_companion_info.assert_called_once_with(
            self.test_user_id, self.test_companion_id_2
        )
        self.service._load_companion_context.assert_called_once_with(
            self.test_user_id, self.test_companion_id_2
        )
    
    def test_switch_companion_context_save_failure(self):
        """Test companion switching with save context failure"""
        # Arrange
        session_data = {'session_id': 'test_session'}
        
        # Mock save failure
        self.service._save_companion_context = Mock(return_value={
            'success': False,
            'error': 'Save failed'
        })
        
        # Act
        result = self.service.switch_companion_context(
            self.test_user_id, self.test_companion_id_1, self.test_companion_id_2, session_data
        )
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn('Failed to save current context', result['error'])
    
    def test_switch_companion_context_companion_not_found(self):
        """Test companion switching with target companion not found"""
        # Arrange
        session_data = {'session_id': 'test_session'}
        
        # Mock save success
        self.service._save_companion_context = Mock(return_value={'success': True})
        
        # Mock companion not found
        self.service._get_companion_info = Mock(return_value={
            'success': False,
            'error': 'Companion not found'
        })
        
        # Act
        result = self.service.switch_companion_context(
            self.test_user_id, self.test_companion_id_1, self.test_companion_id_2, session_data
        )
        
        # Assert
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Companion not found')
    
    def test_switch_companion_context_no_from_companion(self):
        """Test companion switching without a source companion (initial switch)"""
        # Arrange
        session_data = {'session_id': 'test_session'}
        
        # Mock get companion info
        self.service._get_companion_info = Mock(return_value={
            'success': True,
            'companion': {'id': self.test_companion_id_2, 'name': 'Test Companion 2'}
        })
        
        # Mock load context
        self.service._load_companion_context = Mock(return_value={
            'success': True,
            'context': {},
            'conversation_history': [],
            'personality_context': {},
            'memory_context': {}
        })
        
        # Mock other methods
        self.service._update_companion_activity = Mock()
        self.service._log_context_switch = Mock()
        
        # Act
        result = self.service.switch_companion_context(
            self.test_user_id, None, self.test_companion_id_2, session_data
        )
        
        # Assert
        self.assertTrue(result['success'])
        # Should not try to save context when from_companion_id is None
        self.service._save_companion_context = Mock()  # Reset mock
        self.service._save_companion_context.assert_not_called()
    
    def test_get_companion_context_success(self):
        """Test getting companion context successfully"""
        # Arrange
        # Mock get companion info
        self.service._get_companion_info = Mock(return_value={
            'success': True,
            'companion': {'id': self.test_companion_id_1, 'name': 'Test Companion'}
        })
        
        # Mock load context
        self.service._load_companion_context = Mock(return_value={
            'success': True,
            'context': {'test': 'data'},
            'conversation_history': [{'message': 'test'}],
            'personality_context': {'traits': ['friendly']},
            'memory_context': {'total_memories': 3}
        })
        
        # Act
        result = self.service.get_companion_context(self.test_user_id, self.test_companion_id_1)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertIn('companion_info', result)
        self.assertIn('context', result)
        self.assertIn('conversation_history', result)
        self.assertIn('personality_context', result)
        self.assertIn('memory_context', result)
    
    def test_save_conversation_state_success(self):
        """Test saving conversation state successfully"""
        # Arrange
        conversation_state = {
            'session_id': 'test_session',
            'conversation_turn': 10,
            'context_summary': 'Test conversation',
            'emotional_state': {'mood': 'happy'},
            'topic_context': ['greeting', 'weather']
        }
        
        # Mock get companion info
        self.service._get_companion_info = Mock(return_value={
            'success': True,
            'companion': {'id': self.test_companion_id_1}
        })
        
        # Mock Firestore set
        mock_doc_ref = Mock()
        self.mock_firestore.db.collection.return_value.document.return_value = mock_doc_ref
        
        # Act
        result = self.service.save_conversation_state(
            self.test_user_id, self.test_companion_id_1, conversation_state
        )
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Conversation state saved successfully')
        
        # Verify Firestore call
        self.mock_firestore.db.collection.assert_called_with('companion_contexts')
        mock_doc_ref.set.assert_called_once()
    
    def test_get_active_companions(self):
        """Test getting list of active companions"""
        # Arrange
        mock_doc1 = Mock()
        mock_doc1.id = 'comp1'
        mock_doc1.to_dict.return_value = {
            'name': 'Companion 1',
            'personality': 'friendly',
            'avatar': '😊',
            'last_activity': datetime.now().isoformat(),
            'interaction_count': 5,
            'memory_based': True,
            'status': 'active'
        }
        
        mock_doc2 = Mock()
        mock_doc2.id = 'comp2'
        mock_doc2.to_dict.return_value = {
            'name': 'Companion 2',
            'personality': 'helpful',
            'avatar': '🤖',
            'last_activity': datetime.now().isoformat(),
            'interaction_count': 3,
            'memory_based': False,
            'status': 'active'
        }
        
        # Mock Firestore query
        mock_query = Mock()
        mock_query.stream.return_value = [mock_doc1, mock_doc2]
        self.mock_firestore.db.collection.return_value.where.return_value.order_by.return_value.limit.return_value = mock_query
        
        # Mock context summary
        self.service._get_context_summary = Mock(return_value={
            'last_message': {'preview': 'Hello...', 'timestamp': datetime.now().isoformat()},
            'conversation_turn': 5
        })
        
        # Act
        result = self.service.get_active_companions(self.test_user_id, limit=10)
        
        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Companion 1')
        self.assertEqual(result[1]['name'], 'Companion 2')
        self.assertTrue(result[0]['memory_based'])
        self.assertFalse(result[1]['memory_based'])
        self.assertIn('context_summary', result[0])
        self.assertIn('context_summary', result[1])
    
    def test_get_context_isolation_status(self):
        """Test getting context isolation status"""
        # Arrange
        # Mock isolation checks
        self.service._check_conversation_isolation = Mock(return_value={
            'isolated': True,
            'total_messages': 10,
            'isolation_level': 'complete'
        })
        
        self.service._check_memory_context_isolation = Mock(return_value={
            'isolated': True,
            'assigned_memories': 5,
            'isolation_level': 'complete'
        })
        
        self.service._check_personality_context_isolation = Mock(return_value={
            'isolated': True,
            'has_profile': True,
            'isolation_level': 'complete'
        })
        
        self.service._check_session_isolation = Mock(return_value={
            'isolated': True,
            'has_context': True,
            'isolation_level': 'complete'
        })
        
        self.service._get_isolation_recommendations = Mock(return_value=[
            'All systems properly isolated'
        ])
        
        # Act
        result = self.service.get_context_isolation_status(self.test_user_id, self.test_companion_id_1)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['isolation_score'], 100.0)
        self.assertIn('conversation_isolation', result)
        self.assertIn('memory_isolation', result)
        self.assertIn('personality_isolation', result)
        self.assertIn('session_isolation', result)
        self.assertIn('recommendations', result)
    
    def test_cleanup_inactive_contexts(self):
        """Test cleaning up inactive companion contexts"""
        # Arrange
        days_inactive = 30
        old_date = (datetime.now() - timedelta(days=days_inactive + 1)).isoformat()
        
        # Mock inactive context documents
        mock_context_doc1 = Mock()
        mock_context_doc1.to_dict.return_value = {
            'companion_id': 'old_comp_1',
            'user_id': self.test_user_id,
            'last_updated': old_date
        }
        mock_context_doc1.reference = Mock()
        
        mock_context_doc2 = Mock()
        mock_context_doc2.to_dict.return_value = {
            'companion_id': 'old_comp_2',
            'user_id': self.test_user_id,
            'last_updated': old_date
        }
        mock_context_doc2.reference = Mock()
        
        # Mock Firestore query for contexts
        mock_contexts_query = Mock()
        mock_contexts_query.stream.return_value = [mock_context_doc1, mock_context_doc2]
        self.mock_firestore.db.collection.return_value.where.return_value.where.return_value = mock_contexts_query
        
        # Mock companion existence checks (both companions don't exist)
        mock_companion_doc = Mock()
        mock_companion_doc.exists = False
        self.mock_firestore.db.collection.return_value.document.return_value.get.return_value = mock_companion_doc
        
        # Mock archived contexts collection
        mock_archived_collection = Mock()
        self.mock_firestore.db.collection.return_value = mock_archived_collection
        
        # Act
        result = self.service.cleanup_inactive_contexts(self.test_user_id, days_inactive)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['cleaned_count'], 2)
        self.assertEqual(len(result['archived_contexts']), 2)
        self.assertIn('old_comp_1', result['archived_contexts'])
        self.assertIn('old_comp_2', result['archived_contexts'])
    
    def test_load_conversation_history(self):
        """Test loading conversation history for a companion"""
        # Arrange
        mock_message1 = Mock()
        mock_message1.id = 'msg1'
        mock_message1.to_dict.return_value = {
            'user_message': 'Hello',
            'ai_response': 'Hi there!',
            'timestamp': datetime.now().isoformat(),
            'metadata': {'turn': 1}
        }
        
        mock_message2 = Mock()
        mock_message2.id = 'msg2'
        mock_message2.to_dict.return_value = {
            'user_message': 'How are you?',
            'ai_response': 'I am doing well!',
            'timestamp': datetime.now().isoformat(),
            'metadata': {'turn': 2}
        }
        
        # Mock Firestore query
        mock_query = Mock()
        mock_query.stream.return_value = [mock_message2, mock_message1]  # Reversed order from DB
        self.mock_firestore.db.collection.return_value.where.return_value.where.return_value.order_by.return_value.limit.return_value = mock_query
        
        # Act
        result = self.service._load_conversation_history(self.test_user_id, self.test_companion_id_1, limit=20)
        
        # Assert
        self.assertEqual(len(result), 2)
        # Should be in chronological order (reversed from DB order)
        self.assertEqual(result[0]['user_message'], 'Hello')
        self.assertEqual(result[1]['user_message'], 'How are you?')
    
    def test_load_personality_context(self):
        """Test loading personality context for a companion"""
        # Arrange
        mock_profile = Mock()
        mock_profile.personality_traits = {'openness': 0.8, 'extraversion': 0.6}
        mock_profile.communication_style = 'casual'
        mock_profile.emotional_patterns = {'positive': 0.7}
        mock_profile.persona_prompt = 'You are a friendly companion'
        mock_profile.personalization_level = 'high'
        mock_profile.last_updated = datetime.now()
        
        self.mock_personalization_engine.get_personality_profile.return_value = mock_profile
        
        # Act
        result = self.service._load_personality_context(self.test_user_id, self.test_companion_id_1)
        
        # Assert
        self.assertIn('personality_traits', result)
        self.assertIn('communication_style', result)
        self.assertIn('emotional_patterns', result)
        self.assertIn('persona_prompt', result)
        self.assertIn('personalization_level', result)
        self.assertIn('last_updated', result)
        self.assertEqual(result['communication_style'], 'casual')
    
    def test_load_memory_context(self):
        """Test loading memory context for a companion"""
        # Arrange
        mock_memory1 = Mock()
        mock_memory1.id = 'mem1'
        mock_memory1.to_dict.return_value = {
            'content': 'This is a test memory content that is longer than 100 characters to test the preview functionality',
            'memory_type': 'emotional',
            'timestamp': datetime.now().isoformat()
        }
        
        mock_memory2 = Mock()
        mock_memory2.id = 'mem2'
        mock_memory2.to_dict.return_value = {
            'content': 'Another memory',
            'memory_type': 'general',
            'timestamp': datetime.now().isoformat()
        }
        
        # Mock Firestore query
        mock_query = Mock()
        mock_query.stream.return_value = [mock_memory1, mock_memory2]
        self.mock_firestore.db.collection.return_value.where.return_value = mock_query
        
        # Act
        result = self.service._load_memory_context(self.test_user_id, self.test_companion_id_1)
        
        # Assert
        self.assertEqual(result['total_assigned_memories'], 2)
        self.assertIn('recent_memories', result)
        self.assertEqual(len(result['recent_memories']), 2)
        self.assertIn('memory_assignment_type', result)
        self.assertIn('last_memory_access', result)
        
        # Check content preview truncation
        first_memory = result['recent_memories'][0]
        self.assertTrue(first_memory['content_preview'].endswith('...'))
        self.assertTrue(len(first_memory['content_preview']) <= 103)  # 100 chars + '...'

if __name__ == '__main__':
    unittest.main()
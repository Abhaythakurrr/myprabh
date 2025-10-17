"""
Unit tests for memory manager
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from services.memory.memory_manager import MemoryManager
from services.memory.memory_models import MemoryType, SourceType, RetentionPolicy, PrivacyLevel

class TestMemoryManager:
    """Test cases for MemoryManager"""
    
    def setup_method(self):
        """Set up test environment"""
        # Mock all the services
        with patch('services.memory.memory_manager.MemoryProcessor') as mock_processor, \
             patch('services.memory.memory_manager.VectorMemoryStore') as mock_vector_store, \
             patch('services.memory.memory_manager.EmbeddingService') as mock_embedding_service, \
             patch('services.memory.memory_manager.MemoryUploadService') as mock_upload_service, \
             patch('services.memory.memory_manager.firestore_db') as mock_firestore:
            
            self.manager = MemoryManager()
            
            # Set up mocks
            self.mock_processor = mock_processor.return_value
            self.mock_vector_store = mock_vector_store.return_value
            self.mock_embedding_service = mock_embedding_service.return_value
            self.mock_upload_service = mock_upload_service.return_value
            self.mock_firestore = mock_firestore
            
            # Test data
            self.test_user_id = "test_user_123"
            self.test_companion_id = "test_companion_456"
            self.test_content = "This is test memory content about a wonderful day."
    
    def test_process_and_store_memory(self):
        """Test processing and storing memory content"""
        # Mock memory chunk
        mock_chunk = Mock()
        mock_chunk.id = "chunk_123"
        mock_chunk.content = self.test_content
        mock_chunk.embedding = [0.1, 0.2, 0.3]
        mock_chunk.to_dict.return_value = {'id': 'chunk_123', 'content': self.test_content}
        
        # Mock processor response
        self.mock_processor.create_memory_chunks.return_value = [mock_chunk]
        
        # Mock vector store response
        self.mock_vector_store.store_memory.return_value = "vector_id_123"
        
        # Mock Firestore
        mock_doc_ref = Mock()
        self.mock_firestore.db.collection.return_value.document.return_value = mock_doc_ref
        
        # Test the method
        result = self.manager.process_and_store_memory(
            user_id=self.test_user_id,
            companion_id=self.test_companion_id,
            content=self.test_content
        )
        
        # Verify calls
        self.mock_processor.create_memory_chunks.assert_called_once()
        self.mock_vector_store.store_memory.assert_called_once()
        mock_doc_ref.set.assert_called_once()
        
        # Verify result
        assert result == ["chunk_123"]
    
    def test_retrieve_relevant_memories(self):
        """Test retrieving relevant memories"""
        query = "happy memories"
        
        # Mock embedding service
        mock_embedding = [0.1, 0.2, 0.3]
        self.mock_embedding_service.generate_embedding.return_value = mock_embedding
        
        # Mock vector store search results
        mock_search_results = [
            {
                'id': 'memory_1',
                'score': 0.9,
                'content': 'Happy memory content',
                'metadata': {
                    'memory_type': 'emotional',
                    'timestamp': datetime.now().isoformat()
                }
            }
        ]
        self.mock_vector_store.search_memories.return_value = mock_search_results
        
        # Mock Firestore enrichment
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {'additional': 'data'}
        self.mock_firestore.db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # Test the method
        result = self.manager.retrieve_relevant_memories(
            user_id=self.test_user_id,
            companion_id=self.test_companion_id,
            query=query,
            limit=5
        )
        
        # Verify calls
        self.mock_embedding_service.generate_embedding.assert_called_once_with(query)
        self.mock_vector_store.search_memories.assert_called_once()
        
        # Verify result
        assert len(result) == 1
        assert result[0]['id'] == 'memory_1'
        assert 'enriched' in result[0]
    
    def test_upload_and_process_file(self):
        """Test file upload and processing"""
        file_data = b"Test file content"
        file_type = "text/plain"
        filename = "test.txt"
        
        # Mock upload service
        session_id = "session_123"
        self.mock_upload_service.upload_memory.return_value = session_id
        self.mock_upload_service.get_session_content.return_value = "Processed content"
        
        # Mock memory processing
        mock_chunk = Mock()
        mock_chunk.id = "chunk_123"
        mock_chunk.content = "Processed content"
        mock_chunk.embedding = [0.1, 0.2, 0.3]
        mock_chunk.to_dict.return_value = {'id': 'chunk_123'}
        
        self.mock_processor.create_memory_chunks.return_value = [mock_chunk]
        self.mock_vector_store.store_memory.return_value = "vector_id_123"
        
        # Mock Firestore
        mock_doc_ref = Mock()
        self.mock_firestore.db.collection.return_value.document.return_value = mock_doc_ref
        
        # Test the method
        result = self.manager.upload_and_process_file(
            user_id=self.test_user_id,
            companion_id=self.test_companion_id,
            file_data=file_data,
            file_type=file_type,
            filename=filename
        )
        
        # Verify calls
        self.mock_upload_service.upload_memory.assert_called_once()
        self.mock_upload_service.get_session_content.assert_called_once()
        
        # Verify result
        assert result == session_id
    
    def test_determine_source_type(self):
        """Test source type determination from file type"""
        # Test different file types
        assert self.manager._determine_source_type("text/plain") == SourceType.TEXT
        assert self.manager._determine_source_type("audio/mp3") == SourceType.VOICE
        assert self.manager._determine_source_type("image/jpeg") == SourceType.PHOTO
        assert self.manager._determine_source_type("application/json") == SourceType.CHAT
        assert self.manager._determine_source_type("application/pdf") == SourceType.DOCUMENT
    
    def test_get_memory_by_id(self):
        """Test getting memory by ID"""
        memory_id = "memory_123"
        
        # Mock Firestore response
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'id': memory_id,
            'user_id': self.test_user_id,
            'content': 'Test memory content'
        }
        self.mock_firestore.db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # Test the method
        result = self.manager.get_memory_by_id(memory_id, self.test_user_id)
        
        # Verify result
        assert result is not None
        assert result['id'] == memory_id
        assert result['user_id'] == self.test_user_id
    
    def test_get_memory_by_id_not_found(self):
        """Test getting non-existent memory by ID"""
        memory_id = "nonexistent_memory"
        
        # Mock Firestore response
        mock_doc = Mock()
        mock_doc.exists = False
        self.mock_firestore.db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # Test the method
        result = self.manager.get_memory_by_id(memory_id, self.test_user_id)
        
        # Verify result
        assert result is None
    
    def test_get_memory_by_id_wrong_user(self):
        """Test getting memory by ID with wrong user"""
        memory_id = "memory_123"
        wrong_user_id = "wrong_user"
        
        # Mock Firestore response
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'id': memory_id,
            'user_id': self.test_user_id,  # Different user
            'content': 'Test memory content'
        }
        self.mock_firestore.db.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # Test the method
        result = self.manager.get_memory_by_id(memory_id, wrong_user_id)
        
        # Verify result
        assert result is None
    
    def test_update_memory(self):
        """Test updating memory"""
        memory_id = "memory_123"
        updates = {'content': 'Updated content'}
        
        # Mock get_memory_by_id to return existing memory
        with patch.object(self.manager, 'get_memory_by_id', return_value={'id': memory_id}):
            # Mock Firestore update
            mock_doc_ref = Mock()
            self.mock_firestore.db.collection.return_value.document.return_value = mock_doc_ref
            
            # Test the method
            result = self.manager.update_memory(memory_id, self.test_user_id, updates)
            
            # Verify calls
            mock_doc_ref.update.assert_called_once()
            self.mock_vector_store.update_memory_metadata.assert_called_once()
            
            # Verify result
            assert result is True
    
    def test_update_memory_not_found(self):
        """Test updating non-existent memory"""
        memory_id = "nonexistent_memory"
        updates = {'content': 'Updated content'}
        
        # Mock get_memory_by_id to return None
        with patch.object(self.manager, 'get_memory_by_id', return_value=None):
            # Test the method
            result = self.manager.update_memory(memory_id, self.test_user_id, updates)
            
            # Verify result
            assert result is False
    
    def test_delete_memory(self):
        """Test deleting memory"""
        memory_id = "memory_123"
        
        # Mock get_memory_by_id to return existing memory
        with patch.object(self.manager, 'get_memory_by_id', return_value={'id': memory_id}):
            # Mock Firestore delete
            mock_doc_ref = Mock()
            self.mock_firestore.db.collection.return_value.document.return_value = mock_doc_ref
            
            # Test the method
            result = self.manager.delete_memory(memory_id, self.test_user_id)
            
            # Verify calls
            mock_doc_ref.delete.assert_called_once()
            
            # Verify result
            assert result is True
    
    def test_delete_all_user_memories(self):
        """Test deleting all user memories"""
        # Mock vector store deletion
        self.mock_vector_store.delete_user_memories.return_value = True
        
        # Mock Firestore query and batch delete
        mock_doc1 = Mock()
        mock_doc1.reference = Mock()
        mock_doc2 = Mock()
        mock_doc2.reference = Mock()
        
        mock_query = Mock()
        mock_query.stream.return_value = [mock_doc1, mock_doc2]
        mock_query.where.return_value = mock_query
        
        self.mock_firestore.db.collection.return_value.where.return_value = mock_query
        
        mock_batch = Mock()
        self.mock_firestore.db.batch.return_value = mock_batch
        
        # Test the method
        result = self.manager.delete_all_user_memories(self.test_user_id)
        
        # Verify calls
        self.mock_vector_store.delete_user_memories.assert_called_once_with(self.test_user_id, None)
        mock_batch.delete.assert_called()
        mock_batch.commit.assert_called_once()
        
        # Verify result
        assert result is True
    
    def test_should_retain_memory(self):
        """Test memory retention policy checking"""
        # Test long-term retention (should always retain)
        metadata_long_term = {
            'retention_policy': 'long_term',
            'timestamp': (datetime.now() - timedelta(days=400)).isoformat()
        }
        assert self.manager._should_retain_memory(metadata_long_term) is True
        
        # Test short-term retention (recent memory)
        metadata_short_term_recent = {
            'retention_policy': 'short_term',
            'timestamp': (datetime.now() - timedelta(days=15)).isoformat()
        }
        assert self.manager._should_retain_memory(metadata_short_term_recent) is True
        
        # Test short-term retention (old memory)
        metadata_short_term_old = {
            'retention_policy': 'short_term',
            'timestamp': (datetime.now() - timedelta(days=45)).isoformat()
        }
        assert self.manager._should_retain_memory(metadata_short_term_old) is False
    
    def test_calculate_recency_score(self):
        """Test recency score calculation"""
        # Recent memory should have high score
        recent_metadata = {
            'timestamp': (datetime.now() - timedelta(days=1)).isoformat()
        }
        recent_score = self.manager._calculate_recency_score(recent_metadata)
        assert recent_score > 0.9
        
        # Old memory should have low score
        old_metadata = {
            'timestamp': (datetime.now() - timedelta(days=300)).isoformat()
        }
        old_score = self.manager._calculate_recency_score(old_metadata)
        assert old_score < 0.5
        
        # Very old memory should have very low score
        very_old_metadata = {
            'timestamp': (datetime.now() - timedelta(days=400)).isoformat()
        }
        very_old_score = self.manager._calculate_recency_score(very_old_metadata)
        assert very_old_score < old_score
    
    def test_calculate_text_match_score(self):
        """Test text match score calculation"""
        content = "this is a test content with some important words"
        
        # Exact match should have high score
        search_terms = ["test", "content"]
        score = self.manager._calculate_text_match_score(content, search_terms)
        assert score > 0
        
        # Phrase match should have higher score
        search_terms_phrase = ["test content"]
        score_phrase = self.manager._calculate_text_match_score(content, search_terms_phrase)
        assert score_phrase > 0
        
        # No match should have zero score
        search_terms_no_match = ["nonexistent", "words"]
        score_no_match = self.manager._calculate_text_match_score(content, search_terms_no_match)
        assert score_no_match == 0
    
    def test_get_user_memory_stats(self):
        """Test getting user memory statistics"""
        # Mock Firestore query
        mock_doc1 = Mock()
        mock_doc1.to_dict.return_value = {
            'memory_type': 'emotional',
            'source_type': 'text',
            'content': 'Test content 1',
            'timestamp': datetime.now().isoformat()
        }
        
        mock_doc2 = Mock()
        mock_doc2.to_dict.return_value = {
            'memory_type': 'factual',
            'source_type': 'voice',
            'content': 'Test content 2',
            'timestamp': (datetime.now() - timedelta(days=1)).isoformat()
        }
        
        mock_query = Mock()
        mock_query.stream.return_value = [mock_doc1, mock_doc2]
        mock_query.where.return_value = mock_query
        
        self.mock_firestore.db.collection.return_value.where.return_value = mock_query
        
        # Test the method
        result = self.manager.get_user_memory_stats(self.test_user_id)
        
        # Verify result
        assert result['total_memories'] == 2
        assert result['memory_types']['emotional'] == 1
        assert result['memory_types']['factual'] == 1
        assert result['source_types']['text'] == 1
        assert result['source_types']['voice'] == 1
        assert result['total_content_length'] > 0
        assert result['oldest_memory'] is not None
        assert result['newest_memory'] is not None
    
    def test_export_user_memories(self):
        """Test exporting user memories"""
        # Mock Firestore query
        mock_doc1 = Mock()
        mock_doc1.to_dict.return_value = {
            'id': 'memory_1',
            'content': 'Test memory 1',
            'user_id': self.test_user_id
        }
        
        mock_doc2 = Mock()
        mock_doc2.to_dict.return_value = {
            'id': 'memory_2',
            'content': 'Test memory 2',
            'user_id': self.test_user_id
        }
        
        mock_query = Mock()
        mock_query.stream.return_value = [mock_doc1, mock_doc2]
        mock_query.where.return_value = mock_query
        
        self.mock_firestore.db.collection.return_value.where.return_value = mock_query
        
        # Test the method
        result = self.manager.export_user_memories(self.test_user_id)
        
        # Verify result
        assert result['user_id'] == self.test_user_id
        assert result['total_memories'] == 2
        assert len(result['memories']) == 2
        assert 'export_date' in result
        assert 'metadata' in result
        assert result['metadata']['privacy_compliant'] is True

if __name__ == "__main__":
    pytest.main([__file__])
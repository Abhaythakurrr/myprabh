"""
Unit tests for embedding service
"""

import pytest
import numpy as np
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from services.memory.embedding_service import EmbeddingService

class TestEmbeddingService:
    """Test cases for EmbeddingService"""
    
    def setup_method(self):
        """Set up test environment"""
        # Use a temporary directory for cache
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the cache file path
        with patch.object(EmbeddingService, '__init__', lambda x: None):
            self.service = EmbeddingService()
            self.service.config = Mock()
            self.service.config.get_embedding_config.return_value = {
                'model': 'sentence-transformers/all-MiniLM-L6-v2',
                'dimension': 384
            }
            self.service.embedding_config = {'model': 'test-model', 'dimension': 384}
            self.service.cache = {}
            self.service.cache_file = os.path.join(self.temp_dir, 'test_cache.pkl')
            self.service.model = "simple"  # Use simple model for testing
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_generate_simple_embedding(self):
        """Test simple embedding generation"""
        text = "This is a test sentence for embedding generation."
        
        embedding = self.service._generate_simple_embedding(text)
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.dtype == np.float32
        assert len(embedding) == 384
        
        # Embedding should be normalized
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 0.01 or norm == 0.0  # Allow for zero embeddings
    
    def test_generate_embedding_with_caching(self):
        """Test embedding generation with caching"""
        text = "Test sentence for caching."
        
        # First call should generate embedding
        embedding1 = self.service.generate_embedding(text)
        
        # Second call should use cache
        embedding2 = self.service.generate_embedding(text)
        
        # Should be identical (from cache)
        np.testing.assert_array_equal(embedding1, embedding2)
        
        # Check that it's in cache
        text_hash = self.service._hash_text(text)
        assert text_hash in self.service.cache
    
    def test_generate_embeddings_batch(self):
        """Test batch embedding generation"""
        texts = [
            "First test sentence.",
            "Second test sentence.",
            "Third test sentence with more words."
        ]
        
        embeddings = self.service.generate_embeddings(texts)
        
        assert len(embeddings) == len(texts)
        
        for embedding in embeddings:
            assert isinstance(embedding, np.ndarray)
            assert embedding.dtype == np.float32
            assert len(embedding) == 384
    
    def test_calculate_similarity(self):
        """Test similarity calculation between embeddings"""
        # Create two similar embeddings
        embedding1 = np.array([1.0, 0.0, 0.0, 0.0] + [0.0] * 380, dtype=np.float32)
        embedding2 = np.array([0.8, 0.6, 0.0, 0.0] + [0.0] * 380, dtype=np.float32)
        embedding3 = np.array([0.0, 0.0, 1.0, 0.0] + [0.0] * 380, dtype=np.float32)
        
        # Calculate similarities
        similarity_12 = self.service.calculate_similarity(embedding1, embedding2)
        similarity_13 = self.service.calculate_similarity(embedding1, embedding3)
        
        # embedding1 and embedding2 should be more similar than embedding1 and embedding3
        assert similarity_12 > similarity_13
        assert 0.0 <= similarity_12 <= 1.0
        assert 0.0 <= similarity_13 <= 1.0
    
    def test_calculate_similarity_identical(self):
        """Test similarity calculation for identical embeddings"""
        embedding = np.array([1.0, 0.0, 0.0] + [0.0] * 381, dtype=np.float32)
        
        similarity = self.service.calculate_similarity(embedding, embedding)
        
        # Identical embeddings should have similarity of 1.0
        assert abs(similarity - 1.0) < 0.01
    
    def test_calculate_similarity_zero_embeddings(self):
        """Test similarity calculation with zero embeddings"""
        zero_embedding = np.zeros(384, dtype=np.float32)
        normal_embedding = np.array([1.0, 0.0] + [0.0] * 382, dtype=np.float32)
        
        similarity = self.service.calculate_similarity(zero_embedding, normal_embedding)
        
        # Zero embedding should have similarity of 0.0
        assert similarity == 0.0
    
    def test_find_most_similar(self):
        """Test finding most similar embeddings"""
        # Create query embedding
        query = np.array([1.0, 0.0, 0.0] + [0.0] * 381, dtype=np.float32)
        
        # Create candidate embeddings
        candidates = [
            np.array([0.9, 0.1, 0.0] + [0.0] * 381, dtype=np.float32),  # Very similar
            np.array([0.0, 1.0, 0.0] + [0.0] * 381, dtype=np.float32),  # Different
            np.array([0.8, 0.2, 0.0] + [0.0] * 381, dtype=np.float32),  # Similar
            np.array([0.0, 0.0, 1.0] + [0.0] * 381, dtype=np.float32),  # Different
        ]
        
        most_similar = self.service.find_most_similar(query, candidates, top_k=2)
        
        assert len(most_similar) == 2
        
        # Results should be sorted by similarity (descending)
        assert most_similar[0][1] >= most_similar[1][1]
        
        # First result should be the most similar (index 0)
        assert most_similar[0][0] == 0
    
    def test_hash_text_consistency(self):
        """Test text hashing consistency"""
        text = "Test text for hashing"
        
        hash1 = self.service._hash_text(text)
        hash2 = self.service._hash_text(text)
        
        # Same text should produce same hash
        assert hash1 == hash2
        
        # Different text should produce different hash
        hash3 = self.service._hash_text("Different text")
        assert hash1 != hash3
    
    def test_get_embedding_dimension(self):
        """Test getting embedding dimension"""
        dimension = self.service.get_embedding_dimension()
        assert dimension == 384
    
    def test_clear_cache(self):
        """Test cache clearing"""
        # Add something to cache
        self.service.cache['test_hash'] = np.array([1.0, 2.0, 3.0])
        
        # Clear cache
        self.service.clear_cache()
        
        # Cache should be empty
        assert len(self.service.cache) == 0
    
    def test_get_cache_stats(self):
        """Test getting cache statistics"""
        # Add some items to cache
        self.service.cache['hash1'] = np.array([1.0, 2.0, 3.0])
        self.service.cache['hash2'] = np.array([4.0, 5.0, 6.0])
        
        stats = self.service.get_cache_stats()
        
        assert 'cached_embeddings' in stats
        assert 'cache_size_mb' in stats
        assert 'model_type' in stats
        assert 'embedding_dimension' in stats
        
        assert stats['cached_embeddings'] == 2
        assert stats['embedding_dimension'] == 384
    
    def test_benchmark_performance(self):
        """Test performance benchmarking"""
        test_texts = [
            "Short text.",
            "Medium length text for testing.",
            "Longer text with more words to process and analyze for benchmarking."
        ]
        
        benchmark = self.service.benchmark_performance(test_texts)
        
        assert 'single_embedding_time' in benchmark
        assert 'batch_embedding_time' in benchmark
        assert 'batch_size' in benchmark
        assert 'avg_time_per_embedding' in benchmark
        assert 'embedding_dimension' in benchmark
        assert 'speedup_factor' in benchmark
        
        assert benchmark['batch_size'] == len(test_texts)
        assert benchmark['embedding_dimension'] == 384
        assert benchmark['single_embedding_time'] >= 0
        assert benchmark['batch_embedding_time'] >= 0
    
    def test_embedding_consistency(self):
        """Test that same text produces consistent embeddings"""
        text = "Consistent embedding test text"
        
        embedding1 = self.service.generate_embedding(text)
        
        # Clear cache to force regeneration
        self.service.cache.clear()
        
        embedding2 = self.service.generate_embedding(text)
        
        # Should be very similar (allowing for small numerical differences)
        similarity = self.service.calculate_similarity(embedding1, embedding2)
        assert similarity > 0.99  # Should be nearly identical
    
    def test_different_texts_different_embeddings(self):
        """Test that different texts produce different embeddings"""
        text1 = "This is the first text."
        text2 = "This is completely different content."
        
        embedding1 = self.service.generate_embedding(text1)
        embedding2 = self.service.generate_embedding(text2)
        
        # Should not be identical
        assert not np.array_equal(embedding1, embedding2)
        
        # Similarity should be less than 1.0
        similarity = self.service.calculate_similarity(embedding1, embedding2)
        assert similarity < 1.0
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_sentence_transformers_initialization(self, mock_st):
        """Test SentenceTransformers model initialization"""
        mock_model = Mock()
        mock_st.return_value = mock_model
        
        service = EmbeddingService()
        service.embedding_config = {'model': 'sentence-transformers/all-MiniLM-L6-v2', 'dimension': 384}
        service._initialize_sentence_transformers('all-MiniLM-L6-v2')
        
        assert service.model == mock_model
        mock_st.assert_called_once_with('all-MiniLM-L6-v2')
    
    @patch('openai.OpenAI')
    def test_openai_initialization(self, mock_openai):
        """Test OpenAI embeddings initialization"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        service = EmbeddingService()
        service._initialize_openai_embeddings()
        
        assert service.model == "openai"
        assert service.openai_client == mock_client
    
    def test_batch_vs_individual_consistency(self):
        """Test that batch processing produces same results as individual processing"""
        texts = [
            "First test text.",
            "Second test text.",
            "Third test text."
        ]
        
        # Generate individually
        individual_embeddings = [self.service.generate_embedding(text) for text in texts]
        
        # Clear cache
        self.service.cache.clear()
        
        # Generate in batch
        batch_embeddings = self.service.generate_embeddings(texts)
        
        # Should be very similar
        for ind_emb, batch_emb in zip(individual_embeddings, batch_embeddings):
            similarity = self.service.calculate_similarity(ind_emb, batch_emb)
            assert similarity > 0.99

if __name__ == "__main__":
    pytest.main([__file__])
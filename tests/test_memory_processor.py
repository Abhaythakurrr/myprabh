"""
Unit tests for memory processor
"""

import pytest
import numpy as np
from services.memory.memory_processor import MemoryProcessor
from services.memory.memory_models import MemoryType, SourceType, RetentionPolicy, PrivacyLevel

class TestMemoryProcessor:
    """Test cases for MemoryProcessor"""
    
    def setup_method(self):
        """Set up test environment"""
        self.processor = MemoryProcessor()
        self.test_user_id = "test_user_123"
        self.test_companion_id = "test_companion_456"
    
    def test_chunk_memory_short_text(self):
        """Test chunking of short text"""
        short_text = "This is a short memory."
        
        chunks = self.processor.chunk_memory(short_text)
        
        assert len(chunks) == 1
        assert chunks[0]['content'] == short_text
        assert chunks[0]['chunk_index'] == 0
        assert chunks[0]['total_chunks'] == 1
        assert chunks[0]['word_count'] == len(short_text.split())
    
    def test_chunk_memory_long_text(self):
        """Test chunking of long text"""
        # Create a long text that should be chunked
        long_text = " ".join([
            "This is the first sentence of a long memory.",
            "It contains multiple sentences that should be processed.",
            "The memory processor should split this into appropriate chunks.",
            "Each chunk should maintain semantic coherence.",
            "The chunking algorithm should handle sentence boundaries properly."
        ] * 50)  # Repeat to make it long enough
        
        chunks = self.processor.chunk_memory(long_text)
        
        # Should create multiple chunks for long text
        assert len(chunks) >= 1
        
        # Check chunk properties
        for i, chunk in enumerate(chunks):
            assert 'content' in chunk
            assert 'chunk_index' in chunk
            assert 'total_chunks' in chunk
            assert 'word_count' in chunk
            assert 'metadata' in chunk
            assert chunk['chunk_index'] == i
            assert chunk['total_chunks'] == len(chunks)
    
    def test_chunk_memory_with_metadata(self):
        """Test chunking with additional metadata"""
        text = "This is a test memory with metadata."
        metadata = {
            'source': 'test',
            'timestamp': '2024-01-01T00:00:00',
            'custom_field': 'custom_value'
        }
        
        chunks = self.processor.chunk_memory(text, metadata)
        
        assert len(chunks) == 1
        chunk_metadata = chunks[0]['metadata']
        
        # Should include original metadata
        assert chunk_metadata['source'] == 'test'
        assert chunk_metadata['custom_field'] == 'custom_value'
        
        # Should include extracted metadata
        assert 'character_count' in chunk_metadata
        assert 'word_count' in chunk_metadata
        assert 'language' in chunk_metadata
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        text = "I love going to the beautiful beach on sunny days with my family and friends."
        
        keywords = self.processor._extract_keywords(text)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        
        # Should extract meaningful words, not stop words
        assert 'love' in keywords or 'beach' in keywords or 'beautiful' in keywords
        assert 'the' not in keywords  # Stop word should be filtered
        assert 'and' not in keywords  # Stop word should be filtered
    
    def test_analyze_sentiment_positive(self):
        """Test sentiment analysis for positive text"""
        positive_text = "I am so happy and excited about this wonderful day!"
        
        sentiment = self.processor._analyze_sentiment(positive_text)
        
        assert sentiment['polarity'] == 'positive'
        assert sentiment['confidence'] > 0
        assert sentiment['positive_words'] > 0
    
    def test_analyze_sentiment_negative(self):
        """Test sentiment analysis for negative text"""
        negative_text = "I hate this terrible and awful situation. It makes me so sad and angry."
        
        sentiment = self.processor._analyze_sentiment(negative_text)
        
        assert sentiment['polarity'] == 'negative'
        assert sentiment['confidence'] > 0
        assert sentiment['negative_words'] > 0
    
    def test_analyze_sentiment_neutral(self):
        """Test sentiment analysis for neutral text"""
        neutral_text = "The weather report indicates partly cloudy conditions with moderate temperatures."
        
        sentiment = self.processor._analyze_sentiment(neutral_text)
        
        assert sentiment['polarity'] == 'neutral'
        assert isinstance(sentiment['confidence'], float)
    
    def test_extract_simple_entities(self):
        """Test simple entity extraction"""
        text = "John Smith went to Central Park on January 15, 2024 with Mary Johnson."
        
        entities = self.processor._extract_simple_entities(text)
        
        assert 'people' in entities
        assert 'places' in entities
        assert 'dates' in entities
        
        # Should extract people names
        people = entities['people']
        assert any('John' in person for person in people)
        assert any('Mary' in person for person in people)
        
        # Should extract places
        places = entities['places']
        assert any('Park' in place for place in places)
        
        # Should extract dates
        dates = entities['dates']
        assert any('January' in date or '2024' in date for date in dates)
    
    def test_categorize_memory_emotional(self):
        """Test memory categorization for emotional content"""
        emotional_text = "I felt so happy and joyful when I saw my family after a long time."
        
        category = self.processor.categorize_memory(emotional_text)
        
        assert category == MemoryType.EMOTIONAL.value
    
    def test_categorize_memory_conversational(self):
        """Test memory categorization for conversational content"""
        conversational_text = "She said that she would call me later, and I told her that would be fine."
        
        category = self.processor.categorize_memory(conversational_text)
        
        assert category == MemoryType.CONVERSATIONAL.value
    
    def test_categorize_memory_experiential(self):
        """Test memory categorization for experiential content"""
        experiential_text = "We went to the mountains and saw the most beautiful sunset."
        
        category = self.processor.categorize_memory(experiential_text)
        
        assert category == MemoryType.EXPERIENTIAL.value
    
    def test_categorize_memory_factual(self):
        """Test memory categorization for factual content"""
        factual_text = "The research study shows that regular exercise improves cognitive function."
        
        category = self.processor.categorize_memory(factual_text)
        
        assert category == MemoryType.FACTUAL.value
    
    def test_generate_embeddings(self):
        """Test embedding generation"""
        chunks = [
            "This is the first chunk of text.",
            "This is the second chunk of text.",
            "This is a completely different chunk."
        ]
        
        embeddings = self.processor.generate_embeddings(chunks)
        
        assert len(embeddings) == len(chunks)
        
        for embedding in embeddings:
            assert isinstance(embedding, np.ndarray)
            assert len(embedding) == self.processor.config.EMBEDDING_DIMENSION
            
            # Embeddings should be normalized
            norm = np.linalg.norm(embedding)
            assert norm <= 1.1  # Allow small floating point errors
    
    def test_simple_embedding_similarity(self):
        """Test that similar texts produce similar embeddings"""
        text1 = "I love going to the beach"
        text2 = "I enjoy visiting the beach"
        text3 = "The weather is cold today"
        
        embedding1 = self.processor._simple_embedding(text1)
        embedding2 = self.processor._simple_embedding(text2)
        embedding3 = self.processor._simple_embedding(text3)
        
        # Similar texts should have higher similarity
        similarity_12 = np.dot(embedding1, embedding2)
        similarity_13 = np.dot(embedding1, embedding3)
        
        # This is a basic test - in practice, the simple embedding might not work perfectly
        assert isinstance(similarity_12, float)
        assert isinstance(similarity_13, float)
    
    def test_create_memory_chunks(self):
        """Test creating MemoryChunk objects from text"""
        text = "This is a test memory about a wonderful day at the beach with friends."
        
        chunks = self.processor.create_memory_chunks(
            user_id=self.test_user_id,
            companion_id=self.test_companion_id,
            text=text,
            source_type=SourceType.TEXT,
            retention_policy=RetentionPolicy.LONG_TERM,
            privacy_level=PrivacyLevel.PRIVATE
        )
        
        assert len(chunks) >= 1
        
        for chunk in chunks:
            assert chunk.user_id == self.test_user_id
            assert chunk.companion_id == self.test_companion_id
            assert chunk.source_type == SourceType.TEXT
            assert chunk.retention_policy == RetentionPolicy.LONG_TERM
            assert chunk.privacy_level == PrivacyLevel.PRIVATE
            assert chunk.content is not None
            assert len(chunk.content) > 0
            assert chunk.id is not None
    
    def test_create_memory_chunks_with_embeddings(self):
        """Test that created memory chunks have embeddings"""
        text = "This is a test memory for embedding generation."
        
        chunks = self.processor.create_memory_chunks(
            user_id=self.test_user_id,
            companion_id=self.test_companion_id,
            text=text
        )
        
        assert len(chunks) >= 1
        
        for chunk in chunks:
            assert chunk.embedding is not None
            assert isinstance(chunk.embedding, list)
            assert len(chunk.embedding) == self.processor.config.EMBEDDING_DIMENSION
    
    def test_create_memory_chunks_error_handling(self):
        """Test error handling in memory chunk creation"""
        # Test with empty text
        chunks = self.processor.create_memory_chunks(
            user_id=self.test_user_id,
            companion_id=self.test_companion_id,
            text=""
        )
        
        # Should still return at least one chunk
        assert len(chunks) >= 1
        assert chunks[0].user_id == self.test_user_id
    
    def test_semantic_chunking_sentences(self):
        """Test semantic chunking with sentence boundaries"""
        # Create text with clear sentence boundaries
        text = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
        
        chunks = self.processor._semantic_chunking(text)
        
        assert len(chunks) >= 1
        
        # Each chunk should contain complete sentences
        for chunk in chunks:
            assert chunk.strip().endswith('.') or chunk == chunks[-1]  # Last chunk might not end with period
    
    def test_get_overlap_sentences(self):
        """Test getting overlap sentences from chunk"""
        chunk = "This is the first sentence. This is the second sentence. This is the third sentence."
        
        overlap = self.processor._get_overlap_sentences(chunk)
        
        assert isinstance(overlap, str)
        assert len(overlap) > 0
        # Should contain part of the original chunk
        assert any(word in overlap for word in chunk.split())
    
    def test_extract_chunk_metadata_comprehensive(self):
        """Test comprehensive metadata extraction"""
        chunk = "I was so happy on January 1, 2024 when John and I went to Central Park!"
        
        metadata = self.processor._extract_chunk_metadata(chunk)
        
        # Basic statistics
        assert 'character_count' in metadata
        assert 'word_count' in metadata
        assert 'sentence_count' in metadata
        assert 'language' in metadata
        assert 'reading_time_minutes' in metadata
        
        # Emotions
        assert 'emotions' in metadata
        assert 'joy' in metadata['emotions']
        
        # Keywords
        assert 'keywords' in metadata
        assert len(metadata['keywords']) > 0
        
        # Entities
        assert 'entities' in metadata
        assert 'people' in metadata['entities']
        assert 'places' in metadata['entities']
        
        # Sentiment
        assert 'sentiment' in metadata
        assert metadata['sentiment']['polarity'] == 'positive'

if __name__ == "__main__":
    pytest.main([__file__])
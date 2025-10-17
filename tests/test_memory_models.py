"""
Unit tests for memory models
"""

import pytest
from datetime import datetime, timedelta
from services.memory.memory_models import (
    MemoryChunk, PersonalizationProfile, MemoryUploadSession,
    MemoryType, SourceType, RetentionPolicy, PrivacyLevel
)
from utils.memory_utils import generate_memory_id, generate_session_id

class TestMemoryChunk:
    """Test cases for MemoryChunk model"""
    
    def test_memory_chunk_creation(self):
        """Test basic memory chunk creation"""
        chunk = MemoryChunk(
            id=generate_memory_id(),
            user_id="user123",
            companion_id="companion456",
            content="This is a test memory about a happy day at the beach."
        )
        
        assert chunk.id is not None
        assert chunk.user_id == "user123"
        assert chunk.companion_id == "companion456"
        assert chunk.content == "This is a test memory about a happy day at the beach."
        assert chunk.memory_type == MemoryType.FACTUAL
        assert chunk.source_type == SourceType.TEXT
        assert chunk.privacy_level == PrivacyLevel.PRIVATE
        assert isinstance(chunk.timestamp, datetime)
    
    def test_memory_chunk_validation_success(self):
        """Test successful memory chunk validation"""
        chunk = MemoryChunk(
            id=generate_memory_id(),
            user_id="user123",
            companion_id="companion456",
            content="Valid content for testing memory chunk validation."
        )
        
        assert chunk.validate() == True
    
    def test_memory_chunk_validation_failures(self):
        """Test memory chunk validation failures"""
        # Test empty ID
        with pytest.raises(ValueError, match="Memory ID is required"):
            MemoryChunk(
                id="",
                user_id="user123",
                companion_id="companion456",
                content="Test content"
            )
        
        # Test empty user ID
        with pytest.raises(ValueError, match="User ID is required"):
            MemoryChunk(
                id=generate_memory_id(),
                user_id="",
                companion_id="companion456",
                content="Test content"
            )
        
        # Test empty content
        with pytest.raises(ValueError, match="Content cannot be empty"):
            MemoryChunk(
                id=generate_memory_id(),
                user_id="user123",
                companion_id="companion456",
                content=""
            )
        
        # Test content too short
        with pytest.raises(ValueError, match="Content must be at least 10 characters"):
            MemoryChunk(
                id=generate_memory_id(),
                user_id="user123",
                companion_id="companion456",
                content="Short"
            )
        
        # Test content too long
        long_content = "x" * 10001
        with pytest.raises(ValueError, match="Content exceeds maximum length"):
            MemoryChunk(
                id=generate_memory_id(),
                user_id="user123",
                companion_id="companion456",
                content=long_content
            )
    
    def test_memory_chunk_content_processing(self):
        """Test automatic content processing"""
        chunk = MemoryChunk(
            id=generate_memory_id(),
            user_id="user123",
            companion_id="companion456",
            content="I was so happy and excited today! It was an amazing day at the beach with friends."
        )
        
        # Check that content hash is generated
        assert chunk.content_hash is not None
        assert len(chunk.content_hash) == 64  # SHA256 hash length
        
        # Check emotion extraction
        assert 'joy' in chunk.emotions  # Should detect happiness
        
        # Check language detection
        assert chunk.language == 'en'
        
        # Check reading time estimation
        assert chunk.reading_time_minutes >= 1
        
        # Check keywords extraction
        assert len(chunk.keywords) > 0
        assert 'happy' in chunk.keywords or 'excited' in chunk.keywords
    
    def test_memory_chunk_similarity(self):
        """Test memory chunk similarity detection"""
        content1 = "I love going to the beach on sunny days"
        content2 = "I love going to the beach on sunny days"  # Identical
        content3 = "Beach days are wonderful when it's sunny"  # Similar
        content4 = "I prefer mountains over beaches"  # Different
        
        chunk1 = MemoryChunk(
            id=generate_memory_id(),
            user_id="user123",
            companion_id="companion456",
            content=content1
        )
        
        chunk2 = MemoryChunk(
            id=generate_memory_id(),
            user_id="user123",
            companion_id="companion456",
            content=content2
        )
        
        chunk3 = MemoryChunk(
            id=generate_memory_id(),
            user_id="user123",
            companion_id="companion456",
            content=content3
        )
        
        chunk4 = MemoryChunk(
            id=generate_memory_id(),
            user_id="user123",
            companion_id="companion456",
            content=content4
        )
        
        # Identical content should be similar
        assert chunk1.is_similar_to(chunk2) == True
        
        # Different content should not be similar
        assert chunk1.is_similar_to(chunk4) == False
    
    def test_memory_chunk_retention(self):
        """Test memory retention policies"""
        # Short-term memory (30 days old)
        old_timestamp = datetime.now() - timedelta(days=35)
        short_term_chunk = MemoryChunk(
            id=generate_memory_id(),
            user_id="user123",
            companion_id="companion456",
            content="Short term memory content",
            retention_policy=RetentionPolicy.SHORT_TERM,
            timestamp=old_timestamp
        )
        
        assert short_term_chunk.should_be_retained() == False
        
        # Long-term memory should always be retained
        long_term_chunk = MemoryChunk(
            id=generate_memory_id(),
            user_id="user123",
            companion_id="companion456",
            content="Long term memory content",
            retention_policy=RetentionPolicy.LONG_TERM,
            timestamp=old_timestamp
        )
        
        assert long_term_chunk.should_be_retained() == True
    
    def test_memory_chunk_serialization(self):
        """Test memory chunk to/from dict conversion"""
        original_chunk = MemoryChunk(
            id=generate_memory_id(),
            user_id="user123",
            companion_id="companion456",
            content="Test serialization content",
            memory_type=MemoryType.EMOTIONAL,
            source_type=SourceType.VOICE
        )
        
        # Convert to dict
        chunk_dict = original_chunk.to_dict()
        
        # Verify dict structure
        assert chunk_dict['id'] == original_chunk.id
        assert chunk_dict['user_id'] == original_chunk.user_id
        assert chunk_dict['memory_type'] == 'emotional'
        assert chunk_dict['source_type'] == 'voice'
        
        # Convert back from dict
        restored_chunk = MemoryChunk.from_dict(chunk_dict)
        
        # Verify restoration
        assert restored_chunk.id == original_chunk.id
        assert restored_chunk.user_id == original_chunk.user_id
        assert restored_chunk.memory_type == MemoryType.EMOTIONAL
        assert restored_chunk.source_type == SourceType.VOICE

class TestPersonalizationProfile:
    """Test cases for PersonalizationProfile model"""
    
    def test_personalization_profile_creation(self):
        """Test basic personalization profile creation"""
        profile = PersonalizationProfile(
            user_id="user123",
            companion_id="companion456"
        )
        
        assert profile.user_id == "user123"
        assert profile.companion_id == "companion456"
        assert profile.personalization_level == "basic"
        assert isinstance(profile.personality_traits, dict)
        assert isinstance(profile.last_updated, datetime)
    
    def test_personalization_profile_validation(self):
        """Test personalization profile validation"""
        # Valid profile
        profile = PersonalizationProfile(
            user_id="user123",
            companion_id="companion456"
        )
        assert profile.validate() == True
        
        # Invalid personalization level
        with pytest.raises(ValueError, match="Invalid personalization level"):
            PersonalizationProfile(
                user_id="user123",
                companion_id="companion456",
                personalization_level="invalid"
            )
    
    def test_personality_trait_updates(self):
        """Test personality trait updates"""
        profile = PersonalizationProfile(
            user_id="user123",
            companion_id="companion456"
        )
        
        # Update trait
        profile.update_personality_trait("friendliness", 0.8)
        assert profile.personality_traits["friendliness"] == 0.8
        
        # Test invalid trait value
        with pytest.raises(ValueError, match="Personality trait values must be between 0.0 and 1.0"):
            profile.update_personality_trait("invalid_trait", 1.5)
    
    def test_dominant_traits(self):
        """Test getting dominant personality traits"""
        profile = PersonalizationProfile(
            user_id="user123",
            companion_id="companion456"
        )
        
        # Add some traits
        profile.personality_traits = {
            "friendliness": 0.9,
            "creativity": 0.7,
            "analytical": 0.5,
            "empathy": 0.8
        }
        
        dominant_traits = profile.get_dominant_traits(top_n=2)
        assert len(dominant_traits) == 2
        assert dominant_traits[0][0] == "friendliness"
        assert dominant_traits[0][1] == 0.9

class TestMemoryUploadSession:
    """Test cases for MemoryUploadSession model"""
    
    def test_upload_session_creation(self):
        """Test basic upload session creation"""
        session = MemoryUploadSession(
            session_id=generate_session_id(),
            user_id="user123",
            companion_id="companion456"
        )
        
        assert session.session_id is not None
        assert session.user_id == "user123"
        assert session.companion_id == "companion456"
        assert session.processing_status == "pending"
        assert len(session.uploaded_files) == 0
    
    def test_upload_session_file_management(self):
        """Test file management in upload session"""
        session = MemoryUploadSession(
            session_id=generate_session_id(),
            user_id="user123",
            companion_id="companion456"
        )
        
        # Add file
        session.add_file("test.txt", "text/plain", 1024)
        assert len(session.uploaded_files) == 1
        assert session.uploaded_files[0]["filename"] == "test.txt"
        
        # Update file status
        session.update_file_status("test.txt", "completed", chunks_created=5)
        assert session.uploaded_files[0]["status"] == "completed"
        assert session.uploaded_files[0]["chunks_created"] == 5
    
    def test_upload_session_completion(self):
        """Test upload session completion"""
        session = MemoryUploadSession(
            session_id=generate_session_id(),
            user_id="user123",
            companion_id="companion456"
        )
        
        # Mark as completed
        session.mark_completed()
        assert session.processing_status == "completed"
        assert session.completed_at is not None
        
        # Test failure marking
        session2 = MemoryUploadSession(
            session_id=generate_session_id(),
            user_id="user123",
            companion_id="companion456"
        )
        
        session2.mark_failed("Test error")
        assert session2.processing_status == "failed"
        assert "Test error" in session2.processing_errors
    
    def test_upload_session_summary(self):
        """Test upload session processing summary"""
        session = MemoryUploadSession(
            session_id=generate_session_id(),
            user_id="user123",
            companion_id="companion456"
        )
        
        # Add some files
        session.add_file("file1.txt", "text/plain", 1024)
        session.add_file("file2.txt", "text/plain", 2048)
        
        # Update statuses
        session.update_file_status("file1.txt", "completed", chunks_created=3)
        session.update_file_status("file2.txt", "failed", errors=["Processing error"])
        
        session.total_chunks_created = 3
        
        summary = session.get_processing_summary()
        assert summary["total_files"] == 2
        assert summary["completed_files"] == 1
        assert summary["failed_files"] == 1
        assert summary["total_chunks"] == 3

if __name__ == "__main__":
    pytest.main([__file__])
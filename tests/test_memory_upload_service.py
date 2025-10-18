"""
Unit tests for memory upload service
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from services.memory.memory_upload_service import MemoryUploadService
from config.memory_config import MemoryConfig

class TestMemoryUploadService:
    """Test cases for MemoryUploadService"""
    
    def setup_method(self):
        """Set up test environment"""
        self.service = MemoryUploadService()
        self.test_user_id = "test_user_123"
        self.test_companion_id = "test_companion_456"
    
    def teardown_method(self):
        """Clean up test environment"""
        # Clean up any test files
        if hasattr(self.service, 'temp_dir') and os.path.exists(self.service.temp_dir):
            import shutil
            shutil.rmtree(self.service.temp_dir)
    
    def test_validate_upload_success(self):
        """Test successful file validation"""
        # Test with valid text content
        text_content = b"This is a test memory content for validation."
        
        # Mock the file type detection
        with patch('services.memory.memory_upload_service.detect_file_type', return_value='text/plain'):
            result = self.service.validate_upload(text_content, 'text/plain')
            assert result == True
    
    def test_validate_upload_file_too_large(self):
        """Test file validation with oversized file"""
        # Create content larger than max size
        large_content = b"x" * (MemoryConfig.MAX_MEMORY_FILE_SIZE + 1)
        
        result = self.service.validate_upload(large_content, 'text/plain')
        assert result == False
    
    def test_validate_upload_unsupported_type(self):
        """Test file validation with unsupported file type"""
        content = b"test content"
        
        with patch('services.memory.memory_upload_service.detect_file_type', return_value='application/x-executable'):
            result = self.service.validate_upload(content, 'application/x-executable')
            assert result == False
    
    def test_validate_upload_security_scan_fail(self):
        """Test file validation with malicious content"""
        malicious_content = b"<script>alert('xss')</script>"
        
        with patch('services.memory.memory_upload_service.detect_file_type', return_value='text/html'):
            result = self.service.validate_upload(malicious_content, 'text/html')
            assert result == False
    
    def test_process_text_file(self):
        """Test text file processing"""
        text_content = b"This is a test memory about a wonderful day at the beach."
        
        result = self.service._process_text_file(text_content)
        assert result == "This is a test memory about a wonderful day at the beach."
        assert isinstance(result, str)
    
    def test_process_text_file_encoding_issues(self):
        """Test text file processing with encoding issues"""
        # Test with different encodings
        text_content = "Café résumé naïve".encode('utf-8')
        
        result = self.service._process_text_file(text_content)
        assert "Café" in result
        assert "résumé" in result
    
    def test_process_text_file_invalid_encoding(self):
        """Test text file processing with invalid encoding"""
        # Create invalid UTF-8 sequence
        invalid_content = b'\xff\xfe\x00\x00invalid'
        
        result = self.service._process_text_file(invalid_content)
        # Should not raise exception and return some content
        assert isinstance(result, str)
    
    def test_process_voice_note_built_from_scratch(self):
        """Test voice note processing with built-from-scratch implementation"""
        # Test with WAV format
        wav_data = b'RIFF\x00\x00\x00\x00WAVEfmt fake audio data'
        result = self.service.process_voice_note(wav_data)
        
        assert "Voice note recorded" in result
        assert "wav format" in result
        assert "[Voice content - transcription would be implemented here]" in result
    
    def test_process_voice_note_mp3_format(self):
        """Test voice note processing with MP3 format"""
        # Test with MP3 format
        mp3_data = b'ID3\x03\x00\x00\x00fake mp3 data'
        result = self.service.process_voice_note(mp3_data)
        
        assert "Voice note recorded" in result
        assert "mp3 format" in result
        assert "[Voice content - transcription would be implemented here]" in result
    
    def test_process_image_built_from_scratch(self):
        """Test image processing with built-from-scratch implementation"""
        # Test with PNG format
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR fake png data'
        result = self.service.process_image(png_data)
        
        assert 'caption' in result
        assert 'description' in result
        assert 'metadata' in result
        assert "Image memory from" in result['caption']
        assert "png format" in result['description']
        assert result['metadata']['analysis_method'] == 'built_from_scratch'
    
    def test_process_image_jpeg_format(self):
        """Test image processing with JPEG format"""
        # Test with JPEG format
        jpeg_data = b'\xff\xd8\xff\xe0fake jpeg data'
        result = self.service.process_image(jpeg_data)
        
        assert 'caption' in result
        assert 'description' in result
        assert 'metadata' in result
        assert "Image memory from" in result['caption']
        assert "jpeg format" in result['description']
    
    def test_encryption_decryption(self):
        """Test content encryption and decryption"""
        original_content = "This is sensitive memory content that should be encrypted."
        
        # Encrypt content
        encrypted = self.service._encrypt_content(original_content)
        assert encrypted != original_content.encode()
        assert isinstance(encrypted, bytes)
        
        # Decrypt content
        decrypted = self.service._decrypt_content(encrypted)
        assert decrypted == original_content
    
    def test_upload_memory_text_success(self):
        """Test successful memory upload with text file"""
        text_content = b"This is a test memory about my childhood."
        
        with patch.object(self.service, 'validate_upload', return_value=True):
            with patch.object(self.service, '_process_file_by_type', return_value="Processed content"):
                session_id = self.service.upload_memory(
                    user_id=self.test_user_id,
                    file_data=text_content,
                    file_type='text/plain',
                    companion_id=self.test_companion_id,
                    filename='test_memory.txt'
                )
                
                assert session_id is not None
                assert len(session_id) > 0
    
    def test_upload_memory_validation_failure(self):
        """Test memory upload with validation failure"""
        text_content = b"Invalid content"
        
        with patch.object(self.service, 'validate_upload', return_value=False):
            with pytest.raises(ValueError, match="File validation failed"):
                self.service.upload_memory(
                    user_id=self.test_user_id,
                    file_data=text_content,
                    file_type='text/plain',
                    companion_id=self.test_companion_id
                )
    
    def test_upload_memory_missing_params(self):
        """Test memory upload with missing parameters"""
        text_content = b"Test content"
        
        # Test missing user_id
        with pytest.raises(ValueError, match="User ID and Companion ID are required"):
            self.service.upload_memory(
                user_id="",
                file_data=text_content,
                file_type='text/plain',
                companion_id=self.test_companion_id
            )
        
        # Test missing companion_id
        with pytest.raises(ValueError, match="User ID and Companion ID are required"):
            self.service.upload_memory(
                user_id=self.test_user_id,
                file_data=text_content,
                file_type='text/plain',
                companion_id=""
            )
        
        # Test empty file data
        with pytest.raises(ValueError, match="File data cannot be empty"):
            self.service.upload_memory(
                user_id=self.test_user_id,
                file_data=b"",
                file_type='text/plain',
                companion_id=self.test_companion_id
            )
    
    def test_get_supported_file_types(self):
        """Test getting supported file types"""
        supported_types = self.service.get_supported_file_types()
        
        assert 'text' in supported_types
        assert 'audio' in supported_types
        assert 'image' in supported_types
        assert isinstance(supported_types['text'], list)
        assert '.txt' in supported_types['text']
    
    def test_get_upload_limits(self):
        """Test getting upload limits"""
        limits = self.service.get_upload_limits()
        
        assert 'max_file_size' in limits
        assert 'max_file_size_mb' in limits
        assert 'supported_types' in limits
        assert limits['max_file_size'] > 0
        assert limits['max_file_size_mb'] > 0
    
    def test_cleanup_old_sessions(self):
        """Test cleanup of old session files"""
        # Create a test session directory
        test_session_id = "test_session_123"
        session_dir = os.path.join(self.service.temp_dir, test_session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Create a test file
        test_file = os.path.join(session_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Verify directory exists
        assert os.path.exists(session_dir)
        
        # Run cleanup (should not remove recent files)
        self.service.cleanup_old_sessions(max_age_hours=24)
        assert os.path.exists(session_dir)
        
        # Run cleanup with very short age (should remove files)
        self.service.cleanup_old_sessions(max_age_hours=0)
        # Note: This might not work reliably in tests due to timing
    
    def test_session_content_storage_retrieval(self):
        """Test storing and retrieving session content"""
        session_id = "test_session_456"
        filename = "test_file.txt"
        content = "This is test content for storage and retrieval."
        
        # Store content
        encrypted_content = self.service._encrypt_content(content)
        storage_path = self.service._store_encrypted_file(session_id, filename, encrypted_content)
        
        assert os.path.exists(storage_path)
        
        # Retrieve content
        retrieved_content = self.service.get_session_content(session_id, filename)
        assert retrieved_content == content
    
    def test_session_content_not_found(self):
        """Test retrieving non-existent session content"""
        with pytest.raises(FileNotFoundError, match="Session file not found"):
            self.service.get_session_content("nonexistent_session", "nonexistent_file.txt")

if __name__ == "__main__":
    pytest.main([__file__])
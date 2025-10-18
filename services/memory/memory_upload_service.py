"""
Memory Upload Service for My Prabh
Handles secure file upload and validation for memory processing
Built from scratch without third-party API dependencies
"""

import os
import tempfile
import shutil
import base64
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import mimetypes
import hashlib

from .interfaces import MemoryUploadInterface
from .memory_models import MemoryUploadSession, SourceType
from config.memory_config import MemoryConfig
from utils.memory_utils import (
    generate_session_id, detect_file_type, validate_file_size,
    sanitize_filename, clean_text
)

class MemoryUploadService(MemoryUploadInterface):
    """Service for handling memory file uploads - built from scratch"""
    
    def __init__(self):
        self.config = MemoryConfig()
        self.temp_dir = tempfile.mkdtemp(prefix="myprabh_memory_")
        self.encryption_key = self._get_or_create_encryption_key()
        
        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def _get_or_create_encryption_key(self) -> str:
        """Get or create encryption key for memory data"""
        key = self.config.ENCRYPTION_KEY
        if key:
            return key
        else:
            # Generate a simple key (in production, use proper key management)
            return hashlib.sha256(b'myprabh_memory_key').hexdigest()[:32]
    
    def upload_memory(self, user_id: str, file_data: bytes, file_type: str, 
                     companion_id: str, filename: str = None, 
                     metadata: Dict[str, Any] = None) -> str:
        """Upload and process memory file"""
        try:
            # Validate inputs
            if not user_id or not companion_id:
                raise ValueError("User ID and Companion ID are required")
            
            if not file_data:
                raise ValueError("File data cannot be empty")
            
            # Validate file
            if not self.validate_upload(file_data, file_type):
                raise ValueError("File validation failed")
            
            # Create upload session
            session_id = generate_session_id()
            session = MemoryUploadSession(
                session_id=session_id,
                user_id=user_id,
                companion_id=companion_id,
                metadata=metadata or {}
            )
            
            # Sanitize filename
            safe_filename = sanitize_filename(filename) if filename else f"upload_{session_id}"
            
            # Add file to session
            session.add_file(safe_filename, file_type, len(file_data))
            
            # Process file based on type
            processed_content = self._process_file_by_type(file_data, file_type, safe_filename)
            
            if processed_content:
                # Encrypt and store processed content
                encrypted_content = self._encrypt_content(processed_content)
                storage_path = self._store_encrypted_file(session_id, safe_filename, encrypted_content)
                
                # Update session
                session.update_file_status(safe_filename, "completed", chunks_created=1)
                session.mark_completed()
                
                # Store session metadata
                session.metadata['storage_path'] = storage_path
                session.metadata['content_preview'] = processed_content[:200] + "..." if len(processed_content) > 200 else processed_content
                
                return session_id
            else:
                session.mark_failed("Failed to process file content")
                raise ValueError("Failed to process file content")
                
        except Exception as e:
            # Clean up on error
            self._cleanup_session_files(session_id if 'session_id' in locals() else None)
            raise e
    
    def validate_upload(self, file_data: bytes, file_type: str) -> bool:
        """Validate uploaded file"""
        try:
            # Check file size
            if not validate_file_size(file_data, self.config.MAX_MEMORY_FILE_SIZE):
                return False
            
            # Detect actual file type
            detected_type = detect_file_type(file_data)
            
            # Check if file type is supported
            if not self._is_supported_file_type(detected_type):
                return False
            
            # Additional security checks
            if not self._security_scan_file(file_data):
                return False
            
            return True
            
        except Exception as e:
            print(f"File validation error: {e}")
            return False
    
    def _is_supported_file_type(self, file_type: str) -> bool:
        """Check if file type is supported"""
        supported_types = (
            self.config.SUPPORTED_TEXT_TYPES +
            self.config.SUPPORTED_AUDIO_TYPES +
            self.config.SUPPORTED_IMAGE_TYPES
        )
        
        # Convert MIME type to extension for comparison
        extension = mimetypes.guess_extension(file_type)
        return extension in supported_types if extension else False
    
    def _security_scan_file(self, file_data: bytes) -> bool:
        """Perform basic security scan on file"""
        # Check for malicious patterns (basic implementation)
        malicious_patterns = [
            b'<script',
            b'javascript:',
            b'<?php',
            b'<%',
            b'exec(',
            b'system(',
            b'shell_exec('
        ]
        
        file_data_lower = file_data.lower()
        for pattern in malicious_patterns:
            if pattern in file_data_lower:
                return False
        
        return True
    
    def _process_file_by_type(self, file_data: bytes, file_type: str, filename: str) -> str:
        """Process file based on its type"""
        try:
            if file_type.startswith('text/') or file_type == 'application/json':
                return self._process_text_file(file_data)
            elif file_type.startswith('audio/'):
                return self.process_voice_note(file_data)
            elif file_type.startswith('image/'):
                image_info = self.process_image(file_data)
                return image_info.get('caption', '') + '\n' + image_info.get('description', '')
            else:
                # Try to process as text
                return self._process_text_file(file_data)
                
        except Exception as e:
            print(f"Error processing file {filename}: {e}")
            return ""
    
    def _process_text_file(self, file_data: bytes) -> str:
        """Process text file content"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    text = file_data.decode(encoding)
                    return clean_text(text)
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, use utf-8 with error handling
            return file_data.decode('utf-8', errors='replace')
            
        except Exception as e:
            print(f"Error processing text file: {e}")
            return ""
    
    def process_voice_note(self, audio_data: bytes) -> str:
        """Process voice note to text - built from scratch"""
        try:
            # Basic audio file analysis
            audio_info = self._analyze_audio_file(audio_data)
            
            # Generate descriptive text based on audio properties
            description = f"Voice note recorded"
            
            if audio_info.get('duration'):
                description += f" (Duration: {audio_info['duration']} seconds)"
            
            if audio_info.get('format'):
                description += f" in {audio_info['format']} format"
            
            # Add timestamp
            description += f" at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # For now, return a placeholder that indicates voice content
            return f"{description}. [Voice content - transcription would be implemented here]"
                
        except Exception as e:
            print(f"Voice processing error: {e}")
            return "[Voice note processing failed]"
    

    
    def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """Process image and extract information - built from scratch"""
        try:
            # Basic image analysis
            image_info = self._analyze_image_file(image_data)
            
            # Generate basic description
            description = f"Image file uploaded"
            
            if image_info.get('format'):
                description += f" in {image_info['format']} format"
            
            if image_info.get('size'):
                description += f" ({image_info['size']} bytes)"
            
            # Add timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            description += f" at {timestamp}"
            
            # Basic caption based on file properties
            caption = f"Image memory from {timestamp}"
            
            return {
                'caption': caption,
                'description': description,
                'metadata': {
                    'size': len(image_data),
                    'format': image_info.get('format', 'unknown'),
                    'processed_at': datetime.now().isoformat(),
                    'analysis_method': 'built_from_scratch'
                }
            }
                
        except Exception as e:
            print(f"Image processing error: {e}")
            return {
                'caption': '[Image processing failed]',
                'description': 'Failed to process image',
                'metadata': {'error': str(e)}
            }
    

    
    def _encrypt_content(self, content: str) -> bytes:
        """Encrypt content for secure storage - simple XOR encryption"""
        try:
            # Simple XOR encryption with the key
            key = self.encryption_key.encode('utf-8')
            content_bytes = content.encode('utf-8')
            
            encrypted = bytearray()
            for i, byte in enumerate(content_bytes):
                encrypted.append(byte ^ key[i % len(key)])
            
            # Base64 encode for storage
            return base64.b64encode(bytes(encrypted))
        except Exception as e:
            print(f"Encryption error: {e}")
            raise e
    
    def _decrypt_content(self, encrypted_content: bytes) -> str:
        """Decrypt content from storage - simple XOR decryption"""
        try:
            # Base64 decode first
            encrypted_bytes = base64.b64decode(encrypted_content)
            
            # Simple XOR decryption with the key
            key = self.encryption_key.encode('utf-8')
            
            decrypted = bytearray()
            for i, byte in enumerate(encrypted_bytes):
                decrypted.append(byte ^ key[i % len(key)])
            
            return bytes(decrypted).decode('utf-8')
        except Exception as e:
            print(f"Decryption error: {e}")
            raise e
    
    def _store_encrypted_file(self, session_id: str, filename: str, encrypted_content: bytes) -> str:
        """Store encrypted file content"""
        try:
            # Create session directory
            session_dir = os.path.join(self.temp_dir, session_id)
            os.makedirs(session_dir, exist_ok=True)
            
            # Store encrypted content
            file_path = os.path.join(session_dir, f"{filename}.encrypted")
            with open(file_path, 'wb') as f:
                f.write(encrypted_content)
            
            return file_path
            
        except Exception as e:
            print(f"File storage error: {e}")
            raise e
    
    def get_session_content(self, session_id: str, filename: str) -> str:
        """Retrieve and decrypt session file content"""
        try:
            file_path = os.path.join(self.temp_dir, session_id, f"{filename}.encrypted")
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Session file not found: {filename}")
            
            with open(file_path, 'rb') as f:
                encrypted_content = f.read()
            
            return self._decrypt_content(encrypted_content)
            
        except Exception as e:
            print(f"Content retrieval error: {e}")
            raise e
    
    def _analyze_audio_file(self, audio_data: bytes) -> Dict[str, Any]:
        """Analyze audio file properties - built from scratch"""
        try:
            info = {
                'size': len(audio_data),
                'format': 'unknown'
            }
            
            # Basic format detection based on file headers
            if audio_data.startswith(b'ID3') or audio_data[6:10] == b'ftyp':
                info['format'] = 'mp3'
            elif audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:12]:
                info['format'] = 'wav'
            elif audio_data.startswith(b'OggS'):
                info['format'] = 'ogg'
            elif audio_data.startswith(b'fLaC'):
                info['format'] = 'flac'
            
            # Estimate duration based on file size (very rough)
            # Assume average bitrate of 128kbps for estimation
            estimated_duration = (len(audio_data) * 8) / (128 * 1000)  # seconds
            info['duration'] = round(estimated_duration, 1)
            
            return info
        except Exception as e:
            print(f"Audio analysis error: {e}")
            return {'size': len(audio_data), 'format': 'unknown'}
    
    def _analyze_image_file(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze image file properties - built from scratch"""
        try:
            info = {
                'size': len(image_data),
                'format': 'unknown'
            }
            
            # Basic format detection based on file headers
            if image_data.startswith(b'\x89PNG'):
                info['format'] = 'png'
            elif image_data.startswith(b'\xff\xd8\xff'):
                info['format'] = 'jpeg'
            elif image_data.startswith(b'GIF8'):
                info['format'] = 'gif'
            elif image_data.startswith(b'RIFF') and b'WEBP' in image_data[:12]:
                info['format'] = 'webp'
            elif image_data.startswith(b'BM'):
                info['format'] = 'bmp'
            
            return info
        except Exception as e:
            print(f"Image analysis error: {e}")
            return {'size': len(image_data), 'format': 'unknown'}
    
    def _cleanup_session_files(self, session_id: str):
        """Clean up temporary session files"""
        if session_id:
            try:
                session_dir = os.path.join(self.temp_dir, session_id)
                if os.path.exists(session_dir):
                    shutil.rmtree(session_dir)
            except Exception as e:
                print(f"Cleanup error: {e}")
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old session files"""
        try:
            current_time = datetime.now()
            
            for session_dir in os.listdir(self.temp_dir):
                session_path = os.path.join(self.temp_dir, session_dir)
                
                if os.path.isdir(session_path):
                    # Check directory age
                    dir_mtime = datetime.fromtimestamp(os.path.getmtime(session_path))
                    age_hours = (current_time - dir_mtime).total_seconds() / 3600
                    
                    if age_hours > max_age_hours:
                        shutil.rmtree(session_path)
                        print(f"Cleaned up old session: {session_dir}")
                        
        except Exception as e:
            print(f"Session cleanup error: {e}")
    
    def get_supported_file_types(self) -> Dict[str, List[str]]:
        """Get list of supported file types"""
        return {
            'text': self.config.SUPPORTED_TEXT_TYPES,
            'audio': self.config.SUPPORTED_AUDIO_TYPES,
            'image': self.config.SUPPORTED_IMAGE_TYPES
        }
    
    def get_upload_limits(self) -> Dict[str, Any]:
        """Get upload limits and restrictions"""
        return {
            'max_file_size': self.config.MAX_MEMORY_FILE_SIZE,
            'max_file_size_mb': self.config.MAX_MEMORY_FILE_SIZE / (1024 * 1024),
            'supported_types': self.get_supported_file_types()
        }
    
    def __del__(self):
        """Cleanup on object destruction"""
        try:
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass
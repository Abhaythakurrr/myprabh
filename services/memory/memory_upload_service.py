"""
Memory Upload Service for My Prabh
Handles secure file upload and validation for memory processing
"""

import os
import tempfile
import shutil
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import mimetypes
import hashlib

# Try to import optional dependencies
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    # Fallback encryption using base64 (not secure, for development only)
    import base64

from .interfaces import MemoryUploadInterface
from .memory_models import MemoryUploadSession, SourceType
from config.memory_config import MemoryConfig
from utils.memory_utils import (
    generate_session_id, detect_file_type, validate_file_size,
    sanitize_filename, clean_text
)

class MemoryUploadService(MemoryUploadInterface):
    """Service for handling memory file uploads"""
    
    def __init__(self):
        self.config = MemoryConfig()
        self.temp_dir = tempfile.mkdtemp(prefix="myprabh_memory_")
        self.encryption_key = self._get_or_create_encryption_key()
        
        if CRYPTO_AVAILABLE:
            self.cipher_suite = Fernet(self.encryption_key)
        else:
            self.cipher_suite = None
        
        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for memory data"""
        if not CRYPTO_AVAILABLE:
            return b'fallback_key_not_secure'
        
        key = self.config.ENCRYPTION_KEY
        if key:
            return key.encode()
        else:
            # Generate a new key (in production, this should be stored securely)
            return Fernet.generate_key()
    
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
        """Process voice note to text"""
        try:
            # This is a placeholder implementation
            # In production, integrate with speech-to-text service
            
            if self.config.STT_SERVICE == 'openai':
                return self._transcribe_with_openai(audio_data)
            elif self.config.STT_SERVICE == 'google':
                return self._transcribe_with_google(audio_data)
            else:
                # Fallback: return placeholder text
                return "[Voice note transcription not available - please configure STT service]"
                
        except Exception as e:
            print(f"Voice transcription error: {e}")
            return "[Voice note transcription failed]"
    
    def _transcribe_with_openai(self, audio_data: bytes) -> str:
        """Transcribe audio using OpenAI Whisper API"""
        try:
            import openai
            
            # Save audio to temporary file
            temp_audio_path = os.path.join(self.temp_dir, f"audio_{generate_session_id()}.wav")
            with open(temp_audio_path, 'wb') as f:
                f.write(audio_data)
            
            # Transcribe using OpenAI
            client = openai.OpenAI(api_key=self.config.STT_API_KEY)
            
            with open(temp_audio_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            # Clean up temp file
            os.remove(temp_audio_path)
            
            return transcript.text
            
        except Exception as e:
            print(f"OpenAI transcription error: {e}")
            return "[OpenAI transcription failed]"
    
    def _transcribe_with_google(self, audio_data: bytes) -> str:
        """Transcribe audio using Google Speech-to-Text"""
        try:
            from google.cloud import speech
            
            client = speech.SpeechClient()
            
            audio = speech.RecognitionAudio(content=audio_data)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
            )
            
            response = client.recognize(config=config, audio=audio)
            
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript + " "
            
            return transcript.strip()
            
        except Exception as e:
            print(f"Google transcription error: {e}")
            return "[Google transcription failed]"
    
    def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """Process image and extract information"""
        try:
            # This is a placeholder implementation
            # In production, integrate with image captioning service
            
            if self.config.IMAGE_CAPTION_SERVICE == 'openai':
                return self._caption_with_openai(image_data)
            elif self.config.IMAGE_CAPTION_SERVICE == 'google':
                return self._caption_with_google(image_data)
            else:
                # Fallback: basic image info
                return {
                    'caption': '[Image caption not available - please configure image service]',
                    'description': 'An uploaded image file',
                    'metadata': {
                        'size': len(image_data),
                        'processed_at': datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            print(f"Image processing error: {e}")
            return {
                'caption': '[Image processing failed]',
                'description': 'Failed to process image',
                'metadata': {'error': str(e)}
            }
    
    def _caption_with_openai(self, image_data: bytes) -> Dict[str, Any]:
        """Generate image caption using OpenAI Vision API"""
        try:
            import openai
            import base64
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            client = openai.OpenAI(api_key=self.config.IMAGE_CAPTION_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this image in detail, focusing on emotions, people, places, and memorable moments."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            description = response.choices[0].message.content
            
            return {
                'caption': description[:100] + "..." if len(description) > 100 else description,
                'description': description,
                'metadata': {
                    'service': 'openai',
                    'model': 'gpt-4-vision-preview',
                    'processed_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            print(f"OpenAI image captioning error: {e}")
            return {
                'caption': '[OpenAI image captioning failed]',
                'description': 'Failed to generate image caption',
                'metadata': {'error': str(e)}
            }
    
    def _caption_with_google(self, image_data: bytes) -> Dict[str, Any]:
        """Generate image caption using Google Vision API"""
        try:
            from google.cloud import vision
            
            client = vision.ImageAnnotatorClient()
            image = vision.Image(content=image_data)
            
            # Detect labels and text
            labels_response = client.label_detection(image=image)
            text_response = client.text_detection(image=image)
            
            labels = [label.description for label in labels_response.label_annotations[:5]]
            texts = [text.description for text in text_response.text_annotations[:3]]
            
            # Create description
            description = f"Image contains: {', '.join(labels)}"
            if texts:
                description += f". Text found: {', '.join(texts)}"
            
            return {
                'caption': description[:100] + "..." if len(description) > 100 else description,
                'description': description,
                'metadata': {
                    'service': 'google',
                    'labels': labels,
                    'texts': texts,
                    'processed_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            print(f"Google image captioning error: {e}")
            return {
                'caption': '[Google image captioning failed]',
                'description': 'Failed to generate image caption',
                'metadata': {'error': str(e)}
            }
    
    def _encrypt_content(self, content: str) -> bytes:
        """Encrypt content for secure storage"""
        try:
            if CRYPTO_AVAILABLE and self.cipher_suite:
                return self.cipher_suite.encrypt(content.encode('utf-8'))
            else:
                # Fallback: base64 encoding (not secure, for development only)
                return base64.b64encode(content.encode('utf-8'))
        except Exception as e:
            print(f"Encryption error: {e}")
            raise e
    
    def _decrypt_content(self, encrypted_content: bytes) -> str:
        """Decrypt content from storage"""
        try:
            if CRYPTO_AVAILABLE and self.cipher_suite:
                return self.cipher_suite.decrypt(encrypted_content).decode('utf-8')
            else:
                # Fallback: base64 decoding (not secure, for development only)
                return base64.b64decode(encrypted_content).decode('utf-8')
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
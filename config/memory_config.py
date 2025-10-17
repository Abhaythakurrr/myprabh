"""
Configuration for memory processing system
"""

import os
from typing import Dict, Any

class MemoryConfig:
    """Configuration class for memory processing"""
    
    # Vector Database Configuration
    VECTOR_DB_TYPE = os.environ.get('VECTOR_DB_TYPE', 'pinecone')  # pinecone, qdrant, milvus
    VECTOR_DB_URL = os.environ.get('VECTOR_DB_URL', '')
    VECTOR_DB_API_KEY = os.environ.get('VECTOR_DB_API_KEY', '')
    VECTOR_DB_INDEX_NAME = os.environ.get('VECTOR_DB_INDEX_NAME', 'myprabh-memories')
    
    # Embedding Model Configuration
    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    EMBEDDING_DIMENSION = int(os.environ.get('EMBEDDING_DIMENSION', '384'))
    
    # Memory Processing Configuration
    CHUNK_SIZE = int(os.environ.get('MEMORY_CHUNK_SIZE', '1000'))  # tokens per chunk
    CHUNK_OVERLAP = int(os.environ.get('MEMORY_CHUNK_OVERLAP', '200'))  # overlap between chunks
    MAX_MEMORY_FILE_SIZE = int(os.environ.get('MAX_MEMORY_FILE_SIZE', '50')) * 1024 * 1024  # 50MB default
    
    # Supported file types
    SUPPORTED_TEXT_TYPES = ['.txt', '.md', '.json', '.csv']
    SUPPORTED_AUDIO_TYPES = ['.mp3', '.wav', '.m4a', '.ogg']
    SUPPORTED_IMAGE_TYPES = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    
    # Speech-to-Text Configuration
    STT_SERVICE = os.environ.get('STT_SERVICE', 'openai')  # openai, google, azure
    STT_API_KEY = os.environ.get('STT_API_KEY', '')
    
    # Image Processing Configuration
    IMAGE_CAPTION_SERVICE = os.environ.get('IMAGE_CAPTION_SERVICE', 'openai')  # openai, google, azure
    IMAGE_CAPTION_API_KEY = os.environ.get('IMAGE_CAPTION_API_KEY', '')
    
    # Personalization Configuration
    PERSONALIZATION_LEVELS = {
        'basic': {
            'max_memories': 1000,
            'features': ['persona_prompt', 'basic_retrieval']
        },
        'enhanced': {
            'max_memories': 10000,
            'features': ['persona_prompt', 'advanced_retrieval', 'personality_analysis']
        },
        'premium': {
            'max_memories': 100000,
            'features': ['persona_prompt', 'advanced_retrieval', 'personality_analysis', 'lora_adapters', 'voice_synthesis']
        }
    }
    
    # Privacy and Security
    ENCRYPTION_KEY = os.environ.get('MEMORY_ENCRYPTION_KEY', '')
    DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', '365'))
    
    @classmethod
    def get_vector_db_config(cls) -> Dict[str, Any]:
        """Get vector database configuration"""
        return {
            'type': cls.VECTOR_DB_TYPE,
            'url': cls.VECTOR_DB_URL,
            'api_key': cls.VECTOR_DB_API_KEY,
            'index_name': cls.VECTOR_DB_INDEX_NAME,
            'dimension': cls.EMBEDDING_DIMENSION
        }
    
    @classmethod
    def get_embedding_config(cls) -> Dict[str, Any]:
        """Get embedding model configuration"""
        return {
            'model': cls.EMBEDDING_MODEL,
            'dimension': cls.EMBEDDING_DIMENSION
        }
    
    @classmethod
    def get_processing_config(cls) -> Dict[str, Any]:
        """Get memory processing configuration"""
        return {
            'chunk_size': cls.CHUNK_SIZE,
            'chunk_overlap': cls.CHUNK_OVERLAP,
            'max_file_size': cls.MAX_MEMORY_FILE_SIZE,
            'supported_types': {
                'text': cls.SUPPORTED_TEXT_TYPES,
                'audio': cls.SUPPORTED_AUDIO_TYPES,
                'image': cls.SUPPORTED_IMAGE_TYPES
            }
        }
    
    @classmethod
    def get_personalization_config(cls, level: str) -> Dict[str, Any]:
        """Get personalization configuration for level"""
        return cls.PERSONALIZATION_LEVELS.get(level, cls.PERSONALIZATION_LEVELS['basic'])
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration completeness"""
        required_vars = [
            'VECTOR_DB_TYPE',
            'EMBEDDING_MODEL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var, None):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️ Missing memory configuration: {', '.join(missing_vars)}")
            return False
        
        return True
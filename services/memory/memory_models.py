"""
Data models for memory processing system
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import numpy as np
from enum import Enum

class MemoryType(Enum):
    """Types of memories"""
    EMOTIONAL = "emotional"
    FACTUAL = "factual"
    CONVERSATIONAL = "conversational"
    EXPERIENTIAL = "experiential"

class SourceType(Enum):
    """Source types for memories"""
    TEXT = "text"
    VOICE = "voice"
    PHOTO = "photo"
    CHAT = "chat"
    DOCUMENT = "document"

class RetentionPolicy(Enum):
    """Memory retention policies"""
    SHORT_TERM = "short_term"  # 30 days
    MID_TERM = "mid_term"      # 1 year
    LONG_TERM = "long_term"    # Permanent

class PrivacyLevel(Enum):
    """Privacy levels for memories"""
    PRIVATE = "private"        # Only user can access
    COMPANION = "companion"    # Specific companion can access
    SHARED = "shared"          # Can be shared with other companions

@dataclass
class MemoryChunk:
    """Data model for memory chunks"""
    id: str
    user_id: str
    companion_id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    memory_type: MemoryType = MemoryType.FACTUAL
    source_type: SourceType = SourceType.TEXT
    timestamp: datetime = field(default_factory=datetime.now)
    retention_policy: RetentionPolicy = RetentionPolicy.LONG_TERM
    privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE
    content_hash: Optional[str] = None
    emotions: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    language: str = "en"
    reading_time_minutes: int = 1
    similarity_threshold: float = 0.8
    
    def __post_init__(self):
        """Post-initialization validation and processing"""
        self.validate()
        self._process_content()
    
    def validate(self) -> bool:
        """Validate memory chunk data"""
        errors = []
        
        # Required fields validation
        if not self.id:
            errors.append("Memory ID is required")
        
        if not self.user_id:
            errors.append("User ID is required")
        
        if not self.companion_id:
            errors.append("Companion ID is required")
        
        if not self.content or not self.content.strip():
            errors.append("Content cannot be empty")
        
        # Content length validation
        if len(self.content) > 10000:  # 10k character limit per chunk
            errors.append("Content exceeds maximum length of 10,000 characters")
        
        if len(self.content) < 10:  # Minimum content length
            errors.append("Content must be at least 10 characters")
        
        # Embedding validation
        if self.embedding is not None:
            if not isinstance(self.embedding, list):
                errors.append("Embedding must be a list of floats")
            elif len(self.embedding) == 0:
                errors.append("Embedding cannot be empty")
            elif not all(isinstance(x, (int, float)) for x in self.embedding):
                errors.append("Embedding must contain only numeric values")
        
        # Enum validation
        if not isinstance(self.memory_type, MemoryType):
            errors.append("Invalid memory type")
        
        if not isinstance(self.source_type, SourceType):
            errors.append("Invalid source type")
        
        if not isinstance(self.retention_policy, RetentionPolicy):
            errors.append("Invalid retention policy")
        
        if not isinstance(self.privacy_level, PrivacyLevel):
            errors.append("Invalid privacy level")
        
        # Metadata validation
        if not isinstance(self.metadata, dict):
            errors.append("Metadata must be a dictionary")
        
        if errors:
            raise ValueError(f"Memory chunk validation failed: {'; '.join(errors)}")
        
        return True
    
    def _process_content(self):
        """Process content to extract additional information"""
        from utils.memory_utils import (
            hash_content, extract_emotions_keywords, 
            detect_language, estimate_reading_time
        )
        
        # Generate content hash for deduplication
        self.content_hash = hash_content(self.content)
        
        # Extract emotions
        self.emotions = extract_emotions_keywords(self.content)
        
        # Detect language
        self.language = detect_language(self.content)
        
        # Estimate reading time
        self.reading_time_minutes = estimate_reading_time(self.content)
        
        # Extract keywords (simple implementation)
        words = self.content.lower().split()
        # Filter out common stop words and keep meaningful words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'are', 'was', 'were'}
        self.keywords = [word for word in words if len(word) > 3 and word not in stop_words][:10]  # Top 10 keywords
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'companion_id': self.companion_id,
            'content': self.content,
            'embedding': self.embedding,
            'metadata': self.metadata,
            'memory_type': self.memory_type.value,
            'source_type': self.source_type.value,
            'timestamp': self.timestamp.isoformat(),
            'retention_policy': self.retention_policy.value,
            'privacy_level': self.privacy_level.value,
            'content_hash': self.content_hash,
            'emotions': self.emotions,
            'keywords': self.keywords,
            'language': self.language,
            'reading_time_minutes': self.reading_time_minutes,
            'similarity_threshold': self.similarity_threshold
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryChunk':
        """Create from dictionary"""
        # Convert string enums back to enum objects
        data['memory_type'] = MemoryType(data.get('memory_type', 'factual'))
        data['source_type'] = SourceType(data.get('source_type', 'text'))
        data['retention_policy'] = RetentionPolicy(data.get('retention_policy', 'long_term'))
        data['privacy_level'] = PrivacyLevel(data.get('privacy_level', 'private'))
        
        # Convert timestamp string back to datetime
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        return cls(**data)
    
    def is_similar_to(self, other: 'MemoryChunk') -> bool:
        """Check if this memory is similar to another"""
        from utils.memory_utils import calculate_similarity_score
        
        if self.content_hash == other.content_hash:
            return True
        
        similarity = calculate_similarity_score(self.content, other.content)
        return similarity >= self.similarity_threshold
    
    def get_age_days(self) -> int:
        """Get age of memory in days"""
        return (datetime.now() - self.timestamp).days
    
    def should_be_retained(self) -> bool:
        """Check if memory should be retained based on retention policy"""
        age_days = self.get_age_days()
        
        if self.retention_policy == RetentionPolicy.SHORT_TERM:
            return age_days <= 30
        elif self.retention_policy == RetentionPolicy.MID_TERM:
            return age_days <= 365
        else:  # LONG_TERM
            return True

@dataclass
class PersonalizationProfile:
    """Data model for AI personalization profiles"""
    user_id: str
    companion_id: str
    personality_traits: Dict[str, float] = field(default_factory=dict)
    communication_style: Dict[str, Any] = field(default_factory=dict)
    emotional_patterns: Dict[str, Any] = field(default_factory=dict)
    memory_preferences: Dict[str, Any] = field(default_factory=dict)
    adapter_path: Optional[str] = None
    persona_prompt: str = ""
    last_updated: datetime = field(default_factory=datetime.now)
    personalization_level: str = "basic"
    total_memories: int = 0
    interaction_count: int = 0
    
    def validate(self) -> bool:
        """Validate personalization profile"""
        errors = []
        
        if not self.user_id:
            errors.append("User ID is required")
        
        if not self.companion_id:
            errors.append("Companion ID is required")
        
        if self.personalization_level not in ['basic', 'enhanced', 'premium']:
            errors.append("Invalid personalization level")
        
        if not isinstance(self.personality_traits, dict):
            errors.append("Personality traits must be a dictionary")
        
        if not isinstance(self.communication_style, dict):
            errors.append("Communication style must be a dictionary")
        
        if errors:
            raise ValueError(f"Personalization profile validation failed: {'; '.join(errors)}")
        
        return True
    
    def update_personality_trait(self, trait: str, value: float):
        """Update a personality trait"""
        if not 0.0 <= value <= 1.0:
            raise ValueError("Personality trait values must be between 0.0 and 1.0")
        
        self.personality_traits[trait] = value
        self.last_updated = datetime.now()
    
    def get_dominant_traits(self, top_n: int = 5) -> List[tuple]:
        """Get top N dominant personality traits"""
        return sorted(self.personality_traits.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'user_id': self.user_id,
            'companion_id': self.companion_id,
            'personality_traits': self.personality_traits,
            'communication_style': self.communication_style,
            'emotional_patterns': self.emotional_patterns,
            'memory_preferences': self.memory_preferences,
            'adapter_path': self.adapter_path,
            'persona_prompt': self.persona_prompt,
            'last_updated': self.last_updated.isoformat(),
            'personalization_level': self.personalization_level,
            'total_memories': self.total_memories,
            'interaction_count': self.interaction_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonalizationProfile':
        """Create from dictionary"""
        if isinstance(data.get('last_updated'), str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        
        return cls(**data)

@dataclass
class MemoryUploadSession:
    """Data model for memory upload sessions"""
    session_id: str
    user_id: str
    companion_id: str
    uploaded_files: List[Dict[str, Any]] = field(default_factory=list)
    processing_status: str = "pending"  # pending, processing, completed, failed
    total_chunks_created: int = 0
    processing_errors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate upload session"""
        errors = []
        
        if not self.session_id:
            errors.append("Session ID is required")
        
        if not self.user_id:
            errors.append("User ID is required")
        
        if not self.companion_id:
            errors.append("Companion ID is required")
        
        if self.processing_status not in ['pending', 'processing', 'completed', 'failed']:
            errors.append("Invalid processing status")
        
        if errors:
            raise ValueError(f"Upload session validation failed: {'; '.join(errors)}")
        
        return True
    
    def add_file(self, filename: str, file_type: str, file_size: int, status: str = "pending"):
        """Add file to upload session"""
        file_info = {
            'filename': filename,
            'file_type': file_type,
            'file_size': file_size,
            'status': status,
            'uploaded_at': datetime.now().isoformat(),
            'chunks_created': 0,
            'errors': []
        }
        self.uploaded_files.append(file_info)
    
    def update_file_status(self, filename: str, status: str, chunks_created: int = 0, errors: List[str] = None):
        """Update file processing status"""
        for file_info in self.uploaded_files:
            if file_info['filename'] == filename:
                file_info['status'] = status
                file_info['chunks_created'] = chunks_created
                if errors:
                    file_info['errors'].extend(errors)
                break
    
    def mark_completed(self):
        """Mark session as completed"""
        self.processing_status = "completed"
        self.completed_at = datetime.now()
    
    def mark_failed(self, error: str):
        """Mark session as failed"""
        self.processing_status = "failed"
        self.processing_errors.append(error)
        self.completed_at = datetime.now()
    
    def get_total_file_size(self) -> int:
        """Get total size of all uploaded files"""
        return sum(file_info['file_size'] for file_info in self.uploaded_files)
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get processing summary"""
        total_files = len(self.uploaded_files)
        completed_files = len([f for f in self.uploaded_files if f['status'] == 'completed'])
        failed_files = len([f for f in self.uploaded_files if f['status'] == 'failed'])
        
        return {
            'total_files': total_files,
            'completed_files': completed_files,
            'failed_files': failed_files,
            'total_chunks': self.total_chunks_created,
            'processing_time': (self.completed_at - self.created_at).total_seconds() if self.completed_at else None,
            'errors': self.processing_errors
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'companion_id': self.companion_id,
            'uploaded_files': self.uploaded_files,
            'processing_status': self.processing_status,
            'total_chunks_created': self.total_chunks_created,
            'processing_errors': self.processing_errors,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryUploadSession':
        """Create from dictionary"""
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if data.get('completed_at') and isinstance(data['completed_at'], str):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        
        return cls(**data)
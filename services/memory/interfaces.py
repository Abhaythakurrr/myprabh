"""
Core interfaces for memory processing system
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime

class MemoryProcessorInterface(ABC):
    """Interface for memory processing operations"""
    
    @abstractmethod
    def chunk_memory(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Split memory text into semantic chunks"""
        pass
    
    @abstractmethod
    def generate_embeddings(self, chunks: List[str]) -> List[np.ndarray]:
        """Generate embeddings for memory chunks"""
        pass
    
    @abstractmethod
    def extract_metadata(self, chunk: str, source_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract metadata from memory chunk"""
        pass
    
    @abstractmethod
    def categorize_memory(self, chunk: str) -> str:
        """Categorize memory type (emotional, factual, conversational)"""
        pass

class VectorStoreInterface(ABC):
    """Interface for vector memory storage operations"""
    
    @abstractmethod
    def store_memory(self, user_id: str, chunk: str, embedding: np.ndarray, metadata: Dict[str, Any]) -> str:
        """Store memory chunk with embedding"""
        pass
    
    @abstractmethod
    def search_memories(self, user_id: str, query_embedding: np.ndarray, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for relevant memories"""
        pass
    
    @abstractmethod
    def delete_user_memories(self, user_id: str) -> bool:
        """Delete all memories for a user"""
        pass
    
    @abstractmethod
    def update_memory_metadata(self, memory_id: str, metadata: Dict[str, Any]) -> bool:
        """Update memory metadata"""
        pass

class PersonalizationEngineInterface(ABC):
    """Interface for AI personalization operations"""
    
    @abstractmethod
    def create_persona_prompt(self, user_id: str, companion_id: str) -> str:
        """Create persona prompt from user memories"""
        pass
    
    @abstractmethod
    def analyze_personality(self, memories: List[str]) -> Dict[str, Any]:
        """Analyze personality traits from memories"""
        pass
    
    @abstractmethod
    def update_personality_profile(self, user_id: str, companion_id: str, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update personality profile based on interactions"""
        pass
    
    @abstractmethod
    def get_personalization_level(self, user_id: str) -> str:
        """Get user's personalization level (basic, enhanced, premium)"""
        pass

class MemoryUploadInterface(ABC):
    """Interface for memory upload operations"""
    
    @abstractmethod
    def upload_memory(self, user_id: str, file_data: bytes, file_type: str, metadata: Dict[str, Any] = None) -> str:
        """Upload and process memory file"""
        pass
    
    @abstractmethod
    def process_voice_note(self, audio_data: bytes) -> str:
        """Process voice note to text"""
        pass
    
    @abstractmethod
    def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """Process image and extract information"""
        pass
    
    @abstractmethod
    def validate_upload(self, file_data: bytes, file_type: str) -> bool:
        """Validate uploaded file"""
        pass
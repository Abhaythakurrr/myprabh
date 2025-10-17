"""
Memory Processing Service for My Prabh
Handles text chunking, metadata extraction, and memory categorization
"""

import re
import nltk
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np
from collections import Counter

from .interfaces import MemoryProcessorInterface
from .memory_models import MemoryChunk, MemoryType, SourceType, RetentionPolicy, PrivacyLevel
from config.memory_config import MemoryConfig
from utils.memory_utils import (
    generate_memory_id, hash_content, extract_emotions_keywords,
    detect_language, estimate_reading_time, extract_timestamps_from_text,
    chunk_text_by_sentences, clean_text
)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)

class MemoryProcessor(MemoryProcessorInterface):
    """Service for processing memories into chunks with metadata"""
    
    def __init__(self):
        self.config = MemoryConfig()
        self.stop_words = self._load_stop_words()
        
        # Emotion keywords for categorization
        self.emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'thrilled', 'delighted', 'cheerful', 'elated', 'blissful', 'ecstatic'],
            'sadness': ['sad', 'depressed', 'melancholy', 'grief', 'sorrow', 'heartbroken', 'miserable', 'dejected'],
            'anger': ['angry', 'furious', 'rage', 'irritated', 'annoyed', 'frustrated', 'livid', 'enraged'],
            'fear': ['afraid', 'scared', 'terrified', 'anxious', 'worried', 'nervous', 'frightened', 'panicked'],
            'love': ['love', 'adore', 'cherish', 'affection', 'romance', 'passion', 'devotion', 'infatuation'],
            'surprise': ['surprised', 'amazed', 'astonished', 'shocked', 'stunned', 'bewildered', 'astounded'],
            'disgust': ['disgusted', 'revolted', 'repulsed', 'sickened', 'nauseated', 'appalled'],
            'trust': ['trust', 'faith', 'confidence', 'belief', 'reliance', 'dependence'],
            'anticipation': ['excited', 'eager', 'hopeful', 'expectant', 'anticipating', 'looking forward']
        }
        
        # Memory type indicators
        self.memory_type_indicators = {
            MemoryType.EMOTIONAL: ['feel', 'felt', 'emotion', 'heart', 'soul', 'love', 'hate', 'fear', 'joy', 'sad'],
            MemoryType.FACTUAL: ['fact', 'information', 'data', 'statistics', 'research', 'study', 'report'],
            MemoryType.CONVERSATIONAL: ['said', 'told', 'asked', 'replied', 'conversation', 'chat', 'talk', 'discuss'],
            MemoryType.EXPERIENTIAL: ['experience', 'happened', 'went', 'did', 'saw', 'heard', 'felt', 'lived']
        }
    
    def _load_stop_words(self) -> set:
        """Load stop words for text processing"""
        try:
            from nltk.corpus import stopwords
            return set(stopwords.words('english'))
        except:
            # Fallback stop words
            return {
                'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
                'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
                'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
                'we', 'they', 'me', 'him', 'her', 'us', 'them'
            }
    
    def chunk_memory(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Split memory text into semantic chunks"""
        try:
            # Clean and normalize text
            cleaned_text = clean_text(text)
            
            if len(cleaned_text) < 50:  # Too short to chunk
                return [{
                    'content': cleaned_text,
                    'chunk_index': 0,
                    'total_chunks': 1,
                    'word_count': len(cleaned_text.split()),
                    'metadata': metadata or {}
                }]
            
            # Use different chunking strategies based on content length
            if len(cleaned_text.split()) <= self.config.CHUNK_SIZE:
                # Single chunk
                chunks = [cleaned_text]
            else:
                # Multiple chunks with overlap
                chunks = self._semantic_chunking(cleaned_text)
            
            # Process each chunk
            processed_chunks = []
            for i, chunk_content in enumerate(chunks):
                chunk_data = {
                    'content': chunk_content,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'word_count': len(chunk_content.split()),
                    'metadata': self._extract_chunk_metadata(chunk_content, metadata)
                }
                processed_chunks.append(chunk_data)
            
            return processed_chunks
            
        except Exception as e:
            print(f"Error chunking memory: {e}")
            # Return single chunk as fallback
            return [{
                'content': text,
                'chunk_index': 0,
                'total_chunks': 1,
                'word_count': len(text.split()),
                'metadata': metadata or {},
                'error': str(e)
            }]
    
    def _semantic_chunking(self, text: str) -> List[str]:
        """Perform semantic chunking of text"""
        try:
            # Try sentence-based chunking first
            sentences = nltk.sent_tokenize(text)
            
            if len(sentences) <= 2:
                # Too few sentences, use paragraph chunking
                return self._paragraph_chunking(text)
            
            chunks = []
            current_chunk = ""
            current_word_count = 0
            
            for sentence in sentences:
                sentence_word_count = len(sentence.split())
                
                # Check if adding this sentence would exceed chunk size
                if current_word_count + sentence_word_count > self.config.CHUNK_SIZE and current_chunk:
                    # Save current chunk
                    chunks.append(current_chunk.strip())
                    
                    # Start new chunk with overlap
                    overlap_sentences = self._get_overlap_sentences(current_chunk)
                    current_chunk = overlap_sentences + " " + sentence
                    current_word_count = len(current_chunk.split())
                else:
                    # Add sentence to current chunk
                    current_chunk += " " + sentence
                    current_word_count += sentence_word_count
            
            # Add final chunk
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            return chunks
            
        except Exception as e:
            print(f"Error in semantic chunking: {e}")
            # Fallback to simple word-based chunking
            return self._word_based_chunking(text)
    
    def _paragraph_chunking(self, text: str) -> List[str]:
        """Chunk text by paragraphs"""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        current_word_count = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            paragraph_word_count = len(paragraph.split())
            
            if current_word_count + paragraph_word_count > self.config.CHUNK_SIZE and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
                current_word_count = paragraph_word_count
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
                current_word_count += paragraph_word_count
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _word_based_chunking(self, text: str) -> List[str]:
        """Simple word-based chunking as fallback"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.config.CHUNK_SIZE - self.config.CHUNK_OVERLAP):
            chunk_words = words[i:i + self.config.CHUNK_SIZE]
            chunks.append(' '.join(chunk_words))
        
        return chunks
    
    def _get_overlap_sentences(self, chunk: str) -> str:
        """Get overlap sentences from the end of a chunk"""
        try:
            sentences = nltk.sent_tokenize(chunk)
            overlap_word_count = 0
            overlap_sentences = []
            
            # Take sentences from the end until we reach overlap limit
            for sentence in reversed(sentences):
                sentence_word_count = len(sentence.split())
                if overlap_word_count + sentence_word_count <= self.config.CHUNK_OVERLAP:
                    overlap_sentences.insert(0, sentence)
                    overlap_word_count += sentence_word_count
                else:
                    break
            
            return ' '.join(overlap_sentences)
            
        except:
            # Fallback: take last N words
            words = chunk.split()
            overlap_words = words[-self.config.CHUNK_OVERLAP:] if len(words) > self.config.CHUNK_OVERLAP else words
            return ' '.join(overlap_words)
    
    def _extract_chunk_metadata(self, chunk: str, base_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract metadata from a chunk"""
        metadata = base_metadata.copy() if base_metadata else {}
        
        try:
            # Basic statistics
            metadata.update({
                'character_count': len(chunk),
                'word_count': len(chunk.split()),
                'sentence_count': len(nltk.sent_tokenize(chunk)),
                'language': detect_language(chunk),
                'reading_time_minutes': estimate_reading_time(chunk)
            })
            
            # Extract emotions
            emotions = extract_emotions_keywords(chunk)
            if emotions:
                metadata['emotions'] = emotions
                metadata['dominant_emotion'] = emotions[0] if emotions else None
            
            # Extract timestamps
            timestamps = extract_timestamps_from_text(chunk)
            if timestamps:
                metadata['timestamps'] = [ts.isoformat() for ts in timestamps]
                metadata['earliest_timestamp'] = min(timestamps).isoformat()
                metadata['latest_timestamp'] = max(timestamps).isoformat()
            
            # Extract keywords
            keywords = self._extract_keywords(chunk)
            if keywords:
                metadata['keywords'] = keywords[:10]  # Top 10 keywords
            
            # Extract named entities (simple implementation)
            entities = self._extract_simple_entities(chunk)
            if entities:
                metadata['entities'] = entities
            
            # Sentiment analysis (simple)
            sentiment = self._analyze_sentiment(chunk)
            metadata['sentiment'] = sentiment
            
        except Exception as e:
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        try:
            # Tokenize and remove stop words
            words = nltk.word_tokenize(text.lower())
            words = [word for word in words if word.isalpha() and word not in self.stop_words and len(word) > 2]
            
            # Get word frequencies
            word_freq = Counter(words)
            
            # Return most common words
            return [word for word, freq in word_freq.most_common(20)]
            
        except:
            # Fallback: simple word splitting
            words = text.lower().split()
            words = [word for word in words if len(word) > 3 and word not in self.stop_words]
            return list(set(words))[:20]
    
    def _extract_simple_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract simple named entities"""
        entities = {
            'people': [],
            'places': [],
            'organizations': [],
            'dates': []
        }
        
        try:
            # Simple pattern matching for entities
            
            # People (capitalized words that might be names)
            people_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
            potential_people = re.findall(people_pattern, text)
            
            # Filter out common words that aren't names
            common_words = {'The', 'This', 'That', 'When', 'Where', 'What', 'How', 'Why', 'Who'}
            entities['people'] = [name for name in potential_people if name not in common_words][:5]
            
            # Places (words ending with common place suffixes)
            place_suffixes = ['Street', 'Road', 'Avenue', 'Boulevard', 'Lane', 'Drive', 'Park', 'Beach', 'Mountain', 'Lake', 'River']
            for suffix in place_suffixes:
                pattern = rf'\b\w+\s+{suffix}\b'
                places = re.findall(pattern, text, re.IGNORECASE)
                entities['places'].extend(places)
            
            # Dates (simple date patterns)
            date_patterns = [
                r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
                r'\b\d{4}-\d{2}-\d{2}\b',      # YYYY-MM-DD
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
            ]
            
            for pattern in date_patterns:
                dates = re.findall(pattern, text, re.IGNORECASE)
                entities['dates'].extend(dates)
            
            # Remove duplicates and limit results
            for key in entities:
                entities[key] = list(set(entities[key]))[:5]
            
        except Exception as e:
            entities['extraction_error'] = str(e)
        
        return entities
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Simple sentiment analysis"""
        try:
            # Simple keyword-based sentiment analysis
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'enjoy', 'happy', 'joy', 'pleased']
            negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'sad', 'angry', 'frustrated', 'disappointed', 'upset']
            
            text_lower = text.lower()
            words = text_lower.split()
            
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            total_words = len(words)
            
            if total_words == 0:
                return {'polarity': 'neutral', 'confidence': 0.0}
            
            positive_ratio = positive_count / total_words
            negative_ratio = negative_count / total_words
            
            if positive_ratio > negative_ratio:
                polarity = 'positive'
                confidence = positive_ratio
            elif negative_ratio > positive_ratio:
                polarity = 'negative'
                confidence = negative_ratio
            else:
                polarity = 'neutral'
                confidence = 0.5
            
            return {
                'polarity': polarity,
                'confidence': min(confidence * 2, 1.0),  # Scale confidence
                'positive_words': positive_count,
                'negative_words': negative_count
            }
            
        except Exception as e:
            return {'polarity': 'neutral', 'confidence': 0.0, 'error': str(e)}
    
    def generate_embeddings(self, chunks: List[str]) -> List[np.ndarray]:
        """Generate embeddings for memory chunks"""
        try:
            # This is a placeholder implementation
            # In production, use a proper embedding model like sentence-transformers
            
            embeddings = []
            for chunk in chunks:
                # Simple bag-of-words embedding (for demonstration)
                embedding = self._simple_embedding(chunk)
                embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            # Return zero embeddings as fallback
            return [np.zeros(self.config.EMBEDDING_DIMENSION) for _ in chunks]
    
    def _simple_embedding(self, text: str) -> np.ndarray:
        """Generate simple embedding for text (placeholder)"""
        # This is a very basic implementation for demonstration
        # In production, use proper embedding models
        
        words = text.lower().split()
        word_counts = Counter(words)
        
        # Create a simple hash-based embedding
        embedding = np.zeros(self.config.EMBEDDING_DIMENSION)
        
        for word, count in word_counts.items():
            # Simple hash function to map words to embedding dimensions
            word_hash = hash(word) % self.config.EMBEDDING_DIMENSION
            embedding[word_hash] += count
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def extract_metadata(self, chunk: str, source_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract metadata from memory chunk"""
        return self._extract_chunk_metadata(chunk, source_metadata)
    
    def categorize_memory(self, chunk: str) -> str:
        """Categorize memory type based on content"""
        try:
            chunk_lower = chunk.lower()
            words = chunk_lower.split()
            
            # Count indicators for each memory type
            type_scores = {}
            
            for memory_type, indicators in self.memory_type_indicators.items():
                score = sum(1 for word in words if word in indicators)
                type_scores[memory_type] = score
            
            # Find the type with highest score
            if type_scores:
                best_type = max(type_scores, key=type_scores.get)
                if type_scores[best_type] > 0:
                    return best_type.value
            
            # Default categorization based on content analysis
            if any(emotion in chunk_lower for emotion_list in self.emotion_keywords.values() for emotion in emotion_list):
                return MemoryType.EMOTIONAL.value
            elif any(word in chunk_lower for word in ['said', 'told', 'asked', 'replied']):
                return MemoryType.CONVERSATIONAL.value
            elif any(word in chunk_lower for word in ['went', 'did', 'saw', 'experienced']):
                return MemoryType.EXPERIENTIAL.value
            else:
                return MemoryType.FACTUAL.value
                
        except Exception as e:
            print(f"Error categorizing memory: {e}")
            return MemoryType.FACTUAL.value
    
    def create_memory_chunks(self, user_id: str, companion_id: str, text: str, 
                           source_type: SourceType = SourceType.TEXT,
                           retention_policy: RetentionPolicy = RetentionPolicy.LONG_TERM,
                           privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE,
                           metadata: Dict[str, Any] = None) -> List[MemoryChunk]:
        """Create MemoryChunk objects from text"""
        try:
            # Chunk the text
            chunk_data_list = self.chunk_memory(text, metadata)
            
            # Generate embeddings for all chunks
            chunk_contents = [chunk_data['content'] for chunk_data in chunk_data_list]
            embeddings = self.generate_embeddings(chunk_contents)
            
            # Create MemoryChunk objects
            memory_chunks = []
            
            for i, chunk_data in enumerate(chunk_data_list):
                # Determine memory type
                memory_type_str = self.categorize_memory(chunk_data['content'])
                memory_type = MemoryType(memory_type_str)
                
                # Create memory chunk
                memory_chunk = MemoryChunk(
                    id=generate_memory_id(),
                    user_id=user_id,
                    companion_id=companion_id,
                    content=chunk_data['content'],
                    embedding=embeddings[i].tolist() if i < len(embeddings) else None,
                    metadata=chunk_data['metadata'],
                    memory_type=memory_type,
                    source_type=source_type,
                    retention_policy=retention_policy,
                    privacy_level=privacy_level
                )
                
                memory_chunks.append(memory_chunk)
            
            return memory_chunks
            
        except Exception as e:
            print(f"Error creating memory chunks: {e}")
            # Return single chunk as fallback
            return [MemoryChunk(
                id=generate_memory_id(),
                user_id=user_id,
                companion_id=companion_id,
                content=text,
                memory_type=MemoryType.FACTUAL,
                source_type=source_type,
                retention_policy=retention_policy,
                privacy_level=privacy_level,
                metadata={'error': str(e)}
            )]
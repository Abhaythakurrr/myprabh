"""
Utility functions for memory processing
"""

import hashlib
import uuid
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import mimetypes
import magic

def generate_memory_id() -> str:
    """Generate unique memory ID"""
    return str(uuid.uuid4())

def generate_session_id() -> str:
    """Generate unique session ID"""
    return str(uuid.uuid4())

def hash_content(content: str) -> str:
    """Generate hash for content deduplication"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def detect_file_type(file_data: bytes, filename: str = None) -> str:
    """Detect file type from data and filename"""
    try:
        # Use python-magic for accurate detection
        mime_type = magic.from_buffer(file_data, mime=True)
        return mime_type
    except:
        # Fallback to filename extension
        if filename:
            mime_type, _ = mimetypes.guess_type(filename)
            return mime_type or 'application/octet-stream'
        return 'application/octet-stream'

def validate_file_size(file_data: bytes, max_size: int) -> bool:
    """Validate file size against maximum"""
    return len(file_data) <= max_size

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might interfere with processing
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def extract_timestamps_from_text(text: str) -> List[datetime]:
    """Extract timestamps from text content"""
    timestamps = []
    
    # Common timestamp patterns
    patterns = [
        r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
        r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}',        # MM/DD/YYYY HH:MM
        r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}',        # MM-DD-YYYY HH:MM
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                # Try different datetime formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M', '%m-%d-%Y %H:%M']:
                    try:
                        timestamp = datetime.strptime(match, fmt)
                        timestamps.append(timestamp)
                        break
                    except ValueError:
                        continue
            except:
                continue
    
    return timestamps

def detect_language(text: str) -> str:
    """Detect language of text content"""
    # Simple language detection based on common words
    # In production, use a proper language detection library
    
    english_words = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with']
    spanish_words = ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no']
    french_words = ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir']
    
    text_lower = text.lower()
    words = text_lower.split()
    
    if len(words) < 10:
        return 'unknown'
    
    english_count = sum(1 for word in words if word in english_words)
    spanish_count = sum(1 for word in words if word in spanish_words)
    french_count = sum(1 for word in words if word in french_words)
    
    total_words = len(words)
    english_ratio = english_count / total_words
    spanish_ratio = spanish_count / total_words
    french_ratio = french_count / total_words
    
    if english_ratio > 0.1:
        return 'en'
    elif spanish_ratio > 0.1:
        return 'es'
    elif french_ratio > 0.1:
        return 'fr'
    else:
        return 'unknown'

def estimate_reading_time(text: str) -> int:
    """Estimate reading time in minutes"""
    words = len(text.split())
    # Average reading speed: 200 words per minute
    return max(1, words // 200)

def extract_emotions_keywords(text: str) -> List[str]:
    """Extract emotion-related keywords from text"""
    emotion_keywords = {
        'joy': ['happy', 'joy', 'excited', 'thrilled', 'delighted', 'cheerful', 'elated'],
        'sadness': ['sad', 'depressed', 'melancholy', 'grief', 'sorrow', 'heartbroken'],
        'anger': ['angry', 'furious', 'rage', 'irritated', 'annoyed', 'frustrated'],
        'fear': ['afraid', 'scared', 'terrified', 'anxious', 'worried', 'nervous'],
        'love': ['love', 'adore', 'cherish', 'affection', 'romance', 'passion'],
        'surprise': ['surprised', 'amazed', 'astonished', 'shocked', 'stunned']
    }
    
    text_lower = text.lower()
    found_emotions = []
    
    for emotion, keywords in emotion_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_emotions.append(emotion)
                break
    
    return list(set(found_emotions))

def chunk_text_by_sentences(text: str, max_chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Chunk text by sentences with overlap"""
    # Split by sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    chunks = []
    current_chunk = ""
    current_size = 0
    
    for sentence in sentences:
        sentence_size = len(sentence.split())
        
        if current_size + sentence_size > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            
            # Create overlap
            overlap_words = current_chunk.split()[-overlap:]
            current_chunk = ' '.join(overlap_words) + ' ' + sentence
            current_size = len(overlap_words) + sentence_size
        else:
            current_chunk += ' ' + sentence
            current_size += sentence_size
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    
    return filename

def calculate_similarity_score(text1: str, text2: str) -> float:
    """Calculate simple similarity score between two texts"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0
"""
Memory Manager for My Prabh
Orchestrates memory processing, storage, and retrieval operations
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .memory_processor import MemoryProcessor
from .vector_store import VectorMemoryStore
from .embedding_service import EmbeddingService
from .memory_upload_service import MemoryUploadService
from .memory_models import (
    MemoryChunk, PersonalizationProfile, MemoryUploadSession,
    MemoryType, SourceType, RetentionPolicy, PrivacyLevel
)
from services.firestore_db import firestore_db
from config.memory_config import MemoryConfig
from utils.memory_utils import generate_memory_id, generate_session_id

class MemoryManager:
    """Central manager for all memory operations"""
    
    def __init__(self):
        self.config = MemoryConfig()
        
        # Initialize services
        self.processor = MemoryProcessor()
        self.vector_store = VectorMemoryStore()
        self.embedding_service = EmbeddingService()
        self.upload_service = MemoryUploadService()
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        print("✅ Memory Manager initialized")
    
    def process_and_store_memory(self, user_id: str, companion_id: str, content: str,
                                source_type: SourceType = SourceType.TEXT,
                                retention_policy: RetentionPolicy = RetentionPolicy.LONG_TERM,
                                privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE,
                                metadata: Dict[str, Any] = None) -> List[str]:
        """Process content and store as memory chunks"""
        try:
            # Create memory chunks from content
            memory_chunks = self.processor.create_memory_chunks(
                user_id=user_id,
                companion_id=companion_id,
                text=content,
                source_type=source_type,
                retention_policy=retention_policy,
                privacy_level=privacy_level,
                metadata=metadata or {}
            )
            
            # Store chunks in vector database and Firestore
            stored_ids = []
            for chunk in memory_chunks:
                # Store in vector database
                vector_id = self.vector_store.store_memory(
                    user_id=user_id,
                    chunk=chunk.content,
                    embedding=chunk.embedding,
                    metadata=chunk.to_dict()
                )
                
                # Store in Firestore for persistence
                firestore_id = self._store_chunk_in_firestore(chunk)
                
                stored_ids.append(chunk.id)
                
                print(f"✅ Stored memory chunk: {chunk.id}")
            
            return stored_ids
            
        except Exception as e:
            print(f"Error processing and storing memory: {e}")
            raise e
    
    def _store_chunk_in_firestore(self, chunk: MemoryChunk) -> str:
        """Store memory chunk in Firestore"""
        try:
            chunk_data = chunk.to_dict()
            
            # Store in memories collection
            doc_ref = firestore_db.db.collection('memories').document(chunk.id)
            doc_ref.set(chunk_data)
            
            return chunk.id
            
        except Exception as e:
            print(f"Error storing chunk in Firestore: {e}")
            raise e
    
    def retrieve_relevant_memories(self, user_id: str, companion_id: str, query: str,
                                 limit: int = 10, memory_types: List[MemoryType] = None,
                                 time_range: Tuple[datetime, datetime] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant memories based on query"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.generate_embedding(query)
            
            # Search vector database
            search_results = self.vector_store.search_memories(
                user_id=user_id,
                query_embedding=query_embedding,
                limit=limit * 2,  # Get more results for filtering
                companion_id=companion_id
            )
            
            # Filter and rank results
            filtered_results = self._filter_and_rank_memories(
                search_results, memory_types, time_range, limit
            )
            
            # Enrich with additional metadata from Firestore
            enriched_results = self._enrich_memory_results(filtered_results)
            
            return enriched_results
            
        except Exception as e:
            print(f"Error retrieving memories: {e}")
            return []
    
    def _filter_and_rank_memories(self, search_results: List[Dict[str, Any]],
                                 memory_types: List[MemoryType] = None,
                                 time_range: Tuple[datetime, datetime] = None,
                                 limit: int = 10) -> List[Dict[str, Any]]:
        """Filter and rank memory search results"""
        filtered_results = []
        
        for result in search_results:
            metadata = result.get('metadata', {})
            
            # Filter by memory type
            if memory_types:
                memory_type = metadata.get('memory_type')
                if memory_type not in [mt.value for mt in memory_types]:
                    continue
            
            # Filter by time range
            if time_range:
                timestamp_str = metadata.get('timestamp')
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                        if not (time_range[0] <= timestamp <= time_range[1]):
                            continue
                    except:
                        pass
            
            # Check retention policy
            if not self._should_retain_memory(metadata):
                continue
            
            filtered_results.append(result)
        
        # Sort by relevance score and recency
        filtered_results.sort(key=lambda x: (
            x.get('score', 0) * 0.7 +  # Relevance weight
            self._calculate_recency_score(x.get('metadata', {})) * 0.3  # Recency weight
        ), reverse=True)
        
        return filtered_results[:limit]
    
    def _should_retain_memory(self, metadata: Dict[str, Any]) -> bool:
        """Check if memory should be retained based on retention policy"""
        try:
            retention_policy = metadata.get('retention_policy', 'long_term')
            timestamp_str = metadata.get('timestamp')
            
            if not timestamp_str:
                return True  # Keep if no timestamp
            
            timestamp = datetime.fromisoformat(timestamp_str)
            age_days = (datetime.now() - timestamp).days
            
            if retention_policy == 'short_term':
                return age_days <= 30
            elif retention_policy == 'mid_term':
                return age_days <= 365
            else:  # long_term
                return True
                
        except Exception as e:
            print(f"Error checking retention policy: {e}")
            return True  # Keep by default
    
    def _calculate_recency_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate recency score for memory ranking"""
        try:
            timestamp_str = metadata.get('timestamp')
            if not timestamp_str:
                return 0.0
            
            timestamp = datetime.fromisoformat(timestamp_str)
            age_days = (datetime.now() - timestamp).days
            
            # Exponential decay: more recent memories get higher scores
            return max(0.0, 1.0 - (age_days / 365.0))
            
        except Exception as e:
            return 0.0
    
    def _enrich_memory_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich memory results with additional metadata"""
        enriched_results = []
        
        for result in results:
            try:
                memory_id = result.get('id')
                if memory_id:
                    # Get additional data from Firestore
                    doc = firestore_db.db.collection('memories').document(memory_id).get()
                    if doc.exists:
                        firestore_data = doc.to_dict()
                        
                        # Merge data
                        enriched_result = {
                            **result,
                            'firestore_data': firestore_data,
                            'enriched': True
                        }
                        enriched_results.append(enriched_result)
                    else:
                        enriched_results.append(result)
                else:
                    enriched_results.append(result)
                    
            except Exception as e:
                print(f"Error enriching memory result: {e}")
                enriched_results.append(result)
        
        return enriched_results
    
    def upload_and_process_file(self, user_id: str, companion_id: str, file_data: bytes,
                               file_type: str, filename: str = None,
                               metadata: Dict[str, Any] = None) -> str:
        """Upload file and process into memories"""
        try:
            # Upload file
            session_id = self.upload_service.upload_memory(
                user_id=user_id,
                file_data=file_data,
                file_type=file_type,
                companion_id=companion_id,
                filename=filename,
                metadata=metadata
            )
            
            # Get processed content
            processed_content = self.upload_service.get_session_content(session_id, filename or "upload")
            
            # Determine source type
            source_type = self._determine_source_type(file_type)
            
            # Process and store as memories
            memory_ids = self.process_and_store_memory(
                user_id=user_id,
                companion_id=companion_id,
                content=processed_content,
                source_type=source_type,
                metadata=metadata
            )
            
            # Update session with memory IDs
            self._update_session_with_memories(session_id, memory_ids)
            
            return session_id
            
        except Exception as e:
            print(f"Error uploading and processing file: {e}")
            raise e
    
    def _determine_source_type(self, file_type: str) -> SourceType:
        """Determine source type from file type"""
        if file_type.startswith('text/'):
            return SourceType.TEXT
        elif file_type.startswith('audio/'):
            return SourceType.VOICE
        elif file_type.startswith('image/'):
            return SourceType.PHOTO
        elif 'json' in file_type.lower() or 'chat' in file_type.lower():
            return SourceType.CHAT
        else:
            return SourceType.DOCUMENT
    
    def _update_session_with_memories(self, session_id: str, memory_ids: List[str]):
        """Update upload session with created memory IDs"""
        try:
            # Store session info in Firestore
            session_data = {
                'session_id': session_id,
                'memory_ids': memory_ids,
                'created_memories': len(memory_ids),
                'updated_at': datetime.now()
            }
            
            firestore_db.db.collection('upload_sessions').document(session_id).set(session_data)
            
        except Exception as e:
            print(f"Error updating session: {e}")
    
    def get_memory_by_id(self, memory_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get specific memory by ID"""
        try:
            # Get from Firestore
            doc = firestore_db.db.collection('memories').document(memory_id).get()
            if doc.exists:
                memory_data = doc.to_dict()
                
                # Verify user ownership
                if memory_data.get('user_id') == user_id:
                    return memory_data
            
            return None
            
        except Exception as e:
            print(f"Error getting memory by ID: {e}")
            return None
    
    def update_memory(self, memory_id: str, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update memory metadata"""
        try:
            # Verify ownership
            memory = self.get_memory_by_id(memory_id, user_id)
            if not memory:
                return False
            
            # Update in Firestore
            updates['updated_at'] = datetime.now()
            firestore_db.db.collection('memories').document(memory_id).update(updates)
            
            # Update in vector store if needed
            self.vector_store.update_memory_metadata(memory_id, updates)
            
            return True
            
        except Exception as e:
            print(f"Error updating memory: {e}")
            return False
    
    def delete_memory(self, memory_id: str, user_id: str) -> bool:
        """Delete specific memory"""
        try:
            # Verify ownership
            memory = self.get_memory_by_id(memory_id, user_id)
            if not memory:
                return False
            
            # Delete from Firestore
            firestore_db.db.collection('memories').document(memory_id).delete()
            
            # Note: Vector store deletion by ID is complex and depends on the implementation
            # For now, we'll mark it as deleted in metadata
            
            return True
            
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False
    
    def delete_all_user_memories(self, user_id: str, companion_id: str = None) -> bool:
        """Delete all memories for a user"""
        try:
            # Delete from vector store
            vector_deleted = self.vector_store.delete_user_memories(user_id, companion_id)
            
            # Delete from Firestore
            query = firestore_db.db.collection('memories').where('user_id', '==', user_id)
            if companion_id:
                query = query.where('companion_id', '==', companion_id)
            
            docs = query.stream()
            batch = firestore_db.db.batch()
            
            for doc in docs:
                batch.delete(doc.reference)
            
            batch.commit()
            
            return vector_deleted
            
        except Exception as e:
            print(f"Error deleting all user memories: {e}")
            return False
    
    def get_user_memory_stats(self, user_id: str, companion_id: str = None) -> Dict[str, Any]:
        """Get memory statistics for user"""
        try:
            # Query Firestore for user memories
            query = firestore_db.db.collection('memories').where('user_id', '==', user_id)
            if companion_id:
                query = query.where('companion_id', '==', companion_id)
            
            docs = list(query.stream())
            
            # Calculate statistics
            total_memories = len(docs)
            memory_types = {}
            source_types = {}
            total_content_length = 0
            oldest_memory = None
            newest_memory = None
            
            for doc in docs:
                data = doc.to_dict()
                
                # Count by type
                memory_type = data.get('memory_type', 'unknown')
                memory_types[memory_type] = memory_types.get(memory_type, 0) + 1
                
                source_type = data.get('source_type', 'unknown')
                source_types[source_type] = source_types.get(source_type, 0) + 1
                
                # Content length
                content = data.get('content', '')
                total_content_length += len(content)
                
                # Timestamps
                timestamp_str = data.get('timestamp')
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                        if oldest_memory is None or timestamp < oldest_memory:
                            oldest_memory = timestamp
                        if newest_memory is None or timestamp > newest_memory:
                            newest_memory = timestamp
                    except:
                        pass
            
            return {
                'total_memories': total_memories,
                'memory_types': memory_types,
                'source_types': source_types,
                'total_content_length': total_content_length,
                'average_content_length': total_content_length / total_memories if total_memories > 0 else 0,
                'oldest_memory': oldest_memory.isoformat() if oldest_memory else None,
                'newest_memory': newest_memory.isoformat() if newest_memory else None,
                'companion_id': companion_id
            }
            
        except Exception as e:
            print(f"Error getting user memory stats: {e}")
            return {'error': str(e)}
    
    def search_memories_by_text(self, user_id: str, companion_id: str, search_text: str,
                               limit: int = 20) -> List[Dict[str, Any]]:
        """Search memories by text content (full-text search)"""
        try:
            # Query Firestore for text search
            query = firestore_db.db.collection('memories').where('user_id', '==', user_id)
            if companion_id:
                query = query.where('companion_id', '==', companion_id)
            
            docs = query.stream()
            
            # Filter by text content
            matching_memories = []
            search_terms = search_text.lower().split()
            
            for doc in docs:
                data = doc.to_dict()
                content = data.get('content', '').lower()
                
                # Check if all search terms are in content
                if all(term in content for term in search_terms):
                    matching_memories.append({
                        'id': doc.id,
                        'content': data.get('content', ''),
                        'metadata': data,
                        'score': self._calculate_text_match_score(content, search_terms)
                    })
            
            # Sort by relevance score
            matching_memories.sort(key=lambda x: x['score'], reverse=True)
            
            return matching_memories[:limit]
            
        except Exception as e:
            print(f"Error searching memories by text: {e}")
            return []
    
    def _calculate_text_match_score(self, content: str, search_terms: List[str]) -> float:
        """Calculate text match score for ranking"""
        try:
            content_words = content.split()
            total_words = len(content_words)
            
            if total_words == 0:
                return 0.0
            
            # Count term occurrences
            term_count = 0
            for term in search_terms:
                term_count += content.count(term)
            
            # Calculate score based on term frequency
            score = term_count / total_words
            
            # Boost score for exact phrase matches
            search_phrase = ' '.join(search_terms)
            if search_phrase in content:
                score *= 1.5
            
            return score
            
        except Exception as e:
            return 0.0
    
    def cleanup_old_memories(self, max_age_days: int = None) -> int:
        """Clean up old memories based on retention policies"""
        try:
            if max_age_days is None:
                max_age_days = self.config.DATA_RETENTION_DAYS
            
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            # Query for old memories
            query = firestore_db.db.collection('memories').where('timestamp', '<', cutoff_date)
            docs = list(query.stream())
            
            deleted_count = 0
            batch = firestore_db.db.batch()
            
            for doc in docs:
                data = doc.to_dict()
                retention_policy = data.get('retention_policy', 'long_term')
                
                # Only delete if not long-term retention
                if retention_policy != 'long_term':
                    batch.delete(doc.reference)
                    deleted_count += 1
            
            if deleted_count > 0:
                batch.commit()
                print(f"✅ Cleaned up {deleted_count} old memories")
            
            return deleted_count
            
        except Exception as e:
            print(f"Error cleaning up old memories: {e}")
            return 0
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide memory statistics"""
        try:
            # Get vector store stats
            vector_stats = self.vector_store.get_stats()
            
            # Get embedding service stats
            embedding_stats = self.embedding_service.get_cache_stats()
            
            # Get Firestore stats
            total_memories = len(list(firestore_db.db.collection('memories').stream()))
            
            return {
                'vector_store': vector_stats,
                'embedding_service': embedding_stats,
                'total_memories_firestore': total_memories,
                'system_health': {
                    'vector_store_healthy': self.vector_store.health_check(),
                    'embedding_service_healthy': True,  # Always healthy for now
                    'firestore_healthy': firestore_db is not None
                }
            }
            
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return {'error': str(e)}
    
    def export_user_memories(self, user_id: str, companion_id: str = None) -> Dict[str, Any]:
        """Export all user memories for data portability"""
        try:
            # Query user memories
            query = firestore_db.db.collection('memories').where('user_id', '==', user_id)
            if companion_id:
                query = query.where('companion_id', '==', companion_id)
            
            docs = query.stream()
            
            # Collect all memory data
            memories = []
            for doc in docs:
                memory_data = doc.to_dict()
                memories.append(memory_data)
            
            # Create export package
            export_data = {
                'user_id': user_id,
                'companion_id': companion_id,
                'export_date': datetime.now().isoformat(),
                'total_memories': len(memories),
                'memories': memories,
                'metadata': {
                    'export_version': '1.0',
                    'format': 'json',
                    'privacy_compliant': True
                }
            }
            
            return export_data
            
        except Exception as e:
            print(f"Error exporting user memories: {e}")
            return {'error': str(e)}
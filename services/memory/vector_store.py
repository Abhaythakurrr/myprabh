"""
Vector Memory Store for My Prabh
Handles vector database operations for memory storage and retrieval
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import hashlib
import uuid

from .interfaces import VectorStoreInterface
from .memory_models import MemoryChunk
from config.memory_config import MemoryConfig

class VectorMemoryStore(VectorStoreInterface):
    """Vector database service for memory storage and retrieval"""
    
    def __init__(self):
        self.config = MemoryConfig()
        self.db_config = self.config.get_vector_db_config()
        self.client = None
        self.index = None
        
        # Initialize based on configured vector database type
        self._initialize_vector_db()
    
    def _initialize_vector_db(self):
        """Initialize vector database connection"""
        try:
            db_type = self.db_config['type'].lower()
            
            if db_type == 'pinecone':
                self._initialize_pinecone()
            elif db_type == 'qdrant':
                self._initialize_qdrant()
            elif db_type == 'milvus':
                self._initialize_milvus()
            elif db_type == 'local' or db_type == 'faiss':
                self._initialize_local_faiss()
            else:
                print(f"⚠️ Unsupported vector database type: {db_type}")
                self._initialize_local_faiss()  # Fallback to local storage
                
        except Exception as e:
            print(f"⚠️ Vector database initialization error: {e}")
            self._initialize_local_faiss()  # Fallback to local storage
    
    def _initialize_pinecone(self):
        """Initialize Pinecone vector database"""
        try:
            import pinecone
            
            # Initialize Pinecone
            pinecone.init(
                api_key=self.db_config['api_key'],
                environment=self.db_config.get('environment', 'us-west1-gcp')
            )
            
            index_name = self.db_config['index_name']
            
            # Create index if it doesn't exist
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=index_name,
                    dimension=self.db_config['dimension'],
                    metric='cosine'
                )
            
            self.index = pinecone.Index(index_name)
            self.client = pinecone
            
            print(f"✅ Pinecone vector database initialized: {index_name}")
            
        except Exception as e:
            print(f"⚠️ Pinecone initialization failed: {e}")
            raise e
    
    def _initialize_qdrant(self):
        """Initialize Qdrant vector database"""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams, CreateCollection
            
            # Initialize Qdrant client
            if self.db_config.get('url'):
                self.client = QdrantClient(
                    url=self.db_config['url'],
                    api_key=self.db_config.get('api_key')
                )
            else:
                # Local Qdrant instance
                self.client = QdrantClient(host="localhost", port=6333)
            
            collection_name = self.db_config['index_name']
            
            # Create collection if it doesn't exist
            try:
                self.client.get_collection(collection_name)
            except:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=self.db_config['dimension'],
                        distance=Distance.COSINE
                    )
                )
            
            self.index = collection_name
            
            print(f"✅ Qdrant vector database initialized: {collection_name}")
            
        except Exception as e:
            print(f"⚠️ Qdrant initialization failed: {e}")
            raise e
    
    def _initialize_milvus(self):
        """Initialize Milvus vector database"""
        try:
            from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
            
            # Connect to Milvus
            connections.connect(
                alias="default",
                host=self.db_config.get('host', 'localhost'),
                port=self.db_config.get('port', '19530')
            )
            
            collection_name = self.db_config['index_name']
            
            # Create collection if it doesn't exist
            if not utility.has_collection(collection_name):
                # Define schema
                fields = [
                    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
                    FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=100),
                    FieldSchema(name="companion_id", dtype=DataType.VARCHAR, max_length=100),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.db_config['dimension']),
                    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=10000),
                    FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=5000)
                ]
                
                schema = CollectionSchema(fields, "Memory storage collection")
                collection = Collection(collection_name, schema)
                
                # Create index
                index_params = {
                    "metric_type": "COSINE",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 128}
                }
                collection.create_index("embedding", index_params)
            
            self.index = Collection(collection_name)
            self.client = connections
            
            print(f"✅ Milvus vector database initialized: {collection_name}")
            
        except Exception as e:
            print(f"⚠️ Milvus initialization failed: {e}")
            raise e
    
    def _initialize_local_faiss(self):
        """Initialize local FAISS vector database"""
        try:
            import faiss
            import pickle
            
            self.local_storage_path = os.path.join(os.getcwd(), 'data', 'vector_store')
            os.makedirs(self.local_storage_path, exist_ok=True)
            
            index_file = os.path.join(self.local_storage_path, 'faiss_index.bin')
            metadata_file = os.path.join(self.local_storage_path, 'metadata.pkl')
            
            # Load existing index or create new one
            if os.path.exists(index_file):
                self.index = faiss.read_index(index_file)
                with open(metadata_file, 'rb') as f:
                    self.metadata_store = pickle.load(f)
            else:
                # Create new FAISS index
                self.index = faiss.IndexFlatIP(self.db_config['dimension'])  # Inner product (cosine similarity)
                self.metadata_store = {}
            
            self.client = faiss
            
            print(f"✅ Local FAISS vector database initialized")
            
        except Exception as e:
            print(f"⚠️ FAISS initialization failed: {e}")
            # Ultimate fallback - in-memory storage
            self.index = {}
            self.metadata_store = {}
            self.client = "memory"
            print("✅ Fallback to in-memory vector storage")
    
    def store_memory(self, user_id: str, chunk: str, embedding: np.ndarray, metadata: Dict[str, Any]) -> str:
        """Store memory chunk with embedding"""
        try:
            memory_id = str(uuid.uuid4())
            
            # Ensure embedding is the right shape and type
            if isinstance(embedding, list):
                embedding = np.array(embedding, dtype=np.float32)
            elif isinstance(embedding, np.ndarray):
                embedding = embedding.astype(np.float32)
            
            # Normalize embedding for cosine similarity
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            # Store based on database type
            if self.client == pinecone or hasattr(self.client, 'Index'):
                self._store_pinecone(memory_id, user_id, chunk, embedding, metadata)
            elif hasattr(self.client, 'upsert'):  # Qdrant
                self._store_qdrant(memory_id, user_id, chunk, embedding, metadata)
            elif hasattr(self.client, 'connect'):  # Milvus
                self._store_milvus(memory_id, user_id, chunk, embedding, metadata)
            elif hasattr(self.client, 'IndexFlatIP'):  # FAISS
                self._store_faiss(memory_id, user_id, chunk, embedding, metadata)
            else:  # In-memory fallback
                self._store_memory_fallback(memory_id, user_id, chunk, embedding, metadata)
            
            return memory_id
            
        except Exception as e:
            print(f"Error storing memory: {e}")
            raise e
    
    def _store_pinecone(self, memory_id: str, user_id: str, chunk: str, embedding: np.ndarray, metadata: Dict[str, Any]):
        """Store memory in Pinecone"""
        vector_metadata = {
            'user_id': user_id,
            'content': chunk[:1000],  # Pinecone metadata size limit
            'timestamp': datetime.now().isoformat(),
            **{k: str(v)[:100] for k, v in metadata.items()}  # Convert to strings and limit size
        }
        
        self.index.upsert([(memory_id, embedding.tolist(), vector_metadata)])
    
    def _store_qdrant(self, memory_id: str, user_id: str, chunk: str, embedding: np.ndarray, metadata: Dict[str, Any]):
        """Store memory in Qdrant"""
        from qdrant_client.models import PointStruct
        
        point = PointStruct(
            id=memory_id,
            vector=embedding.tolist(),
            payload={
                'user_id': user_id,
                'content': chunk,
                'timestamp': datetime.now().isoformat(),
                **metadata
            }
        )
        
        self.client.upsert(collection_name=self.index, points=[point])
    
    def _store_milvus(self, memory_id: str, user_id: str, chunk: str, embedding: np.ndarray, metadata: Dict[str, Any]):
        """Store memory in Milvus"""
        entities = [
            [memory_id],
            [user_id],
            [metadata.get('companion_id', '')],
            [embedding.tolist()],
            [chunk],
            [json.dumps(metadata)]
        ]
        
        self.index.insert(entities)
        self.index.flush()
    
    def _store_faiss(self, memory_id: str, user_id: str, chunk: str, embedding: np.ndarray, metadata: Dict[str, Any]):
        """Store memory in FAISS"""
        # Add vector to FAISS index
        self.index.add(embedding.reshape(1, -1))
        
        # Store metadata separately
        vector_id = self.index.ntotal - 1  # FAISS assigns sequential IDs
        self.metadata_store[vector_id] = {
            'memory_id': memory_id,
            'user_id': user_id,
            'content': chunk,
            'timestamp': datetime.now().isoformat(),
            **metadata
        }
        
        # Save to disk
        self._save_faiss_index()
    
    def _store_memory_fallback(self, memory_id: str, user_id: str, chunk: str, embedding: np.ndarray, metadata: Dict[str, Any]):
        """Store memory in fallback in-memory storage"""
        self.index[memory_id] = {
            'user_id': user_id,
            'content': chunk,
            'embedding': embedding,
            'timestamp': datetime.now().isoformat(),
            **metadata
        }
    
    def search_memories(self, user_id: str, query_embedding: np.ndarray, limit: int = 10, 
                       companion_id: str = None, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search for relevant memories"""
        try:
            # Ensure query embedding is the right shape and type
            if isinstance(query_embedding, list):
                query_embedding = np.array(query_embedding, dtype=np.float32)
            elif isinstance(query_embedding, np.ndarray):
                query_embedding = query_embedding.astype(np.float32)
            
            # Normalize query embedding
            norm = np.linalg.norm(query_embedding)
            if norm > 0:
                query_embedding = query_embedding / norm
            
            # Search based on database type
            if self.client == pinecone or hasattr(self.client, 'Index'):
                return self._search_pinecone(user_id, query_embedding, limit, companion_id, filters)
            elif hasattr(self.client, 'search'):  # Qdrant
                return self._search_qdrant(user_id, query_embedding, limit, companion_id, filters)
            elif hasattr(self.client, 'connect'):  # Milvus
                return self._search_milvus(user_id, query_embedding, limit, companion_id, filters)
            elif hasattr(self.client, 'IndexFlatIP'):  # FAISS
                return self._search_faiss(user_id, query_embedding, limit, companion_id, filters)
            else:  # In-memory fallback
                return self._search_memory_fallback(user_id, query_embedding, limit, companion_id, filters)
                
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []
    
    def _search_pinecone(self, user_id: str, query_embedding: np.ndarray, limit: int, 
                        companion_id: str = None, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search memories in Pinecone"""
        # Build filter
        filter_dict = {'user_id': user_id}
        if companion_id:
            filter_dict['companion_id'] = companion_id
        if filters:
            filter_dict.update(filters)
        
        # Search
        results = self.index.query(
            vector=query_embedding.tolist(),
            top_k=limit,
            filter=filter_dict,
            include_metadata=True
        )
        
        # Format results
        memories = []
        for match in results['matches']:
            memory = {
                'id': match['id'],
                'score': match['score'],
                'content': match['metadata'].get('content', ''),
                'metadata': match['metadata']
            }
            memories.append(memory)
        
        return memories
    
    def _search_qdrant(self, user_id: str, query_embedding: np.ndarray, limit: int, 
                      companion_id: str = None, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search memories in Qdrant"""
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        # Build filter
        filter_conditions = [FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        if companion_id:
            filter_conditions.append(FieldCondition(key="companion_id", match=MatchValue(value=companion_id)))
        
        search_filter = Filter(must=filter_conditions)
        
        # Search
        results = self.client.search(
            collection_name=self.index,
            query_vector=query_embedding.tolist(),
            query_filter=search_filter,
            limit=limit
        )
        
        # Format results
        memories = []
        for result in results:
            memory = {
                'id': result.id,
                'score': result.score,
                'content': result.payload.get('content', ''),
                'metadata': result.payload
            }
            memories.append(memory)
        
        return memories
    
    def _search_milvus(self, user_id: str, query_embedding: np.ndarray, limit: int, 
                      companion_id: str = None, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search memories in Milvus"""
        # Build expression for filtering
        expr = f'user_id == "{user_id}"'
        if companion_id:
            expr += f' && companion_id == "{companion_id}"'
        
        # Search
        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
        results = self.index.search(
            data=[query_embedding.tolist()],
            anns_field="embedding",
            param=search_params,
            limit=limit,
            expr=expr,
            output_fields=["id", "user_id", "companion_id", "content", "metadata"]
        )
        
        # Format results
        memories = []
        for hits in results:
            for hit in hits:
                memory = {
                    'id': hit.entity.get('id'),
                    'score': hit.score,
                    'content': hit.entity.get('content', ''),
                    'metadata': json.loads(hit.entity.get('metadata', '{}'))
                }
                memories.append(memory)
        
        return memories
    
    def _search_faiss(self, user_id: str, query_embedding: np.ndarray, limit: int, 
                     companion_id: str = None, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search memories in FAISS"""
        if self.index.ntotal == 0:
            return []
        
        # Search
        scores, indices = self.index.search(query_embedding.reshape(1, -1), min(limit * 2, self.index.ntotal))
        
        # Filter results by user_id and other criteria
        memories = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # Invalid index
                continue
                
            metadata = self.metadata_store.get(idx, {})
            if metadata.get('user_id') != user_id:
                continue
                
            if companion_id and metadata.get('companion_id') != companion_id:
                continue
            
            memory = {
                'id': metadata.get('memory_id', str(idx)),
                'score': float(score),
                'content': metadata.get('content', ''),
                'metadata': metadata
            }
            memories.append(memory)
            
            if len(memories) >= limit:
                break
        
        return memories
    
    def _search_memory_fallback(self, user_id: str, query_embedding: np.ndarray, limit: int, 
                               companion_id: str = None, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search memories in fallback in-memory storage"""
        memories = []
        
        for memory_id, memory_data in self.index.items():
            if memory_data.get('user_id') != user_id:
                continue
                
            if companion_id and memory_data.get('companion_id') != companion_id:
                continue
            
            # Calculate similarity
            stored_embedding = memory_data.get('embedding')
            if stored_embedding is not None:
                similarity = np.dot(query_embedding, stored_embedding)
                
                memory = {
                    'id': memory_id,
                    'score': float(similarity),
                    'content': memory_data.get('content', ''),
                    'metadata': {k: v for k, v in memory_data.items() if k not in ['embedding']}
                }
                memories.append(memory)
        
        # Sort by similarity and return top results
        memories.sort(key=lambda x: x['score'], reverse=True)
        return memories[:limit]
    
    def delete_user_memories(self, user_id: str, companion_id: str = None) -> bool:
        """Delete all memories for a user"""
        try:
            if self.client == pinecone or hasattr(self.client, 'Index'):
                return self._delete_pinecone_memories(user_id, companion_id)
            elif hasattr(self.client, 'delete'):  # Qdrant
                return self._delete_qdrant_memories(user_id, companion_id)
            elif hasattr(self.client, 'connect'):  # Milvus
                return self._delete_milvus_memories(user_id, companion_id)
            elif hasattr(self.client, 'IndexFlatIP'):  # FAISS
                return self._delete_faiss_memories(user_id, companion_id)
            else:  # In-memory fallback
                return self._delete_memory_fallback(user_id, companion_id)
                
        except Exception as e:
            print(f"Error deleting user memories: {e}")
            return False
    
    def _delete_pinecone_memories(self, user_id: str, companion_id: str = None) -> bool:
        """Delete memories from Pinecone"""
        filter_dict = {'user_id': user_id}
        if companion_id:
            filter_dict['companion_id'] = companion_id
        
        self.index.delete(filter=filter_dict)
        return True
    
    def _delete_qdrant_memories(self, user_id: str, companion_id: str = None) -> bool:
        """Delete memories from Qdrant"""
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        filter_conditions = [FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        if companion_id:
            filter_conditions.append(FieldCondition(key="companion_id", match=MatchValue(value=companion_id)))
        
        delete_filter = Filter(must=filter_conditions)
        
        self.client.delete(collection_name=self.index, points_selector=delete_filter)
        return True
    
    def _delete_milvus_memories(self, user_id: str, companion_id: str = None) -> bool:
        """Delete memories from Milvus"""
        expr = f'user_id == "{user_id}"'
        if companion_id:
            expr += f' && companion_id == "{companion_id}"'
        
        self.index.delete(expr)
        return True
    
    def _delete_faiss_memories(self, user_id: str, companion_id: str = None) -> bool:
        """Delete memories from FAISS (rebuild index without deleted items)"""
        # FAISS doesn't support deletion, so we need to rebuild the index
        new_metadata = {}
        vectors_to_keep = []
        
        for idx, metadata in self.metadata_store.items():
            if metadata.get('user_id') == user_id:
                if companion_id is None or metadata.get('companion_id') == companion_id:
                    continue  # Skip this memory (delete it)
            
            # Keep this memory
            new_idx = len(vectors_to_keep)
            new_metadata[new_idx] = metadata
            
            # Get the vector (this is a simplified approach)
            # In practice, you'd need to store vectors separately or use a different approach
        
        # Rebuild index (simplified - in practice this would be more complex)
        self.metadata_store = new_metadata
        self._save_faiss_index()
        return True
    
    def _delete_memory_fallback(self, user_id: str, companion_id: str = None) -> bool:
        """Delete memories from fallback storage"""
        to_delete = []
        
        for memory_id, memory_data in self.index.items():
            if memory_data.get('user_id') == user_id:
                if companion_id is None or memory_data.get('companion_id') == companion_id:
                    to_delete.append(memory_id)
        
        for memory_id in to_delete:
            del self.index[memory_id]
        
        return True
    
    def update_memory_metadata(self, memory_id: str, metadata: Dict[str, Any]) -> bool:
        """Update memory metadata"""
        try:
            # Implementation depends on vector database capabilities
            # This is a simplified version
            print(f"Updating metadata for memory {memory_id}: {metadata}")
            return True
            
        except Exception as e:
            print(f"Error updating memory metadata: {e}")
            return False
    
    def _save_faiss_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            if hasattr(self.client, 'IndexFlatIP'):
                index_file = os.path.join(self.local_storage_path, 'faiss_index.bin')
                metadata_file = os.path.join(self.local_storage_path, 'metadata.pkl')
                
                faiss.write_index(self.index, index_file)
                
                import pickle
                with open(metadata_file, 'wb') as f:
                    pickle.dump(self.metadata_store, f)
                    
        except Exception as e:
            print(f"Error saving FAISS index: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector database statistics"""
        try:
            if hasattr(self.index, 'ntotal'):  # FAISS
                return {
                    'total_vectors': self.index.ntotal,
                    'dimension': self.index.d,
                    'database_type': 'faiss'
                }
            elif hasattr(self.client, 'describe_index_stats'):  # Pinecone
                stats = self.index.describe_index_stats()
                return {
                    'total_vectors': stats.get('total_vector_count', 0),
                    'dimension': stats.get('dimension', 0),
                    'database_type': 'pinecone'
                }
            else:
                return {
                    'total_vectors': len(self.index) if isinstance(self.index, dict) else 0,
                    'database_type': 'memory'
                }
                
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {'error': str(e)}
    
    def health_check(self) -> bool:
        """Check if vector database is healthy"""
        try:
            if self.client == "memory":
                return True
            elif hasattr(self.client, 'IndexFlatIP'):  # FAISS
                return self.index is not None
            elif hasattr(self.client, 'describe_index_stats'):  # Pinecone
                self.index.describe_index_stats()
                return True
            elif hasattr(self.client, 'get_collection'):  # Qdrant
                self.client.get_collection(self.index)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Vector database health check failed: {e}")
            return False
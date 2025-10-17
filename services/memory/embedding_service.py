"""
Embedding Generation Service for My Prabh
Handles text embedding generation for memory storage and retrieval
"""

import os
import numpy as np
from typing import List, Dict, Any, Optional, Union
import hashlib
import pickle
from datetime import datetime

from config.memory_config import MemoryConfig

class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self):
        self.config = MemoryConfig()
        self.embedding_config = self.config.get_embedding_config()
        self.model = None
        self.cache = {}
        self.cache_file = os.path.join(os.getcwd(), 'data', 'embedding_cache.pkl')
        
        # Load cache if it exists
        self._load_cache()
        
        # Initialize embedding model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model"""
        try:
            model_name = self.embedding_config['model']
            
            if model_name.startswith('sentence-transformers/'):
                self._initialize_sentence_transformers(model_name)
            elif model_name.startswith('openai/'):
                self._initialize_openai_embeddings()
            elif model_name.startswith('huggingface/'):
                self._initialize_huggingface_model(model_name)
            else:
                # Default to sentence-transformers
                self._initialize_sentence_transformers('sentence-transformers/all-MiniLM-L6-v2')
                
        except Exception as e:
            print(f"⚠️ Embedding model initialization failed: {e}")
            print("⚠️ Falling back to simple embedding method")
            self.model = "simple"
    
    def _initialize_sentence_transformers(self, model_name: str):
        """Initialize SentenceTransformers model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Remove the prefix if present
            if model_name.startswith('sentence-transformers/'):
                model_name = model_name.replace('sentence-transformers/', '')
            
            self.model = SentenceTransformer(model_name)
            print(f"✅ SentenceTransformers model loaded: {model_name}")
            
        except ImportError:
            print("⚠️ sentence-transformers not installed. Install with: pip install sentence-transformers")
            raise
        except Exception as e:
            print(f"⚠️ Error loading SentenceTransformers model: {e}")
            raise
    
    def _initialize_openai_embeddings(self):
        """Initialize OpenAI embeddings"""
        try:
            import openai
            
            self.model = "openai"
            self.openai_client = openai.OpenAI(
                api_key=os.environ.get('OPENAI_API_KEY')
            )
            print("✅ OpenAI embeddings initialized")
            
        except ImportError:
            print("⚠️ openai not installed. Install with: pip install openai")
            raise
        except Exception as e:
            print(f"⚠️ Error initializing OpenAI embeddings: {e}")
            raise
    
    def _initialize_huggingface_model(self, model_name: str):
        """Initialize HuggingFace model"""
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch
            
            # Remove the prefix if present
            if model_name.startswith('huggingface/'):
                model_name = model_name.replace('huggingface/', '')
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.model.to(self.device)
            
            print(f"✅ HuggingFace model loaded: {model_name}")
            
        except ImportError:
            print("⚠️ transformers not installed. Install with: pip install transformers torch")
            raise
        except Exception as e:
            print(f"⚠️ Error loading HuggingFace model: {e}")
            raise
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        try:
            # Check cache first
            text_hash = self._hash_text(text)
            if text_hash in self.cache:
                return self.cache[text_hash]
            
            # Generate embedding based on model type
            if hasattr(self.model, 'encode'):  # SentenceTransformers
                embedding = self._generate_sentence_transformer_embedding(text)
            elif self.model == "openai":
                embedding = self._generate_openai_embedding(text)
            elif hasattr(self.model, 'forward'):  # HuggingFace
                embedding = self._generate_huggingface_embedding(text)
            else:  # Simple fallback
                embedding = self._generate_simple_embedding(text)
            
            # Cache the result
            self.cache[text_hash] = embedding
            self._save_cache()
            
            return embedding
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Fallback to simple embedding
            return self._generate_simple_embedding(text)
    
    def generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts (batch processing)"""
        try:
            # Check which texts are already cached
            uncached_texts = []
            uncached_indices = []
            results = [None] * len(texts)
            
            for i, text in enumerate(texts):
                text_hash = self._hash_text(text)
                if text_hash in self.cache:
                    results[i] = self.cache[text_hash]
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
            
            # Generate embeddings for uncached texts
            if uncached_texts:
                if hasattr(self.model, 'encode'):  # SentenceTransformers
                    new_embeddings = self._generate_sentence_transformer_embeddings_batch(uncached_texts)
                elif self.model == "openai":
                    new_embeddings = self._generate_openai_embeddings_batch(uncached_texts)
                elif hasattr(self.model, 'forward'):  # HuggingFace
                    new_embeddings = self._generate_huggingface_embeddings_batch(uncached_texts)
                else:  # Simple fallback
                    new_embeddings = [self._generate_simple_embedding(text) for text in uncached_texts]
                
                # Store results and cache
                for i, embedding in enumerate(new_embeddings):
                    idx = uncached_indices[i]
                    results[idx] = embedding
                    
                    # Cache the result
                    text_hash = self._hash_text(uncached_texts[i])
                    self.cache[text_hash] = embedding
                
                self._save_cache()
            
            return results
            
        except Exception as e:
            print(f"Error generating batch embeddings: {e}")
            # Fallback to individual processing
            return [self.generate_embedding(text) for text in texts]
    
    def _generate_sentence_transformer_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using SentenceTransformers"""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)
    
    def _generate_sentence_transformer_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using SentenceTransformers (batch)"""
        embeddings = self.model.encode(texts, convert_to_numpy=True, batch_size=32)
        return [embedding.astype(np.float32) for embedding in embeddings]
    
    def _generate_openai_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using OpenAI API"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            return embedding
            
        except Exception as e:
            print(f"OpenAI embedding error: {e}")
            return self._generate_simple_embedding(text)
    
    def _generate_openai_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using OpenAI API (batch)"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            
            embeddings = []
            for data in response.data:
                embedding = np.array(data.embedding, dtype=np.float32)
                embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            print(f"OpenAI batch embedding error: {e}")
            return [self._generate_simple_embedding(text) for text in texts]
    
    def _generate_huggingface_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using HuggingFace model"""
        try:
            import torch
            
            # Tokenize
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True, 
                                  padding=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate embedding
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use mean pooling of last hidden states
                embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
            
            return embedding.cpu().numpy().astype(np.float32)
            
        except Exception as e:
            print(f"HuggingFace embedding error: {e}")
            return self._generate_simple_embedding(text)
    
    def _generate_huggingface_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using HuggingFace model (batch)"""
        try:
            import torch
            
            # Tokenize batch
            inputs = self.tokenizer(texts, return_tensors='pt', truncation=True, 
                                  padding=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use mean pooling of last hidden states
                embeddings = outputs.last_hidden_state.mean(dim=1)
            
            return [emb.cpu().numpy().astype(np.float32) for emb in embeddings]
            
        except Exception as e:
            print(f"HuggingFace batch embedding error: {e}")
            return [self._generate_simple_embedding(text) for text in texts]
    
    def _generate_simple_embedding(self, text: str) -> np.ndarray:
        """Generate simple embedding (fallback method)"""
        try:
            from collections import Counter
            import re
            
            # Simple bag-of-words embedding
            words = re.findall(r'\w+', text.lower())
            word_counts = Counter(words)
            
            # Create embedding vector
            embedding = np.zeros(self.embedding_config['dimension'], dtype=np.float32)
            
            for word, count in word_counts.items():
                # Simple hash function to map words to dimensions
                word_hash = hash(word) % self.embedding_config['dimension']
                embedding[word_hash] += count
            
            # Normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            return embedding
            
        except Exception as e:
            print(f"Simple embedding error: {e}")
            # Ultimate fallback - random embedding
            return np.random.normal(0, 0.1, self.embedding_config['dimension']).astype(np.float32)
    
    def _hash_text(self, text: str) -> str:
        """Generate hash for text caching"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _load_cache(self):
        """Load embedding cache from disk"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    self.cache = pickle.load(f)
                print(f"✅ Loaded {len(self.cache)} cached embeddings")
            else:
                self.cache = {}
        except Exception as e:
            print(f"⚠️ Error loading embedding cache: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """Save embedding cache to disk"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
        except Exception as e:
            print(f"⚠️ Error saving embedding cache: {e}")
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Ensure embeddings are normalized
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            embedding1_norm = embedding1 / norm1
            embedding2_norm = embedding2 / norm2
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1_norm, embedding2_norm)
            
            return float(similarity)
            
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def find_most_similar(self, query_embedding: np.ndarray, 
                         candidate_embeddings: List[np.ndarray], 
                         top_k: int = 5) -> List[tuple]:
        """Find most similar embeddings to query"""
        try:
            similarities = []
            
            for i, candidate in enumerate(candidate_embeddings):
                similarity = self.calculate_similarity(query_embedding, candidate)
                similarities.append((i, similarity))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            print(f"Error finding similar embeddings: {e}")
            return []
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this service"""
        return self.embedding_config['dimension']
    
    def clear_cache(self):
        """Clear the embedding cache"""
        self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        print("✅ Embedding cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        cache_size_mb = 0
        if os.path.exists(self.cache_file):
            cache_size_mb = os.path.getsize(self.cache_file) / (1024 * 1024)
        
        return {
            'cached_embeddings': len(self.cache),
            'cache_size_mb': round(cache_size_mb, 2),
            'model_type': type(self.model).__name__ if hasattr(self.model, '__class__') else str(self.model),
            'embedding_dimension': self.get_embedding_dimension()
        }
    
    def benchmark_performance(self, test_texts: List[str] = None) -> Dict[str, Any]:
        """Benchmark embedding generation performance"""
        import time
        
        if test_texts is None:
            test_texts = [
                "This is a short test sentence.",
                "This is a longer test sentence with more words to process and analyze.",
                "Memory processing and embedding generation are important for AI systems.",
                "The quick brown fox jumps over the lazy dog in the beautiful garden.",
                "Artificial intelligence and machine learning are transforming technology."
            ]
        
        # Single embedding benchmark
        start_time = time.time()
        single_embedding = self.generate_embedding(test_texts[0])
        single_time = time.time() - start_time
        
        # Batch embedding benchmark
        start_time = time.time()
        batch_embeddings = self.generate_embeddings(test_texts)
        batch_time = time.time() - start_time
        
        return {
            'single_embedding_time': round(single_time, 4),
            'batch_embedding_time': round(batch_time, 4),
            'batch_size': len(test_texts),
            'avg_time_per_embedding': round(batch_time / len(test_texts), 4),
            'embedding_dimension': len(single_embedding),
            'speedup_factor': round(single_time * len(test_texts) / batch_time, 2) if batch_time > 0 else 0
        }
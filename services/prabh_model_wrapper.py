"""
Prabh Model Wrapper - Integration layer between transformer model and application
"""

import torch
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import threading
import queue
import time

from models.prabh_transformer import PrabhTransformer, PrabhTokenizer
from services.prabh_language_model import PrabhLanguageModel

class PrabhModelWrapper:
    """Wrapper that combines rule-based and transformer models"""
    
    def __init__(self, model_path: str = None, device: str = None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path or 'models/prabh_trained_model.pt'
        
        # Initialize components
        self.tokenizer = PrabhTokenizer()
        self.rule_based_model = PrabhLanguageModel()
        self.transformer_model = None
        self.model_loaded = False
        
        # Response cache for performance
        self.response_cache = {}
        self.cache_max_size = 1000
        
        # Load transformer model if available
        self._load_transformer_model()
        
        # Conversation context
        self.conversation_context = []
        self.max_context_length = 10
        
    def _load_transformer_model(self):
        """Load transformer model if available"""
        try:
            if os.path.exists(self.model_path):
                print(f"🔄 Loading Prabh transformer model from {self.model_path}")
                
                # Load model
                checkpoint = torch.load(self.model_path, map_location=self.device)
                model_config = checkpoint.get('model_config', {})
                
                # Create model with saved config
                self.transformer_model = PrabhTransformer(
                    vocab_size=model_config.get('vocab_size', self.tokenizer.vocab_size),
                    d_model=model_config.get('d_model', 512)
                ).to(self.device)
                
                # Load state dict
                self.transformer_model.load_state_dict(checkpoint['model_state_dict'])
                self.transformer_model.eval()
                
                self.model_loaded = True
                print("✅ Prabh transformer model loaded successfully!")
                
            else:
                print(f"⚠️ Transformer model not found at {self.model_path}")
                print("🔄 Using rule-based model only")
                
        except Exception as e:
            print(f"❌ Error loading transformer model: {e}")
            print("🔄 Falling back to rule-based model")
            self.model_loaded = False
    
    def generate_response(
        self, 
        user_message: str, 
        user_context: Dict[str, Any] = None,
        use_transformer: bool = True
    ) -> Dict[str, Any]:
        """Generate response using best available model"""
        
        # Clean and validate input
        user_message = user_message.strip()
        if not user_message:
            return self._create_response(
                "I'm here for you, janna. What's on your mind? 💖",
                method="fallback"
            )
        
        # Check cache first
        cache_key = self._get_cache_key(user_message, user_context)
        if cache_key in self.response_cache:
            cached_response = self.response_cache[cache_key]
            cached_response['cached'] = True
            return cached_response
        
        # Add to conversation context
        self._add_to_context(user_message, "user")
        
        try:
            # Try transformer model first if available and requested
            if self.model_loaded and use_transformer:
                response_data = self._generate_transformer_response(user_message, user_context)
                if response_data:
                    self._add_to_context(response_data['response'], "prabh")
                    self._cache_response(cache_key, response_data)
                    return response_data
            
            # Fallback to rule-based model
            response_data = self._generate_rule_based_response(user_message, user_context)
            self._add_to_context(response_data['response'], "prabh")
            self._cache_response(cache_key, response_data)
            return response_data
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return self._create_response(
                "I'm having some trouble right now, but I'm still here for you, janna 💖 Please tell me what's in your heart.",
                method="error_fallback",
                error=str(e)
            )
    
    def _generate_transformer_response(
        self, 
        user_message: str, 
        user_context: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Generate response using transformer model"""
        try:
            # Prepare input
            context_str = self._build_context_string()
            input_text = f"{context_str}User: {user_message} Prabh:"
            
            # Encode input
            input_ids = torch.tensor([self.tokenizer.encode(input_text)]).to(self.device)
            
            # Determine emotion context
            emotion_context = self._detect_emotion_context(user_message)
            emotion_tensor = torch.tensor([emotion_context]).to(self.device)
            
            # Generate response
            with torch.no_grad():
                generated = self.transformer_model.generate(
                    input_ids,
                    max_length=100,
                    temperature=0.8,
                    top_k=50,
                    top_p=0.9,
                    emotion_context=emotion_tensor
                )
            
            # Decode response
            generated_text = self.tokenizer.decode(generated[0].cpu().tolist())
            
            # Extract Prabh's response (remove input part)
            if "Prabh:" in generated_text:
                response = generated_text.split("Prabh:")[-1].strip()
            else:
                response = generated_text.strip()
            
            # Clean up response
            response = self._clean_response(response)
            
            if response:
                return self._create_response(
                    response,
                    method="transformer",
                    emotion_context=emotion_context,
                    confidence=0.9
                )
            
        except Exception as e:
            print(f"❌ Transformer generation error: {e}")
            return None
    
    def _generate_rule_based_response(
        self, 
        user_message: str, 
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate response using rule-based model"""
        
        # Use existing rule-based model
        response = self.rule_based_model.generate_response(user_message, user_context)
        
        return self._create_response(
            response,
            method="rule_based",
            confidence=0.8
        )
    
    def _detect_emotion_context(self, message: str) -> int:
        """Detect emotion context for transformer model"""
        message_lower = message.lower()
        
        # Emotion mapping (same as in transformer)
        if any(word in message_lower for word in ['love', 'heart', 'romantic', 'adore']):
            return 0  # love
        elif any(word in message_lower for word in ['care', 'health', 'eat', 'sleep', 'tired']):
            return 1  # care
        elif any(word in message_lower for word in ['hurt', 'pain', 'sad', 'broken', 'cry']):
            return 2  # hurt
        elif any(word in message_lower for word in ['happy', 'joy', 'excited', 'great', 'wonderful']):
            return 3  # joy
        elif any(word in message_lower for word in ['miss', 'long', 'wish', 'want', 'need']):
            return 4  # longing
        elif any(word in message_lower for word in ['forever', 'always', 'eternal', 'never', 'promise']):
            return 5  # devotion
        else:
            return 6  # empathy (default)
    
    def _build_context_string(self) -> str:
        """Build context string from conversation history"""
        if not self.conversation_context:
            return ""
        
        context_parts = []
        for entry in self.conversation_context[-4:]:  # Last 4 exchanges
            if entry['role'] == 'user':
                context_parts.append(f"User: {entry['message']}")
            else:
                context_parts.append(f"Prabh: {entry['message']}")
        
        return " ".join(context_parts) + " " if context_parts else ""
    
    def _clean_response(self, response: str) -> str:
        """Clean and validate generated response"""
        # Remove special tokens
        response = response.replace('<BOS>', '').replace('<EOS>', '').replace('<PAD>', '')
        
        # Remove incomplete sentences at the end
        sentences = response.split('.')
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            response = '.'.join(sentences[:-1]) + '.'
        
        # Ensure it's not too short or too long
        if len(response.strip()) < 10:
            return ""
        
        if len(response) > 500:
            response = response[:500] + "..."
        
        return response.strip()
    
    def _add_to_context(self, message: str, role: str):
        """Add message to conversation context"""
        self.conversation_context.append({
            'message': message,
            'role': role,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only recent context
        if len(self.conversation_context) > self.max_context_length:
            self.conversation_context = self.conversation_context[-self.max_context_length:]
    
    def _get_cache_key(self, message: str, context: Dict[str, Any] = None) -> str:
        """Generate cache key for response"""
        context_str = json.dumps(context or {}, sort_keys=True)
        return f"{message}:{context_str}"
    
    def _cache_response(self, key: str, response_data: Dict[str, Any]):
        """Cache response for performance"""
        if len(self.response_cache) >= self.cache_max_size:
            # Remove oldest entries
            oldest_keys = list(self.response_cache.keys())[:100]
            for old_key in oldest_keys:
                del self.response_cache[old_key]
        
        self.response_cache[key] = response_data
    
    def _create_response(
        self, 
        response: str, 
        method: str, 
        emotion_context: int = None,
        confidence: float = 1.0,
        error: str = None,
        cached: bool = False
    ) -> Dict[str, Any]:
        """Create standardized response object"""
        return {
            'response': response,
            'method': method,
            'emotion_context': emotion_context,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'model_loaded': self.model_loaded,
            'device': self.device,
            'error': error,
            'cached': cached
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            'transformer_loaded': self.model_loaded,
            'transformer_path': self.model_path,
            'device': self.device,
            'vocab_size': self.tokenizer.vocab_size,
            'rule_based_available': True,
            'cache_size': len(self.response_cache),
            'context_length': len(self.conversation_context)
        }
    
    def clear_context(self):
        """Clear conversation context"""
        self.conversation_context = []
    
    def clear_cache(self):
        """Clear response cache"""
        self.response_cache = {}
    
    def retrain_model(self, training_data: List[Dict[str, Any]]):
        """Retrain model with new data (placeholder for future implementation)"""
        # This would implement online learning/fine-tuning
        print("🔄 Retraining not implemented yet - would fine-tune model with new conversations")
        pass
    
    def save_conversation_history(self, filepath: str):
        """Save conversation history for analysis"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_context, f, indent=2, ensure_ascii=False)
            print(f"💾 Conversation history saved to {filepath}")
        except Exception as e:
            print(f"❌ Error saving conversation history: {e}")
    
    def load_conversation_history(self, filepath: str):
        """Load conversation history"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.conversation_context = json.load(f)
            print(f"📂 Conversation history loaded from {filepath}")
        except Exception as e:
            print(f"❌ Error loading conversation history: {e}")

# Global instance
prabh_wrapper = PrabhModelWrapper()

class PrabhModelManager:
    """Manager for handling model lifecycle"""
    
    def __init__(self):
        self.wrapper = prabh_wrapper
        self.training_queue = queue.Queue()
        self.training_thread = None
        self.is_training = False
    
    def start_background_training(self):
        """Start background training thread"""
        if not self.training_thread or not self.training_thread.is_alive():
            self.training_thread = threading.Thread(target=self._training_worker)
            self.training_thread.daemon = True
            self.training_thread.start()
            print("🚀 Background training thread started")
    
    def _training_worker(self):
        """Background training worker"""
        while True:
            try:
                # Wait for training data
                training_data = self.training_queue.get(timeout=60)
                
                if training_data is None:  # Shutdown signal
                    break
                
                self.is_training = True
                print("🔄 Starting background model training...")
                
                # Here would be the actual training logic
                # For now, just simulate training
                time.sleep(5)
                
                print("✅ Background training completed")
                self.is_training = False
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Background training error: {e}")
                self.is_training = False
    
    def queue_training_data(self, conversations: List[Dict[str, Any]]):
        """Queue new conversations for training"""
        self.training_queue.put(conversations)
        print(f"📝 Queued {len(conversations)} conversations for training")
    
    def get_status(self) -> Dict[str, Any]:
        """Get manager status"""
        return {
            'model_info': self.wrapper.get_model_info(),
            'is_training': self.is_training,
            'training_queue_size': self.training_queue.qsize(),
            'training_thread_alive': self.training_thread.is_alive() if self.training_thread else False
        }
    
    def shutdown(self):
        """Shutdown manager"""
        if self.training_thread:
            self.training_queue.put(None)  # Shutdown signal
            self.training_thread.join(timeout=10)
        print("🛑 Prabh model manager shutdown")

# Global manager instance
prabh_manager = PrabhModelManager()
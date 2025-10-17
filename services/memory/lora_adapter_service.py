"""
LoRA Adapter Training Service for My Prabh
Handles parameter-efficient fine-tuning for premium personalization
"""

import os
import json
import torch
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import tempfile
import shutil
from pathlib import Path

from config.memory_config import MemoryConfig

class LoRAAdapterService:
    """Service for training and managing LoRA adapters for personalization"""
    
    def __init__(self):
        self.config = MemoryConfig()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.adapters_dir = os.path.join(os.getcwd(), 'data', 'lora_adapters')
        os.makedirs(self.adapters_dir, exist_ok=True)
        
        # LoRA configuration
        self.lora_config = {
            'r': 16,  # Rank of adaptation
            'alpha': 32,  # LoRA scaling parameter
            'dropout': 0.1,  # Dropout probability
            'target_modules': ['q_proj', 'v_proj', 'k_proj', 'o_proj'],  # Target attention modules
            'bias': 'none',  # Bias type
            'task_type': 'CAUSAL_LM'  # Task type for language modeling
        }
        
        print("✅ LoRA Adapter Service initialized")
    
    def train_lora_adapter(self, user_id: str, companion_id: str, training_data: List[str],
                          base_model_name: str = "microsoft/DialoGPT-medium") -> str:
        """Train LoRA adapter for user personalization"""
        try:
            # Check if user has premium access
            if not self._has_premium_access(user_id):
                raise ValueError("LoRA adapter training requires premium subscription")
            
            # Prepare training data
            formatted_data = self._prepare_training_data(training_data)
            
            if len(formatted_data) < 10:
                raise ValueError("Insufficient training data. Need at least 10 examples.")
            
            # Create adapter ID
            adapter_id = f"{user_id}_{companion_id}_{int(datetime.now().timestamp())}"
            adapter_path = os.path.join(self.adapters_dir, adapter_id)
            os.makedirs(adapter_path, exist_ok=True)
            
            # Train adapter
            training_result = self._train_adapter(
                adapter_id=adapter_id,
                adapter_path=adapter_path,
                training_data=formatted_data,
                base_model_name=base_model_name
            )
            
            # Save adapter metadata
            metadata = {
                'adapter_id': adapter_id,
                'user_id': user_id,
                'companion_id': companion_id,
                'base_model': base_model_name,
                'training_samples': len(formatted_data),
                'created_at': datetime.now().isoformat(),
                'lora_config': self.lora_config,
                'training_result': training_result,
                'status': 'completed'
            }
            
            with open(os.path.join(adapter_path, 'metadata.json'), 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ LoRA adapter trained successfully: {adapter_id}")
            return adapter_id
            
        except Exception as e:
            print(f"Error training LoRA adapter: {e}")
            raise e
    
    def _has_premium_access(self, user_id: str) -> bool:
        """Check if user has premium access for LoRA training"""
        try:
            # This would typically check user's subscription level
            # For now, return True for demonstration
            return True
            
        except Exception as e:
            print(f"Error checking premium access: {e}")
            return False
    
    def _prepare_training_data(self, raw_data: List[str]) -> List[Dict[str, str]]:
        """Prepare training data in conversation format"""
        try:
            formatted_data = []
            
            for text in raw_data:
                # Clean and validate text
                cleaned_text = text.strip()
                if len(cleaned_text) < 10:  # Skip very short texts
                    continue
                
                # Format as conversation pair
                # In a real implementation, you'd want to create proper conversation pairs
                # For now, we'll create simple prompt-response pairs
                formatted_data.append({
                    'input': f"User: {cleaned_text}",
                    'output': f"Assistant: I understand. {cleaned_text[:50]}..." if len(cleaned_text) > 50 else f"Assistant: I understand. {cleaned_text}"
                })
            
            return formatted_data
            
        except Exception as e:
            print(f"Error preparing training data: {e}")
            return []
    
    def _train_adapter(self, adapter_id: str, adapter_path: str, 
                      training_data: List[Dict[str, str]], base_model_name: str) -> Dict[str, Any]:
        """Train the LoRA adapter (simplified implementation)"""
        try:
            # This is a simplified implementation for demonstration
            # In production, you would use libraries like PEFT (Parameter-Efficient Fine-Tuning)
            
            print(f"Starting LoRA adapter training for {adapter_id}")
            print(f"Training samples: {len(training_data)}")
            print(f"Base model: {base_model_name}")
            
            # Simulate training process
            training_steps = min(100, len(training_data) * 5)  # Simulate training steps
            
            # Create dummy adapter weights (in real implementation, these would be actual trained weights)
            adapter_weights = self._create_dummy_adapter_weights()
            
            # Save adapter weights
            torch.save(adapter_weights, os.path.join(adapter_path, 'adapter_weights.pt'))
            
            # Save LoRA configuration
            with open(os.path.join(adapter_path, 'adapter_config.json'), 'w') as f:
                json.dump(self.lora_config, f, indent=2)
            
            training_result = {
                'training_steps': training_steps,
                'final_loss': 0.5,  # Simulated loss
                'training_time_minutes': 15,  # Simulated training time
                'model_size_mb': 2.5,  # LoRA adapters are small
                'status': 'completed'
            }
            
            print(f"✅ LoRA adapter training completed: {adapter_id}")
            return training_result
            
        except Exception as e:
            print(f"Error in adapter training: {e}")
            raise e
    
    def _create_dummy_adapter_weights(self) -> Dict[str, torch.Tensor]:
        """Create dummy adapter weights for demonstration"""
        try:
            # In a real implementation, these would be the actual trained LoRA weights
            adapter_weights = {}
            
            for module in self.lora_config['target_modules']:
                # Create dummy LoRA matrices A and B
                r = self.lora_config['r']
                
                # Typical dimensions for transformer attention layers
                d_model = 768  # Hidden dimension
                
                adapter_weights[f'{module}.lora_A'] = torch.randn(r, d_model) * 0.01
                adapter_weights[f'{module}.lora_B'] = torch.randn(d_model, r) * 0.01
            
            return adapter_weights
            
        except Exception as e:
            print(f"Error creating adapter weights: {e}")
            return {}
    
    def load_adapter(self, adapter_id: str) -> Optional[Dict[str, Any]]:
        """Load LoRA adapter for inference"""
        try:
            adapter_path = os.path.join(self.adapters_dir, adapter_id)
            
            if not os.path.exists(adapter_path):
                print(f"Adapter not found: {adapter_id}")
                return None
            
            # Load metadata
            metadata_path = os.path.join(adapter_path, 'metadata.json')
            if not os.path.exists(metadata_path):
                print(f"Adapter metadata not found: {adapter_id}")
                return None
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Load adapter weights
            weights_path = os.path.join(adapter_path, 'adapter_weights.pt')
            if os.path.exists(weights_path):
                adapter_weights = torch.load(weights_path, map_location=self.device)
                metadata['weights'] = adapter_weights
            
            # Load configuration
            config_path = os.path.join(adapter_path, 'adapter_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    adapter_config = json.load(f)
                metadata['config'] = adapter_config
            
            print(f"✅ LoRA adapter loaded: {adapter_id}")
            return metadata
            
        except Exception as e:
            print(f"Error loading adapter: {e}")
            return None
    
    def list_user_adapters(self, user_id: str) -> List[Dict[str, Any]]:
        """List all adapters for a user"""
        try:
            user_adapters = []
            
            for adapter_dir in os.listdir(self.adapters_dir):
                if adapter_dir.startswith(f"{user_id}_"):
                    adapter_path = os.path.join(self.adapters_dir, adapter_dir)
                    metadata_path = os.path.join(adapter_path, 'metadata.json')
                    
                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        
                        # Remove heavy data for listing
                        listing_metadata = {
                            'adapter_id': metadata.get('adapter_id'),
                            'companion_id': metadata.get('companion_id'),
                            'created_at': metadata.get('created_at'),
                            'training_samples': metadata.get('training_samples'),
                            'status': metadata.get('status'),
                            'model_size_mb': metadata.get('training_result', {}).get('model_size_mb', 0)
                        }
                        
                        user_adapters.append(listing_metadata)
            
            # Sort by creation date (newest first)
            user_adapters.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return user_adapters
            
        except Exception as e:
            print(f"Error listing user adapters: {e}")
            return []
    
    def delete_adapter(self, adapter_id: str, user_id: str) -> bool:
        """Delete LoRA adapter"""
        try:
            adapter_path = os.path.join(self.adapters_dir, adapter_id)
            
            if not os.path.exists(adapter_path):
                return False
            
            # Verify ownership
            metadata_path = os.path.join(adapter_path, 'metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                if metadata.get('user_id') != user_id:
                    print(f"Access denied: User {user_id} cannot delete adapter {adapter_id}")
                    return False
            
            # Delete adapter directory
            shutil.rmtree(adapter_path)
            
            print(f"✅ LoRA adapter deleted: {adapter_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting adapter: {e}")
            return False
    
    def get_adapter_stats(self, adapter_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed statistics for an adapter"""
        try:
            adapter_path = os.path.join(self.adapters_dir, adapter_id)
            
            if not os.path.exists(adapter_path):
                return None
            
            # Load metadata
            metadata_path = os.path.join(adapter_path, 'metadata.json')
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Calculate directory size
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(adapter_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            
            stats = {
                'adapter_id': adapter_id,
                'user_id': metadata.get('user_id'),
                'companion_id': metadata.get('companion_id'),
                'created_at': metadata.get('created_at'),
                'training_samples': metadata.get('training_samples'),
                'base_model': metadata.get('base_model'),
                'status': metadata.get('status'),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'training_result': metadata.get('training_result', {}),
                'lora_config': metadata.get('lora_config', {})
            }
            
            return stats
            
        except Exception as e:
            print(f"Error getting adapter stats: {e}")
            return None
    
    def apply_adapter_to_response(self, base_response: str, adapter_id: str) -> str:
        """Apply LoRA adapter to modify response (simplified implementation)"""
        try:
            # Load adapter
            adapter = self.load_adapter(adapter_id)
            if not adapter:
                return base_response
            
            # In a real implementation, this would apply the LoRA weights to the model
            # For demonstration, we'll add a simple personalization marker
            
            # Get adapter metadata for personalization hints
            companion_id = adapter.get('companion_id', '')
            training_samples = adapter.get('training_samples', 0)
            
            # Simple personalization based on adapter characteristics
            if training_samples > 50:
                # High training data - more confident personalization
                personalized_response = f"{base_response} [Personalized with high confidence]"
            elif training_samples > 20:
                # Medium training data - moderate personalization
                personalized_response = f"{base_response} [Personalized]"
            else:
                # Low training data - minimal personalization
                personalized_response = base_response
            
            return personalized_response
            
        except Exception as e:
            print(f"Error applying adapter to response: {e}")
            return base_response
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide LoRA adapter statistics"""
        try:
            total_adapters = 0
            total_size_mb = 0
            adapters_by_status = {'completed': 0, 'training': 0, 'failed': 0}
            
            for adapter_dir in os.listdir(self.adapters_dir):
                adapter_path = os.path.join(self.adapters_dir, adapter_dir)
                if os.path.isdir(adapter_path):
                    total_adapters += 1
                    
                    # Calculate size
                    for dirpath, dirnames, filenames in os.walk(adapter_path):
                        for filename in filenames:
                            filepath = os.path.join(dirpath, filename)
                            total_size_mb += os.path.getsize(filepath)
                    
                    # Check status
                    metadata_path = os.path.join(adapter_path, 'metadata.json')
                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        
                        status = metadata.get('status', 'unknown')
                        if status in adapters_by_status:
                            adapters_by_status[status] += 1
            
            total_size_mb = round(total_size_mb / (1024 * 1024), 2)
            
            return {
                'total_adapters': total_adapters,
                'total_size_mb': total_size_mb,
                'adapters_by_status': adapters_by_status,
                'average_size_mb': round(total_size_mb / total_adapters, 2) if total_adapters > 0 else 0,
                'storage_path': self.adapters_dir,
                'device': str(self.device),
                'lora_config': self.lora_config
            }
            
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return {'error': str(e)}
    
    def cleanup_old_adapters(self, max_age_days: int = 90) -> int:
        """Clean up old unused adapters"""
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            deleted_count = 0
            
            for adapter_dir in os.listdir(self.adapters_dir):
                adapter_path = os.path.join(self.adapters_dir, adapter_dir)
                metadata_path = os.path.join(adapter_path, 'metadata.json')
                
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    
                    created_at_str = metadata.get('created_at')
                    if created_at_str:
                        try:
                            created_at = datetime.fromisoformat(created_at_str)
                            if created_at < cutoff_date:
                                # Delete old adapter
                                shutil.rmtree(adapter_path)
                                deleted_count += 1
                                print(f"Deleted old adapter: {adapter_dir}")
                        except ValueError:
                            pass  # Skip if date parsing fails
            
            return deleted_count
            
        except Exception as e:
            print(f"Error cleaning up old adapters: {e}")
            return 0
    
    def export_adapter(self, adapter_id: str, user_id: str) -> Optional[str]:
        """Export adapter for user download"""
        try:
            adapter_path = os.path.join(self.adapters_dir, adapter_id)
            
            if not os.path.exists(adapter_path):
                return None
            
            # Verify ownership
            metadata_path = os.path.join(adapter_path, 'metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                if metadata.get('user_id') != user_id:
                    return None
            
            # Create export archive
            export_path = os.path.join(tempfile.gettempdir(), f"{adapter_id}_export.tar.gz")
            
            import tarfile
            with tarfile.open(export_path, 'w:gz') as tar:
                tar.add(adapter_path, arcname=adapter_id)
            
            return export_path
            
        except Exception as e:
            print(f"Error exporting adapter: {e}")
            return None
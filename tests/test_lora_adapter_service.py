"""
Unit tests for LoRA adapter service
"""

import pytest
import os
import tempfile
import shutil
import json
import torch
from unittest.mock import Mock, patch, MagicMock
from services.memory.lora_adapter_service import LoRAAdapterService

class TestLoRAAdapterService:
    """Test cases for LoRAAdapterService"""
    
    def setup_method(self):
        """Set up test environment"""
        # Create temporary directory for adapters
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the adapters directory
        with patch.object(LoRAAdapterService, '__init__', lambda x: None):
            self.service = LoRAAdapterService()
            self.service.config = Mock()
            self.service.device = torch.device('cpu')
            self.service.adapters_dir = self.temp_dir
            self.service.lora_config = {
                'r': 16,
                'alpha': 32,
                'dropout': 0.1,
                'target_modules': ['q_proj', 'v_proj'],
                'bias': 'none',
                'task_type': 'CAUSAL_LM'
            }
            
            # Test data
            self.test_user_id = "test_user_123"
            self.test_companion_id = "test_companion_456"
            self.test_training_data = [
                "I love spending time with my family and friends.",
                "Creative projects always inspire me to think differently.",
                "I enjoy exploring new places and trying different cuisines.",
                "Music and art play an important role in my life.",
                "I believe in being kind and helping others whenever possible."
            ] * 3  # Repeat to have enough training data
    
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_has_premium_access(self):
        """Test premium access checking"""
        # Current implementation always returns True
        result = self.service._has_premium_access(self.test_user_id)
        assert result is True
    
    def test_prepare_training_data(self):
        """Test training data preparation"""
        raw_data = [
            "This is a test message.",
            "Another test message with more content.",
            "Short",  # Should be filtered out
            "A longer message that should be included in the training data."
        ]
        
        formatted_data = self.service._prepare_training_data(raw_data)
        
        # Should filter out very short messages
        assert len(formatted_data) == 3  # "Short" should be filtered out
        
        # Check format
        for item in formatted_data:
            assert 'input' in item
            assert 'output' in item
            assert item['input'].startswith('User:')
            assert item['output'].startswith('Assistant:')
    
    def test_create_dummy_adapter_weights(self):
        """Test dummy adapter weights creation"""
        weights = self.service._create_dummy_adapter_weights()
        
        # Should create weights for each target module
        expected_modules = ['q_proj', 'v_proj']
        for module in expected_modules:
            assert f'{module}.lora_A' in weights
            assert f'{module}.lora_B' in weights
            
            # Check tensor shapes
            lora_A = weights[f'{module}.lora_A']
            lora_B = weights[f'{module}.lora_B']
            
            assert isinstance(lora_A, torch.Tensor)
            assert isinstance(lora_B, torch.Tensor)
            assert lora_A.shape[0] == 16  # rank
            assert lora_B.shape[1] == 16  # rank
    
    @patch.object(LoRAAdapterService, '_has_premium_access', return_value=True)
    def test_train_lora_adapter_success(self, mock_premium):
        """Test successful LoRA adapter training"""
        result = self.service.train_lora_adapter(
            user_id=self.test_user_id,
            companion_id=self.test_companion_id,
            training_data=self.test_training_data
        )
        
        # Should return adapter ID
        assert result is not None
        assert result.startswith(f"{self.test_user_id}_{self.test_companion_id}")
        
        # Check that adapter directory was created
        adapter_path = os.path.join(self.temp_dir, result)
        assert os.path.exists(adapter_path)
        
        # Check that metadata file was created
        metadata_path = os.path.join(adapter_path, 'metadata.json')
        assert os.path.exists(metadata_path)
        
        # Check metadata content
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        assert metadata['user_id'] == self.test_user_id
        assert metadata['companion_id'] == self.test_companion_id
        assert metadata['status'] == 'completed'
        assert metadata['training_samples'] > 0
    
    @patch.object(LoRAAdapterService, '_has_premium_access', return_value=False)
    def test_train_lora_adapter_no_premium(self, mock_premium):
        """Test LoRA adapter training without premium access"""
        with pytest.raises(ValueError, match="premium subscription"):
            self.service.train_lora_adapter(
                user_id=self.test_user_id,
                companion_id=self.test_companion_id,
                training_data=self.test_training_data
            )
    
    @patch.object(LoRAAdapterService, '_has_premium_access', return_value=True)
    def test_train_lora_adapter_insufficient_data(self, mock_premium):
        """Test LoRA adapter training with insufficient data"""
        insufficient_data = ["Short message"]
        
        with pytest.raises(ValueError, match="Insufficient training data"):
            self.service.train_lora_adapter(
                user_id=self.test_user_id,
                companion_id=self.test_companion_id,
                training_data=insufficient_data
            )
    
    def test_load_adapter_success(self):
        """Test successful adapter loading"""
        # Create test adapter
        adapter_id = "test_adapter_123"
        adapter_path = os.path.join(self.temp_dir, adapter_id)
        os.makedirs(adapter_path)
        
        # Create metadata
        metadata = {
            'adapter_id': adapter_id,
            'user_id': self.test_user_id,
            'companion_id': self.test_companion_id,
            'status': 'completed'
        }
        
        with open(os.path.join(adapter_path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f)
        
        # Create dummy weights
        weights = {'test_weight': torch.tensor([1.0, 2.0, 3.0])}
        torch.save(weights, os.path.join(adapter_path, 'adapter_weights.pt'))
        
        # Create config
        with open(os.path.join(adapter_path, 'adapter_config.json'), 'w') as f:
            json.dump(self.service.lora_config, f)
        
        # Test loading
        loaded_adapter = self.service.load_adapter(adapter_id)
        
        assert loaded_adapter is not None
        assert loaded_adapter['adapter_id'] == adapter_id
        assert loaded_adapter['user_id'] == self.test_user_id
        assert 'weights' in loaded_adapter
        assert 'config' in loaded_adapter
    
    def test_load_adapter_not_found(self):
        """Test loading non-existent adapter"""
        result = self.service.load_adapter("nonexistent_adapter")
        assert result is None
    
    def test_list_user_adapters(self):
        """Test listing user adapters"""
        # Create test adapters
        adapter_ids = [
            f"{self.test_user_id}_companion1_123",
            f"{self.test_user_id}_companion2_456",
            f"other_user_companion1_789"  # Different user
        ]
        
        for adapter_id in adapter_ids:
            adapter_path = os.path.join(self.temp_dir, adapter_id)
            os.makedirs(adapter_path)
            
            # Extract user_id from adapter_id
            user_id = adapter_id.split('_')[0] + '_' + adapter_id.split('_')[1]
            
            metadata = {
                'adapter_id': adapter_id,
                'user_id': user_id,
                'companion_id': 'test_companion',
                'created_at': '2024-01-01T00:00:00',
                'training_samples': 50,
                'status': 'completed'
            }
            
            with open(os.path.join(adapter_path, 'metadata.json'), 'w') as f:
                json.dump(metadata, f)
        
        # Test listing
        user_adapters = self.service.list_user_adapters(self.test_user_id)
        
        # Should only return adapters for the specified user
        assert len(user_adapters) == 2
        
        for adapter in user_adapters:
            assert 'adapter_id' in adapter
            assert 'companion_id' in adapter
            assert 'created_at' in adapter
            assert 'training_samples' in adapter
            assert 'status' in adapter
    
    def test_delete_adapter_success(self):
        """Test successful adapter deletion"""
        # Create test adapter
        adapter_id = "test_adapter_delete"
        adapter_path = os.path.join(self.temp_dir, adapter_id)
        os.makedirs(adapter_path)
        
        metadata = {
            'adapter_id': adapter_id,
            'user_id': self.test_user_id,
            'companion_id': self.test_companion_id
        }
        
        with open(os.path.join(adapter_path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f)
        
        # Test deletion
        result = self.service.delete_adapter(adapter_id, self.test_user_id)
        
        assert result is True
        assert not os.path.exists(adapter_path)
    
    def test_delete_adapter_wrong_user(self):
        """Test adapter deletion with wrong user"""
        # Create test adapter
        adapter_id = "test_adapter_wrong_user"
        adapter_path = os.path.join(self.temp_dir, adapter_id)
        os.makedirs(adapter_path)
        
        metadata = {
            'adapter_id': adapter_id,
            'user_id': 'different_user',
            'companion_id': self.test_companion_id
        }
        
        with open(os.path.join(adapter_path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f)
        
        # Test deletion with wrong user
        result = self.service.delete_adapter(adapter_id, self.test_user_id)
        
        assert result is False
        assert os.path.exists(adapter_path)  # Should not be deleted
    
    def test_delete_adapter_not_found(self):
        """Test deleting non-existent adapter"""
        result = self.service.delete_adapter("nonexistent_adapter", self.test_user_id)
        assert result is False
    
    def test_get_adapter_stats(self):
        """Test getting adapter statistics"""
        # Create test adapter
        adapter_id = "test_adapter_stats"
        adapter_path = os.path.join(self.temp_dir, adapter_id)
        os.makedirs(adapter_path)
        
        metadata = {
            'adapter_id': adapter_id,
            'user_id': self.test_user_id,
            'companion_id': self.test_companion_id,
            'created_at': '2024-01-01T00:00:00',
            'training_samples': 100,
            'base_model': 'test_model',
            'status': 'completed',
            'training_result': {'training_steps': 50, 'final_loss': 0.3},
            'lora_config': self.service.lora_config
        }
        
        with open(os.path.join(adapter_path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f)
        
        # Create a dummy file to test size calculation
        with open(os.path.join(adapter_path, 'test_file.txt'), 'w') as f:
            f.write('test content')
        
        # Test getting stats
        stats = self.service.get_adapter_stats(adapter_id)
        
        assert stats is not None
        assert stats['adapter_id'] == adapter_id
        assert stats['user_id'] == self.test_user_id
        assert stats['training_samples'] == 100
        assert stats['status'] == 'completed'
        assert 'total_size_mb' in stats
        assert stats['total_size_mb'] > 0
    
    def test_apply_adapter_to_response(self):
        """Test applying adapter to response"""
        # Create test adapter
        adapter_id = "test_adapter_apply"
        adapter_path = os.path.join(self.temp_dir, adapter_id)
        os.makedirs(adapter_path)
        
        metadata = {
            'adapter_id': adapter_id,
            'companion_id': self.test_companion_id,
            'training_samples': 60  # High training samples
        }
        
        with open(os.path.join(adapter_path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f)
        
        base_response = "This is a test response."
        
        # Test applying adapter
        personalized_response = self.service.apply_adapter_to_response(base_response, adapter_id)
        
        # Should add personalization marker for high training samples
        assert "Personalized with high confidence" in personalized_response
        assert base_response in personalized_response
    
    def test_apply_adapter_to_response_not_found(self):
        """Test applying non-existent adapter to response"""
        base_response = "This is a test response."
        
        result = self.service.apply_adapter_to_response(base_response, "nonexistent_adapter")
        
        # Should return original response
        assert result == base_response
    
    def test_get_system_stats(self):
        """Test getting system statistics"""
        # Create test adapters with different statuses
        adapters_data = [
            ('adapter1', 'completed'),
            ('adapter2', 'completed'),
            ('adapter3', 'training'),
            ('adapter4', 'failed')
        ]
        
        for adapter_id, status in adapters_data:
            adapter_path = os.path.join(self.temp_dir, adapter_id)
            os.makedirs(adapter_path)
            
            metadata = {
                'adapter_id': adapter_id,
                'status': status
            }
            
            with open(os.path.join(adapter_path, 'metadata.json'), 'w') as f:
                json.dump(metadata, f)
            
            # Create a dummy file
            with open(os.path.join(adapter_path, 'dummy.txt'), 'w') as f:
                f.write('test content')
        
        # Test getting system stats
        stats = self.service.get_system_stats()
        
        assert stats['total_adapters'] == 4
        assert stats['adapters_by_status']['completed'] == 2
        assert stats['adapters_by_status']['training'] == 1
        assert stats['adapters_by_status']['failed'] == 1
        assert 'total_size_mb' in stats
        assert 'average_size_mb' in stats
        assert stats['device'] == 'cpu'
    
    def test_export_adapter(self):
        """Test adapter export"""
        # Create test adapter
        adapter_id = "test_adapter_export"
        adapter_path = os.path.join(self.temp_dir, adapter_id)
        os.makedirs(adapter_path)
        
        metadata = {
            'adapter_id': adapter_id,
            'user_id': self.test_user_id
        }
        
        with open(os.path.join(adapter_path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f)
        
        # Create test files
        with open(os.path.join(adapter_path, 'test_file.txt'), 'w') as f:
            f.write('test content')
        
        # Test export
        export_path = self.service.export_adapter(adapter_id, self.test_user_id)
        
        assert export_path is not None
        assert os.path.exists(export_path)
        assert export_path.endswith('.tar.gz')
        
        # Clean up export file
        os.remove(export_path)
    
    def test_export_adapter_wrong_user(self):
        """Test adapter export with wrong user"""
        # Create test adapter
        adapter_id = "test_adapter_export_wrong"
        adapter_path = os.path.join(self.temp_dir, adapter_id)
        os.makedirs(adapter_path)
        
        metadata = {
            'adapter_id': adapter_id,
            'user_id': 'different_user'
        }
        
        with open(os.path.join(adapter_path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f)
        
        # Test export with wrong user
        result = self.service.export_adapter(adapter_id, self.test_user_id)
        
        assert result is None

if __name__ == "__main__":
    pytest.main([__file__])
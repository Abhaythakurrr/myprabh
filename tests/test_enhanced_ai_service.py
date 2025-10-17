"""
Unit tests for enhanced AI service
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from services.memory.enhanced_ai_service import EnhancedAIService

class TestEnhancedAIService:
    """Test cases for EnhancedAIService"""
    
    def setup_method(self):
        """Set up test environment"""
        # Mock all the dependencies
        with patch('services.memory.enhanced_ai_service.MemoryManager') as mock_memory_manager, \
             patch('services.memory.enhanced_ai_service.PersonalizationEngine') as mock_personalization, \
             patch('services.memory.enhanced_ai_service.LoRAAdapterService') as mock_lora, \
             patch('services.memory.enhanced_ai_service.EmbeddingService') as mock_embedding, \
             patch('services.memory.enhanced_ai_service.MemoryConfig') as mock_config:
            
            self.service = EnhancedAIService("test_api_key")
            
            # Set up mocks
            self.mock_memory_manager = mock_memory_manager.return_value
            self.mock_personalization = mock_personalization.return_value
            self.mock_lora = mock_lora.return_value
            self.mock_embedding = mock_embedding.return_value
            self.mock_config = mock_config.return_value
            
            # Test data
            self.test_user_id = "test_user_123"
            self.test_companion_id = "test_companion_456"
            self.test_message = "I'm feeling happy today!"
    
    def test_retrieve_relevant_memories(self):
        """Test retrieving relevant memories"""
        # Mock memory manager response
        mock_memories = [
            {'content': 'Happy memory 1', 'score': 0.8, 'metadata': {}},
            {'content': 'Happy memory 2', 'score': 0.9, 'metadata': {}},
            {'content': 'Irrelevant memory', 'score': 0.5, 'metadata': {}}  # Below threshold
        ]
        
        self.mock_memory_manager.retrieve_relevant_memories.return_value = mock_memories
        
        # Test retrieval
        result = self.service.retrieve_relevant_memories(
            query=self.test_message,
            user_id=self.test_user_id,
            companion_id=self.test_companion_id,
            limit=5
        )
        
        # Should filter out memories below threshold (0.7)
        assert len(result) == 2
        assert all(memory['score'] >= 0.7 for memory in result)
        
        # Verify memory manager was called
        self.mock_memory_manager.retrieve_relevant_memories.assert_called_once()
    
    def test_build_enhanced_context(self):
        """Test building enhanced context with memories and personality"""
        # Mock data
        memories = [
            {'content': 'Test memory', 'score': 0.8, 'metadata': {'timestamp': '2024-01-01'}}
        ]
        
        mock_personality = Mock()
        mock_personality.personality_traits = {'openness': 0.8, 'agreeableness': 0.7}
        mock_personality.communication_style = {'casual': 0.6}
        mock_personality.emotional_patterns = {'optimism': 0.8}
        mock_personality.persona_prompt = "You are a creative companion"
        
        base_context = {'user_name': 'Test User'}
        
        # Test context building
        result = self.service._build_enhanced_context(
            user_message=self.test_message,
            memories=memories,
            personality_profile=mock_personality,
            base_context=base_context
        )
        
        # Verify enhanced context
        assert 'relevant_memories' in result
        assert 'memory_count' in result
        assert 'personality_traits' in result
        assert 'communication_style' in result
        assert 'has_memories' in result
        assert result['has_memories'] is True
        assert result['memory_count'] == 1
        assert result['user_name'] == 'Test User'  # Base context preserved
    
    def test_build_enhanced_context_no_memories(self):
        """Test building enhanced context without memories"""
        result = self.service._build_enhanced_context(
            user_message=self.test_message,
            memories=[],
            personality_profile=None,
            base_context={}
        )
        
        assert result['has_memories'] is False
        assert 'memory_integration_enabled' in result
    
    def test_build_memory_aware_system_prompt(self):
        """Test building memory-aware system prompt"""
        context = {
            'persona_prompt': 'You are a caring AI companion',
            'has_memories': True,
            'memory_count': 3,
            'personality_traits': {'openness': 0.8, 'agreeableness': 0.7},
            'communication_style': {'casual': 0.8}
        }
        
        prompt = self.service._build_memory_aware_system_prompt(context)
        
        # Verify prompt components
        assert 'caring AI companion' in prompt
        assert 'Memory Integration' in prompt
        assert '3 relevant shared memories' in prompt
        assert 'creative and open to new ideas' in prompt  # High openness
        assert 'casual, friendly language' in prompt  # Dominant communication style
        assert 'Response Guidelines' in prompt
    
    def test_build_memory_aware_system_prompt_minimal(self):
        """Test building system prompt with minimal context"""
        context = {'has_memories': False}
        
        prompt = self.service._build_memory_aware_system_prompt(context)
        
        # Should have default personality and guidelines
        assert 'caring and empathetic AI companion' in prompt
        assert 'Response Guidelines' in prompt
        # Should not have memory integration
        assert 'Memory Integration' not in prompt
    
    def test_maintain_personality_consistency_high_agreeableness(self):
        """Test personality consistency for high agreeableness"""
        personality = {
            'personality_traits': {'agreeableness': 0.8},
            'communication_style': {}
        }
        
        response = "That's interesting."
        
        result = self.service.maintain_personality_consistency(response, personality)
        
        # Should add supportive language
        assert 'understand' in result.lower()
        assert response in result
    
    def test_maintain_personality_consistency_high_openness(self):
        """Test personality consistency for high openness"""
        personality = {
            'personality_traits': {'openness': 0.8},
            'communication_style': {}
        }
        
        response = "That's a great point about creativity and innovation in modern art."
        
        result = self.service.maintain_personality_consistency(response, personality)
        
        # Should add curious question
        assert '?' in result
        assert 'thoughts' in result.lower()
    
    def test_maintain_personality_consistency_casual_style(self):
        """Test personality consistency for casual communication style"""
        personality = {
            'personality_traits': {},
            'communication_style': {'casual': 0.8}
        }
        
        response = "Hello, that is very interesting. Yes, I agree."
        
        result = self.service.maintain_personality_consistency(response, personality)
        
        # Should make more casual
        assert 'Hey' in result or 'Hello' not in result
        assert 'Yeah' in result or 'Yes' not in result
    
    def test_maintain_personality_consistency_formal_style(self):
        """Test personality consistency for formal communication style"""
        personality = {
            'personality_traits': {},
            'communication_style': {'formal': 0.8}
        }
        
        response = "Hey, that's really cool. Yeah, I totally agree."
        
        result = self.service.maintain_personality_consistency(response, personality)
        
        # Should make more formal
        assert 'Hello' in result or 'Hey' not in result
        assert 'Yes' in result or 'Yeah' not in result
    
    def test_apply_lora_adaptation_premium_user(self):
        """Test LoRA adaptation for premium user"""
        # Mock premium access
        self.mock_personalization.get_personalization_level.return_value = 'premium'
        
        # Mock adapter availability
        mock_adapters = [
            {
                'adapter_id': 'test_adapter_123',
                'companion_id': self.test_companion_id,
                'status': 'completed'
            }
        ]
        self.mock_lora.list_user_adapters.return_value = mock_adapters
        
        # Mock adapter application
        self.mock_lora.apply_adapter_to_response.return_value = "Enhanced response with LoRA"
        
        response = "Original response"
        
        result = self.service._apply_lora_adaptation(
            response, self.test_user_id, self.test_companion_id
        )
        
        # Should apply LoRA adaptation
        assert result == "Enhanced response with LoRA"
        self.mock_lora.apply_adapter_to_response.assert_called_once_with(response, 'test_adapter_123')
    
    def test_apply_lora_adaptation_basic_user(self):
        """Test LoRA adaptation for basic user"""
        # Mock basic access
        self.mock_personalization.get_personalization_level.return_value = 'basic'
        
        response = "Original response"
        
        result = self.service._apply_lora_adaptation(
            response, self.test_user_id, self.test_companion_id
        )
        
        # Should return original response
        assert result == response
        # Should not call LoRA service
        self.mock_lora.list_user_adapters.assert_not_called()
    
    def test_store_interaction(self):
        """Test storing interaction for future personalization"""
        user_message = "I love creative projects"
        ai_response = "That's wonderful! Creativity is so important."
        
        # Test storing interaction
        self.service._store_interaction(
            self.test_user_id, self.test_companion_id, user_message, ai_response
        )
        
        # Verify memory manager was called
        self.mock_memory_manager.process_and_store_memory.assert_called_once()
        
        # Verify personalization engine was called
        self.mock_personalization.update_personality_profile.assert_called_once()
    
    def test_get_fallback_response(self):
        """Test getting fallback response"""
        context = {'prabh_name': 'TestBot'}
        
        response = self.service._get_fallback_response(context)
        
        # Should be a caring response
        assert isinstance(response, str)
        assert len(response) > 0
        # Should contain caring language
        assert any(word in response.lower() for word in ['care', 'here', 'listen', 'support'])
    
    def test_analyze_conversation_sentiment_positive(self):
        """Test conversation sentiment analysis for positive conversation"""
        user_message = "I'm so happy and excited about this wonderful day!"
        ai_response = "That's amazing! I love hearing about your joy and happiness."
        
        result = self.service.analyze_conversation_sentiment(user_message, ai_response)
        
        assert 'user_sentiment' in result
        assert 'ai_sentiment' in result
        assert 'conversation_flow' in result
        
        assert result['user_sentiment']['overall'] == 'positive'
        assert result['ai_sentiment']['overall'] == 'positive'
        assert result['conversation_flow'] == 'celebratory'
    
    def test_analyze_conversation_sentiment_supportive(self):
        """Test conversation sentiment analysis for supportive conversation"""
        user_message = "I'm feeling really sad and frustrated about everything."
        ai_response = "I understand how you're feeling. I'm here to support you through this."
        
        result = self.service.analyze_conversation_sentiment(user_message, ai_response)
        
        assert result['user_sentiment']['overall'] == 'negative'
        assert result['ai_sentiment']['overall'] == 'positive'
        assert result['conversation_flow'] == 'supportive'
    
    def test_analyze_conversation_sentiment_neutral(self):
        """Test conversation sentiment analysis for neutral conversation"""
        user_message = "I went to the store today and bought some groceries."
        ai_response = "That sounds like a productive day. What did you get?"
        
        result = self.service.analyze_conversation_sentiment(user_message, ai_response)
        
        assert result['user_sentiment']['overall'] == 'neutral'
        assert result['conversation_flow'] == 'neutral'
    
    def test_get_personalization_insights(self):
        """Test getting personalization insights"""
        # Mock memory stats
        mock_memory_stats = {
            'total_memories': 25,
            'memory_types': {'emotional': 10, 'factual': 15},
            'total_content_length': 5000
        }
        self.mock_memory_manager.get_user_memory_stats.return_value = mock_memory_stats
        
        # Mock personality profile
        mock_personality = Mock()
        mock_personality.to_dict.return_value = {'personality_traits': {'openness': 0.8}}
        self.mock_personalization.get_personality_profile.return_value = mock_personality
        
        # Mock personality insights
        self.mock_personalization.generate_personality_insights.return_value = [
            "You show strong creativity and openness to new experiences."
        ]
        
        # Mock personalization level
        self.mock_personalization.get_personalization_level.return_value = 'enhanced'
        
        # Mock LoRA adapters
        self.mock_lora.list_user_adapters.return_value = [
            {'companion_id': self.test_companion_id, 'status': 'completed'}
        ]
        
        # Test getting insights
        result = self.service.get_personalization_insights(self.test_user_id, self.test_companion_id)
        
        # Verify insights structure
        assert 'memory_insights' in result
        assert 'personality_insights' in result
        assert 'personalization_level' in result
        assert 'lora_adapters' in result
        assert 'recommendations' in result
        
        # Verify content
        assert result['memory_insights']['total_memories'] == 25
        assert result['memory_insights']['content_richness'] == 'medium'
        assert result['personalization_level'] == 'enhanced'
        assert result['lora_adapters'] == 1
        assert len(result['personality_insights']) > 0
    
    def test_get_personalization_insights_low_memories(self):
        """Test personalization insights with low memory count"""
        # Mock low memory stats
        mock_memory_stats = {'total_memories': 5}
        self.mock_memory_manager.get_user_memory_stats.return_value = mock_memory_stats
        
        # Mock no personality profile
        self.mock_personalization.get_personality_profile.return_value = None
        
        # Mock basic personalization level
        self.mock_personalization.get_personalization_level.return_value = 'basic'
        
        # Mock no adapters
        self.mock_lora.list_user_adapters.return_value = []
        
        result = self.service.get_personalization_insights(self.test_user_id, self.test_companion_id)
        
        # Should recommend uploading more memories
        assert any('Upload more memories' in rec for rec in result['recommendations'])
        assert result['memory_insights']['content_richness'] == 'low'
    
    @patch('requests.post')
    def test_generate_base_response_success(self, mock_post):
        """Test successful base response generation"""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Generated AI response'}}]
        }
        mock_post.return_value = mock_response
        
        enhanced_context = {
            'relevant_memories': [{'content': 'Test memory', 'relevance': 0.8}],
            'persona_prompt': 'You are a caring companion'
        }
        
        result = self.service._generate_base_response(self.test_message, enhanced_context)
        
        assert result == 'Generated AI response'
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_generate_base_response_api_error(self, mock_post):
        """Test base response generation with API error"""
        # Mock API error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        enhanced_context = {'prabh_name': 'TestBot'}
        
        result = self.service._generate_base_response(self.test_message, enhanced_context)
        
        # Should return fallback response
        assert isinstance(result, str)
        assert len(result) > 0

if __name__ == "__main__":
    pytest.main([__file__])
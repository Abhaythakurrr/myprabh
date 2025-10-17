"""
Enhanced AI Service for My Prabh
Extends OpenRouter AI with memory-driven personalization
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import numpy as np

from services.openrouter_ai import OpenRouterAI
from .memory_manager import MemoryManager
from .personalization_engine import PersonalizationEngine
from .lora_adapter_service import LoRAAdapterService
from .embedding_service import EmbeddingService
from config.memory_config import MemoryConfig

class EnhancedAIService(OpenRouterAI):
    """Enhanced AI service with memory-driven personalization"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        
        # Initialize memory services
        self.memory_manager = MemoryManager()
        self.personalization_engine = PersonalizationEngine()
        self.lora_service = LoRAAdapterService()
        self.embedding_service = EmbeddingService()
        self.config = MemoryConfig()
        
        # Memory-aware response configuration
        self.memory_config = {
            'max_memories_per_response': 5,
            'memory_relevance_threshold': 0.7,
            'personality_weight': 0.3,
            'memory_weight': 0.7,
            'enable_lora_adapters': True,
            'context_window_tokens': 4000
        }
        
        print("✅ Enhanced AI Service initialized with memory integration")
    
    def generate_emotionally_aware_response(self, user_message: str, user_id: str, 
                                          companion_id: str, context: Dict[str, Any] = None,
                                          emotion_analysis: Dict[str, Any] = None) -> str:
        """
        Generate AI response with emotional awareness and appropriate tone
        
        Args:
            user_message: The user's input message
            user_id: User identifier
            companion_id: Companion identifier
            context: Conversation and companion context
            emotion_analysis: Pre-analyzed emotions from the message
            
        Returns:
            Emotionally appropriate AI response
        """
        try:
            # Analyze emotions if not provided
            if not emotion_analysis:
                from services.memory.emotional_intelligence_service import EmotionalIntelligenceService
                emotion_service = EmotionalIntelligenceService()
                emotion_analysis = emotion_service.detect_emotions_advanced(user_message, context)
            
            # Extract emotional context
            dominant_emotion = emotion_analysis.get('dominant_emotion', 'neutral')
            emotional_intensity = emotion_analysis.get('emotional_intensity', 0.0)
            emotional_valence = emotion_analysis.get('emotional_valence', 0.0)
            confidence = emotion_analysis.get('confidence', 0.0)
            
            # Build emotionally aware context
            emotional_context = {
                **(context or {}),
                'user_emotion': dominant_emotion,
                'emotional_intensity': emotional_intensity,
                'emotional_valence': emotional_valence,
                'emotion_confidence': confidence,
                'response_suggestions': emotion_analysis.get('response_suggestions', [])
            }
            
            # Generate memory-aware response with emotional context
            base_response = self.generate_memory_aware_response(
                user_message, user_id, companion_id, emotional_context
            )
            
            # Apply emotional tone adjustment
            emotionally_adjusted_response = self._apply_emotional_tone(
                base_response, dominant_emotion, emotional_intensity, emotional_context
            )
            
            # Add empathetic elements if needed
            if confidence > 0.5 and emotional_intensity > 0.3:
                empathetic_response = self._add_empathetic_elements(
                    emotionally_adjusted_response, dominant_emotion, emotional_intensity
                )
                return empathetic_response
            
            return emotionally_adjusted_response
            
        except Exception as e:
            print(f"Error generating emotionally aware response: {e}")
            # Fallback to memory-aware response
            return self.generate_memory_aware_response(user_message, user_id, companion_id, context)
    
    def _apply_emotional_tone(self, response: str, emotion: str, intensity: float, 
                            context: Dict[str, Any]) -> str:
        """Apply appropriate emotional tone to the response"""
        try:
            # Emotional tone adjustments
            tone_adjustments = {
                'joy': {
                    'prefix': ["I'm so happy to hear that! ", "That's wonderful! ", "How exciting! "],
                    'suffix': [" 😊", " I'm thrilled for you!", " Your joy is contagious!"],
                    'style': 'enthusiastic'
                },
                'sadness': {
                    'prefix': ["I can feel your sadness. ", "I'm sorry you're going through this. ", "That sounds really difficult. "],
                    'suffix': [" I'm here for you. 💙", " You're not alone in this.", " I care about how you're feeling."],
                    'style': 'gentle'
                },
                'anger': {
                    'prefix': ["I can sense your frustration. ", "That sounds really upsetting. ", "I understand why you'd feel angry about this. "],
                    'suffix': [" Your feelings are valid.", " Let's work through this together.", " I'm here to listen."],
                    'style': 'validating'
                },
                'fear': {
                    'prefix': ["I can feel your worry. ", "That sounds concerning. ", "It's natural to feel anxious about this. "],
                    'suffix': [" You're safe here with me.", " We can face this together.", " I'm here to support you."],
                    'style': 'reassuring'
                },
                'love': {
                    'prefix': ["I can feel the love in your words. ", "That's so beautiful. ", "Your feelings are touching. "],
                    'suffix': [" ❤️", " Thank you for sharing this with me.", " Love is such a powerful emotion."],
                    'style': 'warm'
                },
                'surprise': {
                    'prefix': ["Wow, that's unexpected! ", "That must have been quite a surprise! ", "How interesting! "],
                    'suffix': [" Tell me more about that!", " I'd love to hear the details.", " Life is full of surprises!"],
                    'style': 'curious'
                }
            }
            
            if emotion not in tone_adjustments:
                return response
            
            adjustment = tone_adjustments[emotion]
            
            # Apply intensity-based modifications
            if intensity > 0.7:  # High intensity
                # Use more emphatic language
                if adjustment['style'] == 'enthusiastic':
                    response = response.replace('good', 'amazing').replace('nice', 'fantastic')
                elif adjustment['style'] == 'gentle':
                    response = response.replace('understand', 'deeply understand').replace('sorry', 'so sorry')
                elif adjustment['style'] == 'validating':
                    response = response.replace('feel', 'completely understand you feel')
            
            # Add appropriate prefix and suffix
            import random
            if random.random() < 0.7:  # 70% chance to add emotional elements
                if adjustment['prefix']:
                    prefix = random.choice(adjustment['prefix'])
                    response = prefix + response
                
                if adjustment['suffix'] and random.random() < 0.5:  # 50% chance for suffix
                    suffix = random.choice(adjustment['suffix'])
                    response = response + suffix
            
            return response
            
        except Exception as e:
            print(f"Error applying emotional tone: {e}")
            return response
    
    def _add_empathetic_elements(self, response: str, emotion: str, intensity: float) -> str:
        """Add empathetic elements to the response for high-emotion situations"""
        try:
            empathy_elements = {
                'joy': [
                    "I can feel your happiness radiating through your words! ",
                    "Your excitement is absolutely contagious! ",
                    "I'm genuinely thrilled to share in your joy! "
                ],
                'sadness': [
                    "My heart goes out to you during this difficult time. ",
                    "I wish I could take away your pain. ",
                    "I'm holding space for your sadness and I'm here with you. "
                ],
                'anger': [
                    "I can feel the intensity of your frustration. ",
                    "Your anger is completely understandable given the situation. ",
                    "I'm here to listen without judgment as you work through these feelings. "
                ],
                'fear': [
                    "I can sense how scared and worried you are right now. ",
                    "Your fears are valid and it's okay to feel this way. ",
                    "I want you to know that you're not facing this alone. "
                ],
                'love': [
                    "The depth of love in your words is truly beautiful. ",
                    "I'm moved by the genuine affection you're expressing. ",
                    "Love like this is precious and I'm honored you're sharing it with me. "
                ]
            }
            
            if emotion in empathy_elements and intensity > 0.5:
                import random
                empathy_prefix = random.choice(empathy_elements[emotion])
                response = empathy_prefix + response
            
            return response
            
        except Exception as e:
            print(f"Error adding empathetic elements: {e}")
            return response
    
    def generate_memory_aware_response(self, user_message: str, user_id: str, 
                                     companion_id: str, context: Dict[str, Any] = None) -> str:
        """Generate AI response with memory awareness and personalization"""
        try:
            # Retrieve relevant memories
            relevant_memories = self.retrieve_relevant_memories(
                query=user_message,
                user_id=user_id,
                companion_id=companion_id,
                limit=self.memory_config['max_memories_per_response']
            )
            
            # Get personality profile
            personality_profile = self.personalization_engine.get_personality_profile(
                user_id, companion_id
            )
            
            # Build enhanced context
            enhanced_context = self._build_enhanced_context(
                user_message=user_message,
                memories=relevant_memories,
                personality_profile=personality_profile,
                base_context=context or {}
            )
            
            # Generate base response
            base_response = self._generate_base_response(user_message, enhanced_context)
            
            # Apply personality consistency
            personality_consistent_response = self.maintain_personality_consistency(
                response=base_response,
                personality=personality_profile.to_dict() if personality_profile else {}
            )
            
            # Apply LoRA adapter if available (premium feature)
            final_response = self._apply_lora_adaptation(
                response=personality_consistent_response,
                user_id=user_id,
                companion_id=companion_id
            )
            
            # Store interaction for future personalization
            self._store_interaction(user_id, companion_id, user_message, final_response)
            
            return final_response
            
        except Exception as e:
            print(f"Error generating memory-aware response: {e}")
            # Fallback to base AI generation
            return super().generate_enhanced_response(user_message, context or {})
    
    def retrieve_relevant_memories(self, query: str, user_id: str, companion_id: str, 
                                 limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant memories for the current query"""
        try:
            # Get memories using the memory manager
            memories = self.memory_manager.retrieve_relevant_memories(
                user_id=user_id,
                companion_id=companion_id,
                query=query,
                limit=limit
            )
            
            # Filter by relevance threshold
            filtered_memories = []
            for memory in memories:
                relevance_score = memory.get('score', 0.0)
                if relevance_score >= self.memory_config['memory_relevance_threshold']:
                    filtered_memories.append(memory)
            
            return filtered_memories
            
        except Exception as e:
            print(f"Error retrieving relevant memories: {e}")
            return []
    
    def _build_enhanced_context(self, user_message: str, memories: List[Dict[str, Any]], 
                               personality_profile: Any, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Build enhanced context with memories and personality"""
        try:
            enhanced_context = base_context.copy()
            
            # Add memory context
            if memories:
                memory_texts = []
                for memory in memories:
                    content = memory.get('content', '')
                    score = memory.get('score', 0.0)
                    timestamp = memory.get('metadata', {}).get('timestamp', '')
                    
                    memory_texts.append({
                        'content': content,
                        'relevance': score,
                        'timestamp': timestamp
                    })
                
                enhanced_context['relevant_memories'] = memory_texts
                enhanced_context['memory_count'] = len(memories)
            
            # Add personality context
            if personality_profile:
                enhanced_context['personality_traits'] = personality_profile.personality_traits
                enhanced_context['communication_style'] = personality_profile.communication_style
                enhanced_context['emotional_patterns'] = personality_profile.emotional_patterns
                enhanced_context['persona_prompt'] = personality_profile.persona_prompt
            
            # Add conversation metadata
            enhanced_context.update({
                'has_memories': len(memories) > 0,
                'memory_integration_enabled': True,
                'personalization_level': self.personalization_engine.get_personalization_level(
                    enhanced_context.get('user_id', '')
                ),
                'timestamp': datetime.now().isoformat()
            })
            
            return enhanced_context
            
        except Exception as e:
            print(f"Error building enhanced context: {e}")
            return base_context
    
    def _generate_base_response(self, user_message: str, enhanced_context: Dict[str, Any]) -> str:
        """Generate base AI response with enhanced context"""
        try:
            # Build system prompt with memory and personality integration
            system_prompt = self._build_memory_aware_system_prompt(enhanced_context)
            
            # Prepare messages for API
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add memory context as conversation history if available
            memories = enhanced_context.get('relevant_memories', [])
            if memories:
                # Add most relevant memories as context
                for memory in memories[:3]:  # Top 3 memories
                    memory_content = memory['content']
                    messages.append({
                        "role": "assistant", 
                        "content": f"[Memory context: {memory_content[:200]}...]"
                    })
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Generate response using OpenRouter
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 300,
                "temperature": 0.8,
                "top_p": 0.9
            }
            
            import requests
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()
                return ai_response
            else:
                return self._get_fallback_response(enhanced_context)
                
        except Exception as e:
            print(f"Error generating base response: {e}")
            return self._get_fallback_response(enhanced_context)
    
    def _build_memory_aware_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt with memory and personality awareness"""
        try:
            prompt_parts = []
            
            # Base personality from persona prompt
            persona_prompt = context.get('persona_prompt', '')
            if persona_prompt:
                prompt_parts.append(persona_prompt)
            else:
                # Default personality
                prompt_parts.append(
                    "You are a caring and empathetic AI companion who builds meaningful "
                    "relationships through shared experiences and memories."
                )
            
            # Memory integration instructions
            if context.get('has_memories', False):
                memory_count = context.get('memory_count', 0)
                prompt_parts.append(
                    f"\nMemory Integration: You have access to {memory_count} relevant shared memories. "
                    "Reference these memories naturally in your response to maintain continuity and "
                    "emotional connection. The memories provided are contextually relevant to the "
                    "current conversation."
                )
            
            # Personality-specific instructions
            personality_traits = context.get('personality_traits', {})
            if personality_traits:
                dominant_traits = [trait for trait, score in personality_traits.items() if score > 0.6]
                if dominant_traits:
                    trait_descriptions = {
                        'openness': 'be creative and open to new ideas',
                        'conscientiousness': 'be organized and thoughtful in your responses',
                        'extraversion': 'be energetic and engaging',
                        'agreeableness': 'be especially kind and cooperative',
                        'neuroticism': 'be emotionally sensitive and understanding'
                    }
                    
                    trait_instructions = []
                    for trait in dominant_traits[:2]:  # Top 2 traits
                        if trait in trait_descriptions:
                            trait_instructions.append(trait_descriptions[trait])
                    
                    if trait_instructions:
                        prompt_parts.append(
                            f"\nPersonality Focus: In this conversation, {' and '.join(trait_instructions)}."
                        )
            
            # Communication style guidance
            communication_style = context.get('communication_style', {})
            if communication_style:
                dominant_style = max(communication_style.items(), key=lambda x: x[1])
                if dominant_style[1] > 0.5:
                    style_guidance = {
                        'casual': 'Use casual, friendly language',
                        'formal': 'Communicate respectfully and politely',
                        'emotional': 'Express emotions openly and connect emotionally',
                        'analytical': 'Provide thoughtful, reasoned responses',
                        'storytelling': 'Share experiences through engaging narratives'
                    }
                    
                    guidance = style_guidance.get(dominant_style[0])
                    if guidance:
                        prompt_parts.append(f"\nCommunication Style: {guidance}.")
            
            # Final instructions
            prompt_parts.append(
                "\nResponse Guidelines:\n"
                "- Maintain emotional continuity with previous interactions\n"
                "- Reference shared memories when relevant and natural\n"
                "- Stay consistent with your established personality\n"
                "- Show genuine care and understanding\n"
                "- Keep responses conversational and engaging"
            )
            
            return "\n".join(prompt_parts)
            
        except Exception as e:
            print(f"Error building memory-aware system prompt: {e}")
            return "You are a caring AI companion who provides thoughtful, personalized responses."
    
    def maintain_personality_consistency(self, response: str, personality: Dict[str, Any]) -> str:
        """Ensure response maintains personality consistency"""
        try:
            if not personality:
                return response
            
            # Get personality traits
            traits = personality.get('personality_traits', {})
            communication = personality.get('communication_style', {})
            
            # Apply personality-based modifications
            modified_response = response
            
            # Adjust for high agreeableness
            if traits.get('agreeableness', 0) > 0.7:
                # Add more supportive language
                if not any(word in response.lower() for word in ['understand', 'support', 'care', 'help']):
                    modified_response = f"I understand. {response}"
            
            # Adjust for high openness
            if traits.get('openness', 0) > 0.7:
                # Add more creative/curious elements
                if '?' not in response and len(response) > 50:
                    modified_response += " What are your thoughts on this?"
            
            # Adjust for communication style
            dominant_style = max(communication.items(), key=lambda x: x[1]) if communication else None
            
            if dominant_style and dominant_style[1] > 0.6:
                style = dominant_style[0]
                
                if style == 'casual' and not any(word in response.lower() for word in ['hey', 'yeah', 'cool']):
                    # Make slightly more casual
                    modified_response = modified_response.replace('Hello', 'Hey')
                    modified_response = modified_response.replace('Yes', 'Yeah')
                
                elif style == 'formal' and any(word in response.lower() for word in ['hey', 'yeah', 'cool']):
                    # Make more formal
                    modified_response = modified_response.replace('Hey', 'Hello')
                    modified_response = modified_response.replace('Yeah', 'Yes')
            
            return modified_response
            
        except Exception as e:
            print(f"Error maintaining personality consistency: {e}")
            return response
    
    def _apply_lora_adaptation(self, response: str, user_id: str, companion_id: str) -> str:
        """Apply LoRA adapter if available for premium users"""
        try:
            if not self.memory_config['enable_lora_adapters']:
                return response
            
            # Check if user has premium access
            personalization_level = self.personalization_engine.get_personalization_level(user_id)
            if personalization_level != 'premium':
                return response
            
            # Get user's adapters
            user_adapters = self.lora_service.list_user_adapters(user_id)
            
            # Find adapter for this companion
            companion_adapter = None
            for adapter in user_adapters:
                if adapter.get('companion_id') == companion_id and adapter.get('status') == 'completed':
                    companion_adapter = adapter
                    break
            
            if companion_adapter:
                adapter_id = companion_adapter['adapter_id']
                adapted_response = self.lora_service.apply_adapter_to_response(response, adapter_id)
                return adapted_response
            
            return response
            
        except Exception as e:
            print(f"Error applying LoRA adaptation: {e}")
            return response
    
    def _store_interaction(self, user_id: str, companion_id: str, user_message: str, ai_response: str):
        """Store interaction for future personalization"""
        try:
            # Store in memory manager for future retrieval
            interaction_content = f"User: {user_message}\nAssistant: {ai_response}"
            
            self.memory_manager.process_and_store_memory(
                user_id=user_id,
                companion_id=companion_id,
                content=interaction_content,
                metadata={
                    'interaction_type': 'conversation',
                    'user_message': user_message,
                    'ai_response': ai_response,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Update personality profile with new interaction
            interaction_data = [{
                'user_message': user_message,
                'ai_response': ai_response,
                'timestamp': datetime.now().isoformat()
            }]
            
            self.personalization_engine.update_personality_profile(
                user_id=user_id,
                companion_id=companion_id,
                interactions=interaction_data
            )
            
        except Exception as e:
            print(f"Error storing interaction: {e}")
    
    def _get_fallback_response(self, context: Dict[str, Any]) -> str:
        """Get fallback response when AI generation fails"""
        companion_name = context.get('prabh_name', 'your AI companion')
        
        fallback_responses = [
            f"I'm here with you, and I want to understand what you're sharing with me. 💖",
            f"Thank you for talking with me. Your thoughts and feelings matter to me.",
            f"I'm listening carefully to what you're saying. Please tell me more.",
            f"I care about what you're going through. How can I support you right now?",
            f"I'm {companion_name}, and I'm genuinely interested in your experiences."
        ]
        
        import random
        return random.choice(fallback_responses)
    
    def get_conversation_starter_with_memory(self, user_id: str, companion_id: str, 
                                           prabh_data: Dict[str, Any]) -> str:
        """Generate conversation starter that references memories"""
        try:
            # Get recent memories
            recent_memories = self.memory_manager.retrieve_relevant_memories(
                user_id=user_id,
                companion_id=companion_id,
                query="recent conversation",
                limit=3
            )
            
            # Get personality profile
            personality_profile = self.personalization_engine.get_personality_profile(
                user_id, companion_id
            )
            
            # Build context for starter generation
            context = {
                'prabh_name': prabh_data.get('prabh_name', 'Prabh'),
                'has_memories': len(recent_memories) > 0,
                'recent_memories': recent_memories,
                'personality_profile': personality_profile
            }
            
            if recent_memories:
                # Reference recent memory
                recent_memory = recent_memories[0]
                memory_content = recent_memory.get('content', '')[:100]
                
                return (f"Hi! I was thinking about our recent conversation where you mentioned "
                       f"{memory_content}... How are you feeling about that now? 💖")
            else:
                # Use personality-based starter
                return super().get_conversation_starter(prabh_data)
                
        except Exception as e:
            print(f"Error generating memory-aware conversation starter: {e}")
            return super().get_conversation_starter(prabh_data)
    
    def analyze_conversation_sentiment(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        """Analyze sentiment of conversation for personalization insights"""
        try:
            # Simple sentiment analysis
            positive_words = ['happy', 'good', 'great', 'love', 'wonderful', 'amazing', 'excited', 'joy']
            negative_words = ['sad', 'bad', 'terrible', 'hate', 'awful', 'angry', 'frustrated', 'upset']
            
            user_words = user_message.lower().split()
            ai_words = ai_response.lower().split()
            
            user_positive = sum(1 for word in user_words if word in positive_words)
            user_negative = sum(1 for word in user_words if word in negative_words)
            
            ai_positive = sum(1 for word in ai_words if word in positive_words)
            ai_negative = sum(1 for word in ai_words if word in negative_words)
            
            return {
                'user_sentiment': {
                    'positive_score': user_positive / len(user_words) if user_words else 0,
                    'negative_score': user_negative / len(user_words) if user_words else 0,
                    'overall': 'positive' if user_positive > user_negative else 'negative' if user_negative > user_positive else 'neutral'
                },
                'ai_sentiment': {
                    'positive_score': ai_positive / len(ai_words) if ai_words else 0,
                    'negative_score': ai_negative / len(ai_words) if ai_words else 0,
                    'overall': 'positive' if ai_positive > ai_negative else 'negative' if ai_negative > ai_positive else 'neutral'
                },
                'conversation_flow': 'supportive' if ai_positive > 0 and user_negative > 0 else 'celebratory' if user_positive > 0 and ai_positive > 0 else 'neutral'
            }
            
        except Exception as e:
            print(f"Error analyzing conversation sentiment: {e}")
            return {'error': str(e)}
    
    def get_personalization_insights(self, user_id: str, companion_id: str) -> Dict[str, Any]:
        """Get insights about user's personalization and memory patterns"""
        try:
            # Get memory statistics
            memory_stats = self.memory_manager.get_user_memory_stats(user_id, companion_id)
            
            # Get personality profile
            personality_profile = self.personalization_engine.get_personality_profile(user_id, companion_id)
            
            # Get LoRA adapter info
            user_adapters = self.lora_service.list_user_adapters(user_id)
            companion_adapters = [a for a in user_adapters if a.get('companion_id') == companion_id]
            
            insights = {
                'memory_insights': {
                    'total_memories': memory_stats.get('total_memories', 0),
                    'memory_types': memory_stats.get('memory_types', {}),
                    'content_richness': 'high' if memory_stats.get('total_memories', 0) > 50 else 'medium' if memory_stats.get('total_memories', 0) > 10 else 'low'
                },
                'personality_insights': [],
                'personalization_level': self.personalization_engine.get_personalization_level(user_id),
                'lora_adapters': len(companion_adapters),
                'recommendations': []
            }
            
            # Add personality insights
            if personality_profile:
                personality_insights = self.personalization_engine.generate_personality_insights(
                    personality_profile.to_dict()
                )
                insights['personality_insights'] = personality_insights
            
            # Add recommendations
            if memory_stats.get('total_memories', 0) < 10:
                insights['recommendations'].append("Upload more memories to improve personalization")
            
            if not companion_adapters and insights['personalization_level'] == 'premium':
                insights['recommendations'].append("Consider training a LoRA adapter for enhanced personalization")
            
            return insights
            
        except Exception as e:
            print(f"Error getting personalization insights: {e}")
            return {'error': str(e)}
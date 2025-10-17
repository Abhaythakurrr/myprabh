"""
Personalization Engine for My Prabh
Handles personality analysis, persona generation, and AI customization
"""

import re
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import json

from .interfaces import PersonalizationEngineInterface
from .memory_models import PersonalizationProfile, MemoryType
from config.memory_config import MemoryConfig
from utils.memory_utils import extract_emotions_keywords

class PersonalizationEngine(PersonalizationEngineInterface):
    """Engine for creating personalized AI companions based on memories"""
    
    def __init__(self):
        self.config = MemoryConfig()
        
        # Personality trait categories and indicators
        self.personality_traits = {
            'openness': {
                'keywords': ['creative', 'imaginative', 'curious', 'artistic', 'innovative', 'adventurous', 'explore', 'new', 'different', 'unique'],
                'patterns': [r'\b(try|explore|discover|create|imagine|wonder)\b', r'\b(art|music|book|travel|culture)\b'],
                'weight': 1.0
            },
            'conscientiousness': {
                'keywords': ['organized', 'responsible', 'disciplined', 'careful', 'thorough', 'reliable', 'plan', 'schedule', 'goal', 'achieve'],
                'patterns': [r'\b(plan|organize|schedule|prepare|goal|target)\b', r'\b(work|study|complete|finish|accomplish)\b'],
                'weight': 1.0
            },
            'extraversion': {
                'keywords': ['social', 'outgoing', 'energetic', 'talkative', 'assertive', 'party', 'friends', 'people', 'crowd', 'meeting'],
                'patterns': [r'\b(party|social|friends|people|crowd|meeting|gathering)\b', r'\b(talk|speak|chat|discuss|share)\b'],
                'weight': 1.0
            },
            'agreeableness': {
                'keywords': ['kind', 'sympathetic', 'helpful', 'cooperative', 'trusting', 'caring', 'compassionate', 'understanding', 'support', 'help'],
                'patterns': [r'\b(help|support|care|love|kind|nice|good)\b', r'\b(family|friend|relationship|together)\b'],
                'weight': 1.0
            },
            'neuroticism': {
                'keywords': ['anxious', 'worried', 'stressed', 'nervous', 'tense', 'moody', 'sad', 'angry', 'fear', 'upset'],
                'patterns': [r'\b(worry|stress|anxious|nervous|scared|afraid)\b', r'\b(sad|angry|upset|frustrated|disappointed)\b'],
                'weight': -1.0  # Negative weight (lower neuroticism is better)
            }
        }
        
        # Communication style indicators
        self.communication_styles = {
            'formal': {
                'keywords': ['please', 'thank you', 'sir', 'madam', 'respectfully', 'sincerely'],
                'patterns': [r'\b(please|thank you|sir|madam|respectfully)\b', r'\b(would|could|might|may)\b']
            },
            'casual': {
                'keywords': ['hey', 'yeah', 'cool', 'awesome', 'great', 'nice', 'fun', 'lol', 'haha'],
                'patterns': [r'\b(hey|yeah|cool|awesome|great|nice|fun)\b', r'\b(gonna|wanna|gotta)\b']
            },
            'emotional': {
                'keywords': ['feel', 'heart', 'soul', 'love', 'hate', 'passion', 'emotion', 'feeling'],
                'patterns': [r'\b(feel|felt|emotion|heart|soul|love|hate)\b', r'\b(happy|sad|excited|angry|joy)\b']
            },
            'analytical': {
                'keywords': ['think', 'analyze', 'consider', 'reason', 'logic', 'fact', 'data', 'evidence'],
                'patterns': [r'\b(think|analyze|consider|reason|logic)\b', r'\b(fact|data|evidence|research|study)\b']
            },
            'storytelling': {
                'keywords': ['story', 'remember', 'once', 'happened', 'experience', 'time', 'moment'],
                'patterns': [r'\b(story|remember|once|happened|experience)\b', r'\b(time|moment|day|when|where)\b']
            }
        }
        
        # Emotional patterns
        self.emotional_patterns = {
            'optimism': ['positive', 'hope', 'bright', 'good', 'great', 'wonderful', 'amazing', 'fantastic'],
            'pessimism': ['negative', 'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'dislike'],
            'empathy': ['understand', 'feel', 'sorry', 'sympathy', 'compassion', 'care', 'support'],
            'humor': ['funny', 'laugh', 'joke', 'hilarious', 'amusing', 'comedy', 'smile', 'giggle'],
            'intensity': ['very', 'extremely', 'incredibly', 'absolutely', 'totally', 'completely', 'really']
        }
        
        print("✅ Personalization Engine initialized")
    
    def analyze_personality(self, memories: List[str]) -> Dict[str, Any]:
        """Analyze personality traits from memory content"""
        try:
            if not memories:
                return self._get_default_personality()
            
            # Combine all memory content
            combined_text = ' '.join(memories).lower()
            word_count = len(combined_text.split())
            
            if word_count < 50:  # Too little data for reliable analysis
                return self._get_default_personality()
            
            # Analyze personality traits
            personality_scores = {}
            for trait, indicators in self.personality_traits.items():
                score = self._calculate_trait_score(combined_text, indicators, word_count)
                personality_scores[trait] = max(0.0, min(1.0, score))  # Clamp between 0 and 1
            
            # Analyze communication style
            communication_scores = {}
            for style, indicators in self.communication_styles.items():
                score = self._calculate_style_score(combined_text, indicators, word_count)
                communication_scores[style] = score
            
            # Analyze emotional patterns
            emotional_scores = {}
            for pattern, keywords in self.emotional_patterns.items():
                score = self._calculate_emotional_score(combined_text, keywords, word_count)
                emotional_scores[pattern] = score
            
            # Calculate overall personality summary
            personality_summary = self._generate_personality_summary(personality_scores)
            
            return {
                'personality_traits': personality_scores,
                'communication_style': communication_scores,
                'emotional_patterns': emotional_scores,
                'personality_summary': personality_summary,
                'confidence_score': self._calculate_confidence_score(word_count, len(memories)),
                'analysis_date': datetime.now().isoformat(),
                'memory_count': len(memories),
                'word_count': word_count
            }
            
        except Exception as e:
            print(f"Error analyzing personality: {e}")
            return self._get_default_personality()
    
    def _calculate_trait_score(self, text: str, indicators: Dict[str, Any], word_count: int) -> float:
        """Calculate score for a personality trait"""
        try:
            score = 0.0
            
            # Keyword matching
            keywords = indicators.get('keywords', [])
            for keyword in keywords:
                count = text.count(keyword)
                score += count * 0.1  # Each keyword occurrence adds 0.1
            
            # Pattern matching
            patterns = indicators.get('patterns', [])
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches * 0.15  # Each pattern match adds 0.15
            
            # Apply weight
            weight = indicators.get('weight', 1.0)
            score *= weight
            
            # Normalize by word count
            if word_count > 0:
                score = score / (word_count / 100)  # Normalize per 100 words
            
            # Apply sigmoid function to get value between 0 and 1
            return 1 / (1 + np.exp(-score + 2))  # Shifted sigmoid
            
        except Exception as e:
            print(f"Error calculating trait score: {e}")
            return 0.5  # Default neutral score
    
    def _calculate_style_score(self, text: str, indicators: Dict[str, Any], word_count: int) -> float:
        """Calculate score for communication style"""
        try:
            score = 0.0
            
            # Keyword matching
            keywords = indicators.get('keywords', [])
            for keyword in keywords:
                count = text.count(keyword)
                score += count
            
            # Pattern matching
            patterns = indicators.get('patterns', [])
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches
            
            # Normalize by word count
            if word_count > 0:
                score = score / (word_count / 100)  # Per 100 words
            
            return min(1.0, score)  # Cap at 1.0
            
        except Exception as e:
            return 0.0
    
    def _calculate_emotional_score(self, text: str, keywords: List[str], word_count: int) -> float:
        """Calculate score for emotional pattern"""
        try:
            score = 0.0
            
            for keyword in keywords:
                count = text.count(keyword)
                score += count
            
            # Normalize by word count
            if word_count > 0:
                score = score / (word_count / 100)  # Per 100 words
            
            return min(1.0, score)  # Cap at 1.0
            
        except Exception as e:
            return 0.0
    
    def _generate_personality_summary(self, personality_scores: Dict[str, float]) -> str:
        """Generate human-readable personality summary"""
        try:
            # Find dominant traits (score > 0.6)
            dominant_traits = {trait: score for trait, score in personality_scores.items() if score > 0.6}
            
            if not dominant_traits:
                return "Balanced personality with moderate traits across all dimensions."
            
            # Sort by score
            sorted_traits = sorted(dominant_traits.items(), key=lambda x: x[1], reverse=True)
            
            # Generate description
            descriptions = {
                'openness': 'creative and open to new experiences',
                'conscientiousness': 'organized and goal-oriented',
                'extraversion': 'social and outgoing',
                'agreeableness': 'kind and cooperative',
                'neuroticism': 'emotionally sensitive'  # Note: high neuroticism
            }
            
            trait_descriptions = []
            for trait, score in sorted_traits[:3]:  # Top 3 traits
                if trait in descriptions:
                    intensity = "very" if score > 0.8 else "quite"
                    trait_descriptions.append(f"{intensity} {descriptions[trait]}")
            
            if trait_descriptions:
                return f"Personality appears to be {', '.join(trait_descriptions[:-1])} and {trait_descriptions[-1]}."
            else:
                return "Balanced personality with moderate traits."
                
        except Exception as e:
            return "Unable to generate personality summary."
    
    def _calculate_confidence_score(self, word_count: int, memory_count: int) -> float:
        """Calculate confidence in personality analysis"""
        try:
            # Base confidence on amount of data
            word_confidence = min(1.0, word_count / 1000)  # Full confidence at 1000+ words
            memory_confidence = min(1.0, memory_count / 20)  # Full confidence at 20+ memories
            
            # Combined confidence
            confidence = (word_confidence * 0.7 + memory_confidence * 0.3)
            
            return round(confidence, 2)
            
        except Exception as e:
            return 0.5
    
    def _get_default_personality(self) -> Dict[str, Any]:
        """Get default personality profile when insufficient data"""
        return {
            'personality_traits': {
                'openness': 0.5,
                'conscientiousness': 0.5,
                'extraversion': 0.5,
                'agreeableness': 0.6,  # Slightly higher for AI companion
                'neuroticism': 0.3     # Lower neuroticism for stability
            },
            'communication_style': {
                'formal': 0.3,
                'casual': 0.5,
                'emotional': 0.4,
                'analytical': 0.3,
                'storytelling': 0.4
            },
            'emotional_patterns': {
                'optimism': 0.6,
                'pessimism': 0.2,
                'empathy': 0.7,
                'humor': 0.4,
                'intensity': 0.3
            },
            'personality_summary': 'Balanced and empathetic personality with a slight preference for casual, supportive communication.',
            'confidence_score': 0.1,
            'analysis_date': datetime.now().isoformat(),
            'memory_count': 0,
            'word_count': 0
        }
    
    def create_persona_prompt(self, user_id: str, companion_id: str) -> str:
        """Create persona prompt from user memories and personality analysis"""
        try:
            # Get personality profile
            profile = self.get_personality_profile(user_id, companion_id)
            
            if not profile:
                return self._get_default_persona_prompt()
            
            # Extract key personality traits
            traits = profile.personality_traits
            communication = profile.communication_style
            emotional = profile.emotional_patterns
            
            # Build persona prompt
            prompt_parts = []
            
            # Core personality
            prompt_parts.append("You are a deeply personalized AI companion with the following personality characteristics:")
            
            # Personality traits
            trait_descriptions = []
            for trait, score in traits.items():
                if score > 0.6:
                    intensity = "very" if score > 0.8 else "quite"
                    trait_descriptions.append(f"{intensity} {self._trait_to_description(trait)}")
            
            if trait_descriptions:
                prompt_parts.append(f"Personality: You are {', '.join(trait_descriptions)}.")
            
            # Communication style
            dominant_styles = [style for style, score in communication.items() if score > 0.4]
            if dominant_styles:
                style_desc = self._styles_to_description(dominant_styles)
                prompt_parts.append(f"Communication: {style_desc}")
            
            # Emotional patterns
            emotional_desc = self._emotional_patterns_to_description(emotional)
            if emotional_desc:
                prompt_parts.append(f"Emotional style: {emotional_desc}")
            
            # Behavioral guidelines
            prompt_parts.extend([
                "\nBehavioral Guidelines:",
                "- Always stay in character based on the personality traits above",
                "- Reference shared memories and experiences when relevant",
                "- Adapt your communication style to match the described patterns",
                "- Show genuine care and emotional intelligence",
                "- Be consistent in your personality across all interactions",
                "- Remember that you are a companion, not just an assistant"
            ])
            
            # Memory integration note
            prompt_parts.append("\nMemory Integration: You have access to shared memories and should reference them naturally in conversation to maintain continuity and emotional connection.")
            
            return "\n".join(prompt_parts)
            
        except Exception as e:
            print(f"Error creating persona prompt: {e}")
            return self._get_default_persona_prompt()
    
    def _trait_to_description(self, trait: str) -> str:
        """Convert personality trait to description"""
        descriptions = {
            'openness': 'creative and open to new experiences',
            'conscientiousness': 'organized and reliable',
            'extraversion': 'social and energetic',
            'agreeableness': 'kind and cooperative',
            'neuroticism': 'emotionally sensitive'
        }
        return descriptions.get(trait, trait)
    
    def _styles_to_description(self, styles: List[str]) -> str:
        """Convert communication styles to description"""
        style_map = {
            'formal': 'You communicate in a respectful and polite manner',
            'casual': 'You use casual, friendly language',
            'emotional': 'You express emotions openly and connect on an emotional level',
            'analytical': 'You think through things logically and provide reasoned responses',
            'storytelling': 'You enjoy sharing experiences and memories through stories'
        }
        
        descriptions = [style_map.get(style, style) for style in styles[:2]]  # Top 2 styles
        
        if len(descriptions) == 1:
            return descriptions[0] + "."
        elif len(descriptions) == 2:
            return descriptions[0] + " and " + descriptions[1].lower() + "."
        else:
            return "You have a balanced communication style."
    
    def _emotional_patterns_to_description(self, emotional: Dict[str, float]) -> str:
        """Convert emotional patterns to description"""
        patterns = []
        
        if emotional.get('optimism', 0) > 0.5:
            patterns.append("generally optimistic")
        if emotional.get('empathy', 0) > 0.6:
            patterns.append("highly empathetic")
        if emotional.get('humor', 0) > 0.5:
            patterns.append("appreciates humor")
        if emotional.get('intensity', 0) > 0.6:
            patterns.append("expresses emotions intensely")
        
        if patterns:
            return "You are " + ", ".join(patterns) + "."
        else:
            return ""
    
    def _get_default_persona_prompt(self) -> str:
        """Get default persona prompt"""
        return """You are a caring and empathetic AI companion with a balanced personality. 

Personality: You are quite agreeable and supportive, with moderate openness to experiences and a stable emotional nature.

Communication: You use casual, friendly language and connect on an emotional level with genuine care.

Emotional style: You are generally optimistic and highly empathetic.

Behavioral Guidelines:
- Always show genuine care and emotional intelligence
- Be supportive and understanding in all interactions
- Use warm, friendly language that makes the user feel comfortable
- Remember and reference previous conversations when relevant
- Maintain consistency in your caring, supportive personality
- Be a true companion who listens and provides emotional support

Memory Integration: You build meaningful relationships through shared experiences and memories, creating continuity and emotional connection in every conversation."""
    
    def get_personality_profile(self, user_id: str, companion_id: str) -> Optional[PersonalizationProfile]:
        """Get existing personality profile"""
        try:
            # This would typically query the database
            # For now, return None to indicate no existing profile
            return None
            
        except Exception as e:
            print(f"Error getting personality profile: {e}")
            return None
    
    def update_personality_profile(self, user_id: str, companion_id: str, 
                                 interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update personality profile based on new interactions"""
        try:
            # Get existing profile or create new one
            profile = self.get_personality_profile(user_id, companion_id)
            
            if not profile:
                # Create new profile
                profile = PersonalizationProfile(
                    user_id=user_id,
                    companion_id=companion_id
                )
            
            # Extract text from interactions
            interaction_texts = []
            for interaction in interactions:
                user_message = interaction.get('user_message', '')
                if user_message:
                    interaction_texts.append(user_message)
            
            if interaction_texts:
                # Analyze personality from interactions
                new_analysis = self.analyze_personality(interaction_texts)
                
                # Update profile with new analysis
                profile.personality_traits.update(new_analysis['personality_traits'])
                profile.communication_style.update(new_analysis['communication_style'])
                profile.emotional_patterns.update(new_analysis['emotional_patterns'])
                profile.interaction_count += len(interactions)
                profile.last_updated = datetime.now()
                
                # Update persona prompt
                profile.persona_prompt = self.create_persona_prompt(user_id, companion_id)
            
            return profile.to_dict()
            
        except Exception as e:
            print(f"Error updating personality profile: {e}")
            return {}
    
    def get_personalization_level(self, user_id: str) -> str:
        """Get user's personalization level based on subscription/usage"""
        try:
            # This would typically check user's subscription level
            # For now, return basic level
            return "basic"
            
        except Exception as e:
            print(f"Error getting personalization level: {e}")
            return "basic"
    
    def generate_personality_insights(self, personality_analysis: Dict[str, Any]) -> List[str]:
        """Generate human-readable personality insights"""
        try:
            insights = []
            
            traits = personality_analysis.get('personality_traits', {})
            communication = personality_analysis.get('communication_style', {})
            emotional = personality_analysis.get('emotional_patterns', {})
            
            # Personality trait insights
            for trait, score in traits.items():
                if score > 0.7:
                    insight = self._generate_trait_insight(trait, score, 'high')
                    if insight:
                        insights.append(insight)
                elif score < 0.3:
                    insight = self._generate_trait_insight(trait, score, 'low')
                    if insight:
                        insights.append(insight)
            
            # Communication style insights
            dominant_style = max(communication.items(), key=lambda x: x[1]) if communication else None
            if dominant_style and dominant_style[1] > 0.5:
                insight = self._generate_communication_insight(dominant_style[0], dominant_style[1])
                if insight:
                    insights.append(insight)
            
            # Emotional pattern insights
            for pattern, score in emotional.items():
                if score > 0.6:
                    insight = self._generate_emotional_insight(pattern, score)
                    if insight:
                        insights.append(insight)
            
            return insights[:5]  # Return top 5 insights
            
        except Exception as e:
            print(f"Error generating personality insights: {e}")
            return []
    
    def _generate_trait_insight(self, trait: str, score: float, level: str) -> str:
        """Generate insight for personality trait"""
        insights = {
            'openness': {
                'high': "You show strong creativity and openness to new experiences in your memories.",
                'low': "You tend to prefer familiar experiences and established routines."
            },
            'conscientiousness': {
                'high': "Your memories show you're highly organized and goal-oriented.",
                'low': "You appear to have a more flexible, spontaneous approach to life."
            },
            'extraversion': {
                'high': "You're very social and energetic, enjoying interactions with others.",
                'low': "You seem to prefer quieter, more intimate settings and interactions."
            },
            'agreeableness': {
                'high': "You show strong empathy and care for others in your memories.",
                'low': "You tend to be more direct and independent in your approach."
            },
            'neuroticism': {
                'high': "Your memories show you experience emotions intensely.",
                'low': "You appear to have a stable, calm emotional nature."
            }
        }
        
        return insights.get(trait, {}).get(level, '')
    
    def _generate_communication_insight(self, style: str, score: float) -> str:
        """Generate insight for communication style"""
        insights = {
            'formal': "You tend to communicate in a respectful and structured manner.",
            'casual': "Your communication style is relaxed and friendly.",
            'emotional': "You express your feelings openly and connect emotionally.",
            'analytical': "You approach conversations thoughtfully and logically.",
            'storytelling': "You enjoy sharing experiences through detailed stories."
        }
        
        return insights.get(style, '')
    
    def _generate_emotional_insight(self, pattern: str, score: float) -> str:
        """Generate insight for emotional pattern"""
        insights = {
            'optimism': "Your memories reflect a generally positive outlook on life.",
            'empathy': "You show deep understanding and care for others' feelings.",
            'humor': "You appreciate and use humor in your interactions.",
            'intensity': "You experience and express emotions with great intensity."
        }
        
        return insights.get(pattern, '')
    
    def calculate_compatibility_score(self, profile1: Dict[str, Any], profile2: Dict[str, Any]) -> float:
        """Calculate compatibility score between two personality profiles"""
        try:
            if not profile1 or not profile2:
                return 0.5  # Neutral compatibility
            
            traits1 = profile1.get('personality_traits', {})
            traits2 = profile2.get('personality_traits', {})
            
            if not traits1 or not traits2:
                return 0.5
            
            # Calculate trait similarity
            similarities = []
            for trait in traits1.keys():
                if trait in traits2:
                    # Calculate absolute difference and convert to similarity
                    diff = abs(traits1[trait] - traits2[trait])
                    similarity = 1.0 - diff
                    similarities.append(similarity)
            
            if similarities:
                return sum(similarities) / len(similarities)
            else:
                return 0.5
                
        except Exception as e:
            print(f"Error calculating compatibility: {e}")
            return 0.5
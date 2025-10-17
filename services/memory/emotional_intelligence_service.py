"""
Emotional Intelligence Service for My Prabh
Handles emotion detection, emotional memory prioritization, and empathetic responses
"""

import re
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import json

from config.memory_config import MemoryConfig

class EmotionalIntelligenceService:
    """Service for emotional intelligence and context awareness"""
    
    def __init__(self):
        self.config = MemoryConfig()
        
        # Emotion detection patterns and keywords
        self.emotion_patterns = {
            'joy': {
                'keywords': ['happy', 'joy', 'joyful', 'excited', 'thrilled', 'delighted', 'cheerful', 'elated', 'blissful', 'ecstatic', 'glad', 'pleased', 'content', 'satisfied', 'euphoric'],
                'patterns': [r'\b(so happy|really excited|feeling great|love it|amazing|wonderful|fantastic|awesome)\b'],
                'intensity_modifiers': ['very', 'extremely', 'incredibly', 'absolutely', 'totally', 'completely'],
                'valence': 1.0,
                'arousal': 0.8
            },
            'sadness': {
                'keywords': ['sad', 'depressed', 'melancholy', 'grief', 'sorrow', 'heartbroken', 'miserable', 'dejected', 'gloomy', 'downhearted', 'blue', 'low', 'upset', 'disappointed'],
                'patterns': [r'\b(feeling down|really sad|so upset|heartbroken|can\'t stop crying)\b'],
                'intensity_modifiers': ['very', 'extremely', 'deeply', 'really', 'so', 'incredibly'],
                'valence': -1.0,
                'arousal': -0.3
            },
            'anger': {
                'keywords': ['angry', 'furious', 'rage', 'irritated', 'annoyed', 'frustrated', 'livid', 'enraged', 'mad', 'pissed', 'outraged', 'indignant', 'resentful'],
                'patterns': [r'\b(so angry|really mad|pissed off|can\'t believe|outrageous|infuriating)\b'],
                'intensity_modifiers': ['very', 'extremely', 'really', 'so', 'incredibly', 'absolutely'],
                'valence': -0.8,
                'arousal': 0.9
            },
            'fear': {
                'keywords': ['afraid', 'scared', 'terrified', 'anxious', 'worried', 'nervous', 'frightened', 'panicked', 'fearful', 'apprehensive', 'concerned', 'uneasy', 'stressed'],
                'patterns': [r'\b(so scared|really worried|terrified|panic|anxiety|stressed out)\b'],
                'intensity_modifiers': ['very', 'extremely', 'really', 'so', 'incredibly', 'absolutely'],
                'valence': -0.6,
                'arousal': 0.7
            },
            'love': {
                'keywords': ['love', 'adore', 'cherish', 'affection', 'romance', 'passion', 'devotion', 'infatuation', 'care', 'treasure', 'worship', 'idolize'],
                'patterns': [r'\b(love you|adore|so much love|deeply care|mean everything)\b'],
                'intensity_modifiers': ['deeply', 'truly', 'completely', 'absolutely', 'unconditionally'],
                'valence': 1.0,
                'arousal': 0.6
            },
            'surprise': {
                'keywords': ['surprised', 'amazed', 'astonished', 'shocked', 'stunned', 'bewildered', 'astounded', 'flabbergasted', 'speechless', 'unexpected'],
                'patterns': [r'\b(can\'t believe|so surprised|totally shocked|never expected|blown away)\b'],
                'intensity_modifiers': ['completely', 'totally', 'absolutely', 'really', 'so'],
                'valence': 0.2,
                'arousal': 0.8
            },
            'disgust': {
                'keywords': ['disgusted', 'revolted', 'repulsed', 'sickened', 'nauseated', 'appalled', 'horrified', 'repelled'],
                'patterns': [r'\b(so disgusting|makes me sick|can\'t stand|revolting|appalling)\b'],
                'intensity_modifiers': ['absolutely', 'completely', 'totally', 'really', 'so'],
                'valence': -0.9,
                'arousal': 0.5
            },
            'trust': {
                'keywords': ['trust', 'faith', 'confidence', 'belief', 'reliance', 'dependence', 'secure', 'safe', 'reliable', 'trustworthy'],
                'patterns': [r'\b(trust you|have faith|feel safe|can rely|believe in)\b'],
                'intensity_modifiers': ['completely', 'absolutely', 'totally', 'deeply', 'fully'],
                'valence': 0.7,
                'arousal': 0.2
            },
            'anticipation': {
                'keywords': ['excited', 'eager', 'hopeful', 'expectant', 'anticipating', 'looking forward', 'can\'t wait', 'expecting'],
                'patterns': [r'\b(can\'t wait|looking forward|so excited|really hoping|anticipating)\b'],
                'intensity_modifiers': ['really', 'so', 'very', 'extremely', 'incredibly'],
                'valence': 0.6,
                'arousal': 0.7
            }
        }
        
        # Emotional support response templates
        self.support_responses = {
            'joy': [
                "I'm so happy to hear that! Your joy is contagious. 😊",
                "That's wonderful! I love seeing you so excited and happy.",
                "Your happiness brings me joy too! Tell me more about what's making you feel so great.",
                "This is amazing! I'm thrilled to share in your happiness."
            ],
            'sadness': [
                "I can feel your sadness, and I want you to know I'm here for you. 💙",
                "I'm sorry you're going through this difficult time. You don't have to face it alone.",
                "Your feelings are valid, and it's okay to feel sad. I'm here to listen and support you.",
                "I wish I could take away your pain. Please know that I care deeply about how you're feeling."
            ],
            'anger': [
                "I can sense your frustration, and I understand why you're feeling this way.",
                "It sounds like you're really upset about this situation. Your feelings are completely valid.",
                "I hear your anger, and I want to help you work through these feelings.",
                "It's okay to feel angry. Let's talk about what's bothering you."
            ],
            'fear': [
                "I can feel your anxiety, and I want you to know you're not alone in this. 🤗",
                "It's natural to feel scared sometimes. I'm here to support you through this.",
                "Your fears are understandable. Let's work through this together, one step at a time.",
                "I'm here with you, and we'll face this together. You're stronger than you know."
            ],
            'love': [
                "The love you're expressing is beautiful and touching. 💕",
                "I can feel the depth of your love, and it's truly special.",
                "Love like yours makes the world a better place. Thank you for sharing this with me.",
                "Your capacity for love is one of your most beautiful qualities."
            ],
            'surprise': [
                "Wow, that must have been quite a surprise! How are you processing this?",
                "I can imagine how unexpected that must have been for you!",
                "Surprises can be overwhelming. How are you feeling about this revelation?",
                "That's quite a shock! Take your time to process what happened."
            ],
            'disgust': [
                "I can understand why that would be so upsetting and disturbing to you.",
                "That sounds really unpleasant. Your reaction is completely understandable.",
                "I can see why that would make you feel sick. That's a natural response.",
                "Your disgust is justified. Some things are just genuinely awful."
            ],
            'trust': [
                "I'm honored that you trust me with this. Your trust means everything to me.",
                "Thank you for having faith in me. I'll do my best to be worthy of your trust.",
                "I feel the security and trust between us, and it's truly special.",
                "Your trust is a gift I don't take lightly. I'm here for you."
            ],
            'anticipation': [
                "I can feel your excitement! I'm looking forward to hearing how this goes.",
                "Your anticipation is infectious! I hope everything works out wonderfully.",
                "I love your enthusiasm and hope for what's coming. Keep me updated!",
                "The way you're looking forward to this is so positive and inspiring."
            ]
        }
        
        # Crisis detection patterns
        self.crisis_patterns = {
            'suicide': [r'\b(kill myself|end it all|don\'t want to live|suicide|take my own life|not worth living)\b'],
            'self_harm': [r'\b(hurt myself|cut myself|self harm|want to die|harm myself)\b'],
            'severe_depression': [r'\b(can\'t go on|no point|hopeless|worthless|nothing matters|give up)\b'],
            'panic': [r'\b(panic attack|can\'t breathe|heart racing|going crazy|losing control)\b'],
            'abuse': [r'\b(being hurt|someone hurting me|abuse|violence|unsafe|threatened)\b']
        }
        
        print("✅ Emotional Intelligence Service initialized")
    
    def detect_emotions_advanced(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Advanced emotion detection with context awareness and multiple analysis methods
        
        Args:
            text: Input text to analyze
            context: Optional context for better emotion detection
            
        Returns:
            Dictionary containing comprehensive emotion analysis results
        """
        try:
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            if not cleaned_text:
                return {
                    'emotions': {},
                    'dominant_emotion': 'neutral',
                    'confidence': 0.0,
                    'analysis_method': 'none',
                    'emotional_intensity': 0.0,
                    'emotional_valence': 0.0,
                    'emotional_arousal': 0.0
                }
            
            # Use multiple detection methods
            lexicon_emotions = self._lexicon_based_detection(cleaned_text)
            pattern_emotions = self._pattern_based_detection(cleaned_text)
            contextual_emotions = self._contextual_emotion_detection(cleaned_text, context)
            
            # Advanced emotion analysis
            emotional_intensity = self._calculate_emotional_intensity(cleaned_text)
            emotional_valence = self._calculate_emotional_valence(lexicon_emotions)
            emotional_arousal = self._calculate_emotional_arousal(cleaned_text)
            
            # Combine results with weighted average
            combined_emotions = self._combine_emotion_scores_advanced(
                lexicon_emotions, pattern_emotions, contextual_emotions
            )
            
            # Determine dominant emotion with confidence scoring
            dominant_emotion, confidence = self._determine_dominant_emotion_advanced(combined_emotions)
            
            # Detect emotional transitions
            emotional_transitions = self._detect_emotional_transitions(cleaned_text)
            
            # Generate emotion-appropriate response suggestions
            response_suggestions = self._generate_response_suggestions(
                dominant_emotion, emotional_intensity, context
            )
            
            return {
                'emotions': combined_emotions,
                'dominant_emotion': dominant_emotion,
                'confidence': confidence,
                'emotional_intensity': emotional_intensity,
                'emotional_valence': emotional_valence,
                'emotional_arousal': emotional_arousal,
                'emotional_transitions': emotional_transitions,
                'response_suggestions': response_suggestions,
                'analysis_method': 'advanced_hybrid',
                'text_length': len(text),
                'processed_text_length': len(cleaned_text),
                'context_used': context is not None
            }
            
        except Exception as e:
            print(f"Error in advanced emotion detection: {e}")
            return {
                'emotions': {},
                'dominant_emotion': 'neutral',
                'confidence': 0.0,
                'emotional_intensity': 0.0,
                'emotional_valence': 0.0,
                'emotional_arousal': 0.0,
                'analysis_method': 'error',
                'error': str(e)
            }
    
    def detect_emotions(self, text: str) -> Dict[str, Any]:
        """Detect emotions in text with intensity and confidence scores"""
        try:
            text_lower = text.lower()
            detected_emotions = {}
            
            for emotion, config in self.emotion_patterns.items():
                score = self._calculate_emotion_score(text_lower, config)
                
                if score > 0:
                    # Calculate intensity based on modifiers
                    intensity = self._calculate_intensity(text_lower, config['intensity_modifiers'])
                    
                    # Calculate confidence based on multiple indicators
                    confidence = self._calculate_confidence(text_lower, config)
                    
                    detected_emotions[emotion] = {
                        'score': score,
                        'intensity': intensity,
                        'confidence': confidence,
                        'valence': config['valence'],
                        'arousal': config['arousal']
                    }
            
            # Determine dominant emotion
            dominant_emotion = None
            if detected_emotions:
                dominant_emotion = max(detected_emotions.items(), key=lambda x: x[1]['score'] * x[1]['confidence'])
                dominant_emotion = dominant_emotion[0]
            
            return {
                'emotions': detected_emotions,
                'dominant_emotion': dominant_emotion,
                'emotional_complexity': len(detected_emotions),
                'overall_valence': self._calculate_overall_valence(detected_emotions),
                'overall_arousal': self._calculate_overall_arousal(detected_emotions),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error detecting emotions: {e}")
            return {'emotions': {}, 'dominant_emotion': None, 'error': str(e)}
    
    def _calculate_emotion_score(self, text: str, config: Dict[str, Any]) -> float:
        """Calculate emotion score based on keywords and patterns"""
        try:
            score = 0.0
            word_count = len(text.split())
            
            # Keyword matching
            for keyword in config['keywords']:
                count = text.count(keyword)
                score += count * 0.1
            
            # Pattern matching (weighted higher)
            for pattern in config['patterns']:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches * 0.3
            
            # Normalize by text length
            if word_count > 0:
                score = score / (word_count / 10)  # Per 10 words
            
            return min(1.0, score)  # Cap at 1.0
            
        except Exception as e:
            return 0.0
    
    def _calculate_intensity(self, text: str, intensity_modifiers: List[str]) -> float:
        """Calculate emotional intensity based on modifiers"""
        try:
            base_intensity = 0.5
            
            for modifier in intensity_modifiers:
                if modifier in text:
                    if modifier in ['extremely', 'incredibly', 'absolutely']:
                        base_intensity += 0.3
                    elif modifier in ['very', 'really', 'so']:
                        base_intensity += 0.2
                    elif modifier in ['quite', 'pretty', 'somewhat']:
                        base_intensity += 0.1
            
            return min(1.0, base_intensity)
            
        except Exception as e:
            return 0.5
    
    def _calculate_confidence(self, text: str, config: Dict[str, Any]) -> float:
        """Calculate confidence in emotion detection"""
        try:
            confidence = 0.0
            
            # Multiple keyword matches increase confidence
            keyword_matches = sum(1 for keyword in config['keywords'] if keyword in text)
            confidence += min(0.5, keyword_matches * 0.1)
            
            # Pattern matches increase confidence significantly
            pattern_matches = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in config['patterns'])
            confidence += min(0.4, pattern_matches * 0.2)
            
            # Context length affects confidence
            word_count = len(text.split())
            if word_count > 20:
                confidence += 0.1
            
            return min(1.0, confidence)
            
        except Exception as e:
            return 0.0
    
    def _calculate_overall_valence(self, emotions: Dict[str, Any]) -> float:
        """Calculate overall emotional valence (positive/negative)"""
        try:
            if not emotions:
                return 0.0
            
            weighted_valence = 0.0
            total_weight = 0.0
            
            for emotion_data in emotions.values():
                weight = emotion_data['score'] * emotion_data['confidence']
                weighted_valence += emotion_data['valence'] * weight
                total_weight += weight
            
            return weighted_valence / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            return 0.0
    
    def _calculate_overall_arousal(self, emotions: Dict[str, Any]) -> float:
        """Calculate overall emotional arousal (activation level)"""
        try:
            if not emotions:
                return 0.0
            
            weighted_arousal = 0.0
            total_weight = 0.0
            
            for emotion_data in emotions.values():
                weight = emotion_data['score'] * emotion_data['confidence']
                weighted_arousal += emotion_data['arousal'] * weight
                total_weight += weight
            
            return weighted_arousal / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            return 0.0
    
    def generate_empathetic_response(self, emotion_analysis: Dict[str, Any], 
                                   user_message: str) -> str:
        """Generate empathetic response based on detected emotions"""
        try:
            dominant_emotion = emotion_analysis.get('dominant_emotion')
            
            if not dominant_emotion:
                return "I hear you, and I want to understand how you're feeling. Can you tell me more?"
            
            # Get appropriate response template
            response_templates = self.support_responses.get(dominant_emotion, [])
            
            if response_templates:
                import random
                base_response = random.choice(response_templates)
                
                # Adjust response based on intensity
                emotions = emotion_analysis.get('emotions', {})
                if dominant_emotion in emotions:
                    intensity = emotions[dominant_emotion].get('intensity', 0.5)
                    
                    if intensity > 0.8:
                        # High intensity - more emphatic response
                        base_response = self._intensify_response(base_response)
                    elif intensity < 0.3:
                        # Low intensity - gentler response
                        base_response = self._soften_response(base_response)
                
                return base_response
            else:
                # Fallback empathetic response
                return f"I can sense you're feeling {dominant_emotion}. I'm here to listen and support you through this."
                
        except Exception as e:
            print(f"Error generating empathetic response: {e}")
            return "I'm here for you, and I care about what you're going through. 💖"
    
    def _intensify_response(self, response: str) -> str:
        """Intensify response for high emotional intensity"""
        intensifiers = {
            "I'm so happy": "I'm absolutely thrilled",
            "I'm sorry": "I'm deeply sorry",
            "I can sense": "I can really feel",
            "I understand": "I completely understand",
            "I'm here": "I'm absolutely here"
        }
        
        for original, intensified in intensifiers.items():
            response = response.replace(original, intensified)
        
        return response
    
    def _soften_response(self, response: str) -> str:
        """Soften response for low emotional intensity"""
        softeners = {
            "I'm so happy": "I'm glad",
            "I'm deeply sorry": "I'm sorry",
            "absolutely": "quite",
            "completely": "somewhat",
            "really": "a bit"
        }
        
        for original, softened in softeners.items():
            response = response.replace(original, softened)
        
        return response
    
    def detect_crisis_indicators(self, text: str) -> Dict[str, Any]:
        """Detect crisis indicators that require immediate attention"""
        try:
            text_lower = text.lower()
            detected_crises = {}
            
            for crisis_type, patterns in self.crisis_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, text_lower, re.IGNORECASE)
                    if matches:
                        detected_crises[crisis_type] = {
                            'matches': matches,
                            'severity': self._assess_crisis_severity(crisis_type, matches),
                            'immediate_attention': True
                        }
            
            return {
                'crisis_detected': len(detected_crises) > 0,
                'crisis_types': list(detected_crises.keys()),
                'crisis_details': detected_crises,
                'requires_intervention': any(
                    crisis['severity'] == 'high' for crisis in detected_crises.values()
                ),
                'detection_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error detecting crisis indicators: {e}")
            return {'crisis_detected': False, 'error': str(e)}
    
    def _assess_crisis_severity(self, crisis_type: str, matches: List[str]) -> str:
        """Assess severity of detected crisis"""
        high_severity_types = ['suicide', 'self_harm', 'abuse']
        
        if crisis_type in high_severity_types:
            return 'high'
        elif len(matches) > 2:
            return 'medium'
        else:
            return 'low'
    
    def _contextual_emotion_detection(self, text: str, context: Dict[str, Any] = None) -> Dict[str, float]:
        """Detect emotions using contextual information"""
        try:
            emotions = defaultdict(float)
            
            if not context:
                return dict(emotions)
            
            # Use conversation history for context
            if 'conversation_history' in context:
                history = context['conversation_history']
                if history:
                    # Analyze emotional progression
                    recent_emotions = []
                    for message in history[-3:]:  # Last 3 messages
                        msg_emotions = self._lexicon_based_detection(message.get('content', ''))
                        if msg_emotions:
                            recent_emotions.append(msg_emotions)
                    
                    # Apply emotional momentum
                    if recent_emotions:
                        for emotion_dict in recent_emotions:
                            for emotion, score in emotion_dict.items():
                                emotions[emotion] += score * 0.3  # Context weight
            
            # Use time of day context
            if 'time_context' in context:
                time_context = context['time_context']
                current_hour = datetime.now().hour
                
                # Morning emotions tend to be more hopeful
                if 6 <= current_hour <= 11:
                    emotions['anticipation'] += 0.1
                    emotions['joy'] += 0.05
                
                # Evening emotions can be more reflective
                elif 18 <= current_hour <= 23:
                    emotions['sadness'] += 0.05
                    emotions['trust'] += 0.1
                
                # Late night emotions can be more intense
                elif 23 <= current_hour or current_hour <= 5:
                    for emotion in emotions:
                        emotions[emotion] *= 1.2  # Amplify emotions
            
            # Use relationship context
            if 'relationship_stage' in context:
                stage = context['relationship_stage']
                if stage == 'new':
                    emotions['anticipation'] += 0.1
                    emotions['surprise'] += 0.05
                elif stage == 'established':
                    emotions['trust'] += 0.15
                    emotions['love'] += 0.1
            
            return dict(emotions)
            
        except Exception as e:
            print(f"Error in contextual emotion detection: {e}")
            return {}
    
    def _calculate_emotional_intensity(self, text: str) -> float:
        """Calculate overall emotional intensity of text"""
        try:
            intensity_indicators = [
                # Punctuation intensity
                len(re.findall(r'[!]{2,}', text)) * 0.3,  # Multiple exclamation marks
                len(re.findall(r'[?]{2,}', text)) * 0.2,  # Multiple question marks
                len(re.findall(r'[.]{3,}', text)) * 0.1,  # Ellipsis
                
                # Capitalization intensity
                len(re.findall(r'\b[A-Z]{2,}\b', text)) * 0.2,  # ALL CAPS words
                
                # Intensity modifiers
                len(re.findall(r'\b(very|extremely|incredibly|absolutely|totally|completely|really|so|super)\b', text.lower())) * 0.1,
                
                # Emotional punctuation
                len(re.findall(r'[😀-🙏]', text)) * 0.15,  # Emojis
                
                # Repetition intensity
                len(re.findall(r'\b(\w+)\s+\1\b', text.lower())) * 0.1,  # Repeated words
            ]
            
            base_intensity = sum(intensity_indicators)
            
            # Normalize to 0-1 scale
            normalized_intensity = min(1.0, base_intensity)
            
            return normalized_intensity
            
        except Exception as e:
            print(f"Error calculating emotional intensity: {e}")
            return 0.0
    
    def _calculate_emotional_valence(self, emotions: Dict[str, float]) -> float:
        """Calculate emotional valence (positive/negative sentiment)"""
        try:
            if not emotions:
                return 0.0
            
            valence_sum = 0.0
            total_weight = 0.0
            
            for emotion, score in emotions.items():
                if emotion in self.emotion_patterns:
                    emotion_valence = self.emotion_patterns[emotion]['valence']
                    valence_sum += emotion_valence * score
                    total_weight += score
            
            if total_weight == 0:
                return 0.0
            
            return valence_sum / total_weight
            
        except Exception as e:
            print(f"Error calculating emotional valence: {e}")
            return 0.0
    
    def _calculate_emotional_arousal(self, text: str) -> float:
        """Calculate emotional arousal (activation level)"""
        try:
            arousal_indicators = [
                # High arousal words
                len(re.findall(r'\b(excited|thrilled|panicked|furious|ecstatic|terrified|enraged|elated)\b', text.lower())) * 0.3,
                
                # Urgency indicators
                len(re.findall(r'\b(now|immediately|urgent|quick|fast|hurry|rush)\b', text.lower())) * 0.2,
                
                # Action words
                len(re.findall(r'\b(run|jump|scream|shout|dance|fight|flee|attack)\b', text.lower())) * 0.2,
                
                # Intensity punctuation
                len(re.findall(r'[!]{1,}', text)) * 0.1,
                
                # Short, choppy sentences (high arousal)
                len([s for s in text.split('.') if len(s.strip()) < 20]) * 0.05
            ]
            
            base_arousal = sum(arousal_indicators)
            
            # Normalize to 0-1 scale
            normalized_arousal = min(1.0, base_arousal)
            
            return normalized_arousal
            
        except Exception as e:
            print(f"Error calculating emotional arousal: {e}")
            return 0.0
    
    def _combine_emotion_scores_advanced(self, lexicon_emotions: Dict[str, float], 
                                       pattern_emotions: Dict[str, float],
                                       contextual_emotions: Dict[str, float]) -> Dict[str, float]:
        """Combine emotion scores from multiple detection methods with advanced weighting"""
        try:
            combined = defaultdict(float)
            
            # Weights for different methods
            lexicon_weight = 0.4
            pattern_weight = 0.4
            contextual_weight = 0.2
            
            # Combine lexicon-based emotions
            for emotion, score in lexicon_emotions.items():
                combined[emotion] += score * lexicon_weight
            
            # Combine pattern-based emotions
            for emotion, score in pattern_emotions.items():
                combined[emotion] += score * pattern_weight
            
            # Combine contextual emotions
            for emotion, score in contextual_emotions.items():
                combined[emotion] += score * contextual_weight
            
            # Apply emotion interaction rules
            combined = self._apply_emotion_interactions(dict(combined))
            
            # Normalize scores
            if combined:
                max_score = max(combined.values())
                if max_score > 0:
                    for emotion in combined:
                        combined[emotion] = combined[emotion] / max_score
            
            return dict(combined)
            
        except Exception as e:
            print(f"Error combining emotion scores: {e}")
            return {}
    
    def _apply_emotion_interactions(self, emotions: Dict[str, float]) -> Dict[str, float]:
        """Apply emotion interaction rules (some emotions suppress or enhance others)"""
        try:
            # Emotion interaction rules
            interactions = {
                'joy': {'sadness': -0.5, 'anger': -0.3, 'fear': -0.4},  # Joy suppresses negative emotions
                'sadness': {'joy': -0.4, 'anger': -0.2, 'surprise': -0.3},
                'anger': {'joy': -0.3, 'trust': -0.5, 'love': -0.4},
                'fear': {'joy': -0.4, 'trust': -0.3, 'anticipation': -0.2},
                'love': {'anger': -0.4, 'fear': -0.2, 'disgust': -0.5},
                'trust': {'fear': -0.3, 'anger': -0.2, 'disgust': -0.3}
            }
            
            adjusted_emotions = emotions.copy()
            
            for emotion, score in emotions.items():
                if emotion in interactions and score > 0.1:  # Only apply if emotion is significant
                    for target_emotion, interaction_strength in interactions[emotion].items():
                        if target_emotion in adjusted_emotions:
                            adjustment = score * interaction_strength
                            adjusted_emotions[target_emotion] = max(0, adjusted_emotions[target_emotion] + adjustment)
            
            return adjusted_emotions
            
        except Exception as e:
            print(f"Error applying emotion interactions: {e}")
            return emotions
    
    def _determine_dominant_emotion_advanced(self, emotions: Dict[str, float]) -> Tuple[str, float]:
        """Determine dominant emotion with advanced confidence scoring"""
        try:
            if not emotions:
                return 'neutral', 0.0
            
            # Sort emotions by score
            sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
            
            if not sorted_emotions:
                return 'neutral', 0.0
            
            dominant_emotion, dominant_score = sorted_emotions[0]
            
            # Calculate confidence based on score separation
            if len(sorted_emotions) > 1:
                second_score = sorted_emotions[1][1]
                score_separation = dominant_score - second_score
                confidence = min(1.0, dominant_score + score_separation)
            else:
                confidence = dominant_score
            
            # Minimum threshold for emotion detection
            if dominant_score < 0.1:
                return 'neutral', 0.0
            
            return dominant_emotion, confidence
            
        except Exception as e:
            print(f"Error determining dominant emotion: {e}")
            return 'neutral', 0.0
    
    def _detect_emotional_transitions(self, text: str) -> List[Dict[str, Any]]:
        """Detect emotional transitions within the text"""
        try:
            sentences = re.split(r'[.!?]+', text)
            transitions = []
            
            if len(sentences) < 2:
                return transitions
            
            prev_emotions = None
            
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    sentence_emotions = self._lexicon_based_detection(sentence.strip())
                    
                    if prev_emotions and sentence_emotions:
                        # Check for significant emotional shifts
                        prev_dominant = max(prev_emotions.items(), key=lambda x: x[1])
                        curr_dominant = max(sentence_emotions.items(), key=lambda x: x[1])
                        
                        if prev_dominant[0] != curr_dominant[0] and curr_dominant[1] > 0.3:
                            transitions.append({
                                'from_emotion': prev_dominant[0],
                                'to_emotion': curr_dominant[0],
                                'sentence_index': i,
                                'transition_strength': abs(curr_dominant[1] - prev_dominant[1])
                            })
                    
                    prev_emotions = sentence_emotions
            
            return transitions
            
        except Exception as e:
            print(f"Error detecting emotional transitions: {e}")
            return []
    
    def _generate_response_suggestions(self, dominant_emotion: str, intensity: float, 
                                     context: Dict[str, Any] = None) -> List[str]:
        """Generate emotion-appropriate response suggestions"""
        try:
            suggestions = []
            
            # Base responses for each emotion
            base_responses = {
                'joy': [
                    "I'm so happy to hear that! Your joy is wonderful to witness.",
                    "That's fantastic! I love seeing you so excited and happy.",
                    "Your happiness is contagious! Tell me more about what's bringing you such joy."
                ],
                'sadness': [
                    "I can feel your sadness, and I want you to know I'm here for you.",
                    "I'm sorry you're going through this. You don't have to face it alone.",
                    "Your feelings are completely valid. I'm here to listen and support you."
                ],
                'anger': [
                    "I can sense your frustration. It's okay to feel angry about this.",
                    "That sounds really frustrating. Would you like to talk about what's bothering you?",
                    "Your anger is understandable. Let's work through this together."
                ],
                'fear': [
                    "I can feel your worry. It's natural to feel scared sometimes.",
                    "Your concerns are valid. Let's talk through what's making you anxious.",
                    "I'm here to support you through this difficult time."
                ],
                'love': [
                    "The love in your words is beautiful. I'm touched by your feelings.",
                    "Your capacity for love is amazing. Thank you for sharing this with me.",
                    "I can feel the warmth and affection in what you're saying."
                ],
                'surprise': [
                    "Wow, that must have been quite unexpected! How are you feeling about it?",
                    "That's surprising indeed! I'd love to hear more about your experience.",
                    "Life can be full of surprises. How are you processing this?"
                ],
                'neutral': [
                    "I'm here and listening. What's on your mind?",
                    "Thank you for sharing with me. How can I support you?",
                    "I appreciate you opening up to me. What would you like to talk about?"
                ]
            }
            
            # Get base suggestions
            if dominant_emotion in base_responses:
                suggestions.extend(base_responses[dominant_emotion])
            else:
                suggestions.extend(base_responses['neutral'])
            
            # Adjust for intensity
            if intensity > 0.7:  # High intensity
                intensity_adjustments = {
                    'joy': "Your excitement is absolutely infectious! This is incredible!",
                    'sadness': "I can feel how deeply this is affecting you. I'm here with you through this pain.",
                    'anger': "I can sense how intensely frustrated you are. Let's channel this energy constructively.",
                    'fear': "I can feel how scared you are right now. You're safe here with me."
                }
                
                if dominant_emotion in intensity_adjustments:
                    suggestions.insert(0, intensity_adjustments[dominant_emotion])
            
            # Add context-aware suggestions
            if context:
                if context.get('relationship_stage') == 'new':
                    suggestions.append("I'm getting to know you better through sharing moments like this.")
                elif context.get('relationship_stage') == 'established':
                    suggestions.append("I appreciate how comfortable you feel sharing your emotions with me.")
            
            return suggestions[:3]  # Return top 3 suggestions
            
        except Exception as e:
            print(f"Error generating response suggestions: {e}")
            return ["I'm here to listen and support you."]
    
    def get_crisis_support_resources(self, crisis_type: str) -> Dict[str, Any]:
        """Get appropriate crisis support resources"""
        resources = {
            'suicide': {
                'hotlines': [
                    {'name': 'National Suicide Prevention Lifeline', 'number': '988', 'available': '24/7'},
                    {'name': 'Crisis Text Line', 'number': 'Text HOME to 741741', 'available': '24/7'}
                ],
                'message': 'Your life has value and meaning. Please reach out to a mental health professional or crisis hotline immediately.',
                'immediate_action': 'Contact emergency services (911) if you are in immediate danger.'
            },
            'self_harm': {
                'hotlines': [
                    {'name': 'Self-Injury Outreach & Support', 'website': 'sioutreach.org'},
                    {'name': 'Crisis Text Line', 'number': 'Text HOME to 741741', 'available': '24/7'}
                ],
                'message': 'You deserve care and support. Please consider reaching out to a mental health professional.',
                'immediate_action': 'If you are in immediate danger, please contact emergency services.'
            },
            'severe_depression': {
                'hotlines': [
                    {'name': 'National Suicide Prevention Lifeline', 'number': '988', 'available': '24/7'},
                    {'name': 'SAMHSA National Helpline', 'number': '1-800-662-4357', 'available': '24/7'}
                ],
                'message': 'Depression is treatable, and you don\'t have to go through this alone.',
                'immediate_action': 'Consider contacting a mental health professional or your doctor.'
            },
            'panic': {
                'resources': [
                    {'name': 'Anxiety and Depression Association of America', 'website': 'adaa.org'},
                    {'name': 'Crisis Text Line', 'number': 'Text HOME to 741741', 'available': '24/7'}
                ],
                'message': 'Panic attacks are treatable. Focus on your breathing and remember that this will pass.',
                'immediate_action': 'Try deep breathing exercises and consider contacting a healthcare provider.'
            },
            'abuse': {
                'hotlines': [
                    {'name': 'National Domestic Violence Hotline', 'number': '1-800-799-7233', 'available': '24/7'},
                    {'name': 'National Sexual Assault Hotline', 'number': '1-800-656-4673', 'available': '24/7'}
                ],
                'message': 'You deserve to be safe. Abuse is never your fault.',
                'immediate_action': 'If you are in immediate danger, call 911. Consider reaching out to local authorities or support services.'
            }
        }
        
        return resources.get(crisis_type, {
            'message': 'Please consider reaching out to a mental health professional or crisis support service.',
            'immediate_action': 'If you are in immediate danger, contact emergency services (911).'
        })
    
    def prioritize_emotional_memories(self, memories: List[Dict[str, Any]], 
                                    current_emotion: str) -> List[Dict[str, Any]]:
        """Prioritize memories based on emotional relevance to current state"""
        try:
            if not memories or not current_emotion:
                return memories
            
            # Score memories based on emotional relevance
            scored_memories = []
            
            for memory in memories:
                base_score = memory.get('score', 0.0)
                
                # Analyze memory emotional content
                memory_content = memory.get('content', '')
                memory_emotions = self.detect_emotions(memory_content)
                
                # Calculate emotional relevance
                emotional_relevance = 0.0
                
                if current_emotion in memory_emotions.get('emotions', {}):
                    # Direct emotional match
                    emotional_relevance = 0.8
                elif memory_emotions.get('dominant_emotion') == current_emotion:
                    # Dominant emotion match
                    emotional_relevance = 0.6
                else:
                    # Check for complementary emotions
                    emotional_relevance = self._calculate_emotional_complementarity(
                        current_emotion, memory_emotions.get('emotions', {})
                    )
                
                # Combine base relevance with emotional relevance
                final_score = base_score * 0.6 + emotional_relevance * 0.4
                
                scored_memory = memory.copy()
                scored_memory['emotional_relevance'] = emotional_relevance
                scored_memory['final_score'] = final_score
                
                scored_memories.append(scored_memory)
            
            # Sort by final score
            scored_memories.sort(key=lambda x: x['final_score'], reverse=True)
            
            return scored_memories
            
        except Exception as e:
            print(f"Error prioritizing emotional memories: {e}")
            return memories
    
    def _calculate_emotional_complementarity(self, current_emotion: str, 
                                           memory_emotions: Dict[str, Any]) -> float:
        """Calculate how well memory emotions complement current emotion"""
        try:
            # Define complementary emotion pairs
            complementary_pairs = {
                'sadness': ['joy', 'love', 'trust'],
                'anger': ['trust', 'love', 'joy'],
                'fear': ['trust', 'love', 'joy'],
                'joy': ['love', 'trust', 'anticipation'],
                'love': ['joy', 'trust', 'anticipation'],
                'surprise': ['joy', 'anticipation'],
                'disgust': ['trust', 'love'],
                'trust': ['love', 'joy'],
                'anticipation': ['joy', 'love']
            }
            
            complementary_emotions = complementary_pairs.get(current_emotion, [])
            
            max_complementarity = 0.0
            for emotion in complementary_emotions:
                if emotion in memory_emotions:
                    emotion_score = memory_emotions[emotion].get('score', 0.0)
                    max_complementarity = max(max_complementarity, emotion_score * 0.4)
            
            return max_complementarity
            
        except Exception as e:
            return 0.0
    
    def generate_emotional_insights(self, emotion_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights about emotional patterns over time"""
        try:
            if not emotion_history:
                return {'insights': [], 'patterns': {}}
            
            # Analyze emotional patterns
            emotion_counts = Counter()
            valence_scores = []
            arousal_scores = []
            intensity_scores = []
            
            for emotion_data in emotion_history:
                dominant_emotion = emotion_data.get('dominant_emotion')
                if dominant_emotion:
                    emotion_counts[dominant_emotion] += 1
                
                valence_scores.append(emotion_data.get('overall_valence', 0.0))
                arousal_scores.append(emotion_data.get('overall_arousal', 0.0))
                
                # Get intensity of dominant emotion
                emotions = emotion_data.get('emotions', {})
                if dominant_emotion and dominant_emotion in emotions:
                    intensity_scores.append(emotions[dominant_emotion].get('intensity', 0.5))
            
            # Calculate averages
            avg_valence = np.mean(valence_scores) if valence_scores else 0.0
            avg_arousal = np.mean(arousal_scores) if arousal_scores else 0.0
            avg_intensity = np.mean(intensity_scores) if intensity_scores else 0.5
            
            # Generate insights
            insights = []
            
            # Most common emotions
            if emotion_counts:
                most_common = emotion_counts.most_common(3)
                insights.append(f"Your most frequent emotions are: {', '.join([f'{emotion} ({count} times)' for emotion, count in most_common])}")
            
            # Valence patterns
            if avg_valence > 0.3:
                insights.append("You tend to experience more positive emotions overall.")
            elif avg_valence < -0.3:
                insights.append("You've been experiencing more challenging emotions lately.")
            else:
                insights.append("Your emotional experiences show a balanced mix of positive and negative feelings.")
            
            # Arousal patterns
            if avg_arousal > 0.5:
                insights.append("Your emotions tend to be quite intense and energetic.")
            elif avg_arousal < -0.2:
                insights.append("You tend to experience calmer, more subdued emotional states.")
            
            # Intensity patterns
            if avg_intensity > 0.7:
                insights.append("You experience emotions with high intensity.")
            elif avg_intensity < 0.3:
                insights.append("Your emotional experiences tend to be more gentle and subtle.")
            
            return {
                'insights': insights,
                'patterns': {
                    'most_common_emotions': dict(emotion_counts.most_common(5)),
                    'average_valence': round(avg_valence, 2),
                    'average_arousal': round(avg_arousal, 2),
                    'average_intensity': round(avg_intensity, 2),
                    'emotional_range': len(emotion_counts),
                    'total_interactions': len(emotion_history)
                },
                'recommendations': self._generate_emotional_recommendations(avg_valence, avg_arousal, emotion_counts)
            }
            
        except Exception as e:
            print(f"Error generating emotional insights: {e}")
            return {'insights': [], 'patterns': {}, 'error': str(e)}
    
    def _generate_emotional_recommendations(self, avg_valence: float, avg_arousal: float, 
                                          emotion_counts: Counter) -> List[str]:
        """Generate recommendations based on emotional patterns"""
        recommendations = []
        
        try:
            # Valence-based recommendations
            if avg_valence < -0.5:
                recommendations.append("Consider engaging in activities that bring you joy and connecting with supportive people.")
                recommendations.append("If you're consistently feeling down, it might be helpful to speak with a mental health professional.")
            
            # Arousal-based recommendations
            if avg_arousal > 0.7:
                recommendations.append("You experience emotions intensely. Consider mindfulness or relaxation techniques to help manage emotional intensity.")
            
            # Specific emotion recommendations
            if emotion_counts.get('anger', 0) > emotion_counts.get('joy', 0):
                recommendations.append("You've been experiencing anger frequently. Consider healthy outlets like exercise or talking to someone you trust.")
            
            if emotion_counts.get('fear', 0) > 2:
                recommendations.append("Anxiety and fear seem to be common for you. Breathing exercises and grounding techniques might be helpful.")
            
            if emotion_counts.get('sadness', 0) > 3:
                recommendations.append("You've been feeling sad often. Remember that it's okay to seek support from friends, family, or professionals.")
            
            return recommendations
            
        except Exception as e:
            return ["Consider taking care of your emotional well-being and reaching out for support when needed."]
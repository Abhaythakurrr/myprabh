"""
Unit tests for emotional intelligence service
"""

import pytest
from collections import Counter
from services.memory.emotional_intelligence_service import EmotionalIntelligenceService

class TestEmotionalIntelligenceService:
    """Test cases for EmotionalIntelligenceService"""
    
    def setup_method(self):
        """Set up test environment"""
        self.service = EmotionalIntelligenceService()
    
    def test_detect_emotions_joy(self):
        """Test joy emotion detection"""
        text = "I'm so happy and excited about this wonderful day! It's absolutely amazing!"
        
        result = self.service.detect_emotions(text)
        
        assert 'emotions' in result
        assert 'joy' in result['emotions']
        assert result['dominant_emotion'] == 'joy'
        assert result['emotions']['joy']['score'] > 0.5
        assert result['emotions']['joy']['intensity'] > 0.7  # Should detect high intensity
        assert result['overall_valence'] > 0.5  # Positive valence
    
    def test_detect_emotions_sadness(self):
        """Test sadness emotion detection"""
        text = "I'm feeling really sad and depressed today. Everything seems so hopeless."
        
        result = self.service.detect_emotions(text)
        
        assert 'sadness' in result['emotions']
        assert result['dominant_emotion'] == 'sadness'
        assert result['emotions']['sadness']['score'] > 0.5
        assert result['overall_valence'] < -0.3  # Negative valence
    
    def test_detect_emotions_anger(self):
        """Test anger emotion detection"""
        text = "I'm so angry and frustrated! This is absolutely infuriating and outrageous!"
        
        result = self.service.detect_emotions(text)
        
        assert 'anger' in result['emotions']
        assert result['dominant_emotion'] == 'anger'
        assert result['emotions']['anger']['score'] > 0.5
        assert result['emotions']['anger']['intensity'] > 0.7
        assert result['overall_arousal'] > 0.5  # High arousal
    
    def test_detect_emotions_fear(self):
        """Test fear emotion detection"""
        text = "I'm really scared and worried about what might happen. I'm so anxious."
        
        result = self.service.detect_emotions(text)
        
        assert 'fear' in result['emotions']
        assert result['dominant_emotion'] == 'fear'
        assert result['emotions']['fear']['score'] > 0.5
        assert result['overall_valence'] < 0  # Negative valence
    
    def test_detect_emotions_love(self):
        """Test love emotion detection"""
        text = "I love you so much and cherish every moment we spend together. You mean everything to me."
        
        result = self.service.detect_emotions(text)
        
        assert 'love' in result['emotions']
        assert result['dominant_emotion'] == 'love'
        assert result['emotions']['love']['score'] > 0.5
        assert result['overall_valence'] > 0.5  # Positive valence
    
    def test_detect_emotions_multiple(self):
        """Test detection of multiple emotions"""
        text = "I'm excited but also a bit nervous about this new opportunity. It's amazing but scary."
        
        result = self.service.detect_emotions(text)
        
        # Should detect multiple emotions
        assert len(result['emotions']) > 1
        assert result['emotional_complexity'] > 1
        
        # Should detect both positive and negative emotions
        emotions = result['emotions']
        has_positive = any(emotions[e]['valence'] > 0 for e in emotions)
        has_negative = any(emotions[e]['valence'] < 0 for e in emotions)
        assert has_positive and has_negative
    
    def test_detect_emotions_neutral(self):
        """Test detection with neutral text"""
        text = "I went to the store today and bought some groceries. The weather was okay."
        
        result = self.service.detect_emotions(text)
        
        # Should detect few or no strong emotions
        assert len(result['emotions']) <= 2
        assert abs(result['overall_valence']) < 0.3  # Near neutral
    
    def test_calculate_intensity_high(self):
        """Test intensity calculation with high modifiers"""
        text = "extremely happy and absolutely thrilled"
        modifiers = ['extremely', 'absolutely', 'very', 'really']
        
        intensity = self.service._calculate_intensity(text, modifiers)
        
        assert intensity > 0.8  # Should be high intensity
    
    def test_calculate_intensity_low(self):
        """Test intensity calculation with low modifiers"""
        text = "somewhat happy and quite pleased"
        modifiers = ['somewhat', 'quite', 'pretty']
        
        intensity = self.service._calculate_intensity(text, modifiers)
        
        assert intensity < 0.8  # Should be lower intensity
    
    def test_generate_empathetic_response_joy(self):
        """Test empathetic response generation for joy"""
        emotion_analysis = {
            'dominant_emotion': 'joy',
            'emotions': {
                'joy': {'intensity': 0.8, 'confidence': 0.9}
            }
        }
        
        response = self.service.generate_empathetic_response(emotion_analysis, "I'm so happy!")
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Should contain positive, supportive language
        assert any(word in response.lower() for word in ['happy', 'joy', 'wonderful', 'thrilled', 'love'])
    
    def test_generate_empathetic_response_sadness(self):
        """Test empathetic response generation for sadness"""
        emotion_analysis = {
            'dominant_emotion': 'sadness',
            'emotions': {
                'sadness': {'intensity': 0.7, 'confidence': 0.8}
            }
        }
        
        response = self.service.generate_empathetic_response(emotion_analysis, "I'm feeling sad")
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Should contain supportive, caring language
        assert any(word in response.lower() for word in ['sorry', 'here', 'support', 'understand', 'care'])
    
    def test_generate_empathetic_response_no_emotion(self):
        """Test empathetic response generation with no detected emotion"""
        emotion_analysis = {'dominant_emotion': None, 'emotions': {}}
        
        response = self.service.generate_empathetic_response(emotion_analysis, "Just saying hello")
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Should be a general supportive response
        assert any(word in response.lower() for word in ['hear', 'understand', 'feel'])
    
    def test_intensify_response(self):
        """Test response intensification"""
        original = "I'm so happy to hear that!"
        
        intensified = self.service._intensify_response(original)
        
        # Should be more intense
        assert 'absolutely' in intensified or 'thrilled' in intensified
        assert intensified != original
    
    def test_soften_response(self):
        """Test response softening"""
        original = "I'm absolutely thrilled and completely understand!"
        
        softened = self.service._soften_response(original)
        
        # Should be softer
        assert 'absolutely' not in softened or 'completely' not in softened
        assert softened != original
    
    def test_detect_crisis_indicators_suicide(self):
        """Test crisis detection for suicide indicators"""
        text = "I don't want to live anymore and I'm thinking about ending it all."
        
        result = self.service.detect_crisis_indicators(text)
        
        assert result['crisis_detected'] is True
        assert 'suicide' in result['crisis_types']
        assert result['requires_intervention'] is True
        assert result['crisis_details']['suicide']['severity'] == 'high'
    
    def test_detect_crisis_indicators_self_harm(self):
        """Test crisis detection for self-harm indicators"""
        text = "I want to hurt myself and I've been thinking about cutting."
        
        result = self.service.detect_crisis_indicators(text)
        
        assert result['crisis_detected'] is True
        assert 'self_harm' in result['crisis_types']
        assert result['requires_intervention'] is True
    
    def test_detect_crisis_indicators_panic(self):
        """Test crisis detection for panic indicators"""
        text = "I'm having a panic attack and I can't breathe. My heart is racing."
        
        result = self.service.detect_crisis_indicators(text)
        
        assert result['crisis_detected'] is True
        assert 'panic' in result['crisis_types']
        # Panic is typically medium severity
        assert result['crisis_details']['panic']['severity'] in ['medium', 'low']
    
    def test_detect_crisis_indicators_none(self):
        """Test crisis detection with no crisis indicators"""
        text = "I had a good day today and enjoyed spending time with friends."
        
        result = self.service.detect_crisis_indicators(text)
        
        assert result['crisis_detected'] is False
        assert len(result['crisis_types']) == 0
        assert result['requires_intervention'] is False
    
    def test_get_crisis_support_resources_suicide(self):
        """Test getting crisis support resources for suicide"""
        resources = self.service.get_crisis_support_resources('suicide')
        
        assert 'hotlines' in resources
        assert 'message' in resources
        assert 'immediate_action' in resources
        assert len(resources['hotlines']) > 0
        assert '988' in str(resources['hotlines'])  # National Suicide Prevention Lifeline
    
    def test_get_crisis_support_resources_unknown(self):
        """Test getting crisis support resources for unknown crisis type"""
        resources = self.service.get_crisis_support_resources('unknown_crisis')
        
        assert 'message' in resources
        assert 'immediate_action' in resources
        # Should provide general support information
        assert 'mental health professional' in resources['message']
    
    def test_prioritize_emotional_memories(self):
        """Test emotional memory prioritization"""
        memories = [
            {
                'content': 'I was so happy and excited that day!',
                'score': 0.7,
                'metadata': {}
            },
            {
                'content': 'It was a regular day, nothing special happened.',
                'score': 0.8,
                'metadata': {}
            },
            {
                'content': 'I felt such joy and happiness during that moment.',
                'score': 0.6,
                'metadata': {}
            }
        ]
        
        current_emotion = 'joy'
        
        result = self.service.prioritize_emotional_memories(memories, current_emotion)
        
        # Should prioritize emotionally relevant memories
        assert len(result) == 3
        # First memory should have high emotional relevance due to joy content
        assert result[0]['emotional_relevance'] > result[1]['emotional_relevance']
    
    def test_prioritize_emotional_memories_no_emotion(self):
        """Test emotional memory prioritization with no current emotion"""
        memories = [{'content': 'Test memory', 'score': 0.7}]
        
        result = self.service.prioritize_emotional_memories(memories, None)
        
        # Should return original memories unchanged
        assert result == memories
    
    def test_generate_emotional_insights(self):
        """Test emotional insights generation"""
        emotion_history = [
            {
                'dominant_emotion': 'joy',
                'overall_valence': 0.8,
                'overall_arousal': 0.6,
                'emotions': {'joy': {'intensity': 0.7}}
            },
            {
                'dominant_emotion': 'joy',
                'overall_valence': 0.7,
                'overall_arousal': 0.5,
                'emotions': {'joy': {'intensity': 0.6}}
            },
            {
                'dominant_emotion': 'sadness',
                'overall_valence': -0.6,
                'overall_arousal': 0.3,
                'emotions': {'sadness': {'intensity': 0.8}}
            }
        ]
        
        result = self.service.generate_emotional_insights(emotion_history)
        
        assert 'insights' in result
        assert 'patterns' in result
        assert 'recommendations' in result
        
        # Should identify joy as most common
        assert result['patterns']['most_common_emotions']['joy'] == 2
        assert result['patterns']['most_common_emotions']['sadness'] == 1
        
        # Should have positive average valence
        assert result['patterns']['average_valence'] > 0
        
        # Should have insights about emotional patterns
        assert len(result['insights']) > 0
    
    def test_generate_emotional_insights_empty(self):
        """Test emotional insights generation with empty history"""
        result = self.service.generate_emotional_insights([])
        
        assert result['insights'] == []
        assert result['patterns'] == {}
    
    def test_calculate_overall_valence_mixed(self):
        """Test overall valence calculation with mixed emotions"""
        emotions = {
            'joy': {'score': 0.8, 'confidence': 0.9, 'valence': 1.0},
            'sadness': {'score': 0.6, 'confidence': 0.7, 'valence': -1.0}
        }
        
        valence = self.service._calculate_overall_valence(emotions)
        
        # Should be positive but not extremely positive due to mixed emotions
        assert -1.0 <= valence <= 1.0
        # Joy has higher score and confidence, so should lean positive
        assert valence > 0
    
    def test_calculate_overall_arousal_high(self):
        """Test overall arousal calculation with high-arousal emotions"""
        emotions = {
            'anger': {'score': 0.8, 'confidence': 0.9, 'arousal': 0.9},
            'excitement': {'score': 0.6, 'confidence': 0.7, 'arousal': 0.8}
        }
        
        arousal = self.service._calculate_overall_arousal(emotions)
        
        # Should be high arousal
        assert arousal > 0.7
    
    def test_emotion_score_calculation(self):
        """Test emotion score calculation"""
        text = "happy joy excited wonderful amazing"
        config = {
            'keywords': ['happy', 'joy', 'excited'],
            'patterns': [r'\b(wonderful|amazing)\b']
        }
        
        score = self.service._calculate_emotion_score(text, config)
        
        # Should detect multiple keywords and patterns
        assert score > 0.3
        assert score <= 1.0

if __name__ == "__main__":
    pytest.main([__file__])  
  
    def test_detect_emotions_advanced(self):
        """Test advanced emotion detection with context"""
        # Arrange
        text = "I'm so incredibly excited about this amazing opportunity!"
        context = {
            'conversation_history': [
                {'content': 'I got the job!'},
                {'content': 'This is the best day ever!'}
            ],
            'time_context': True,
            'relationship_stage': 'established'
        }
        
        # Act
        result = self.service.detect_emotions_advanced(text, context)
        
        # Assert
        self.assertIn('emotions', result)
        self.assertIn('dominant_emotion', result)
        self.assertIn('confidence', result)
        self.assertIn('emotional_intensity', result)
        self.assertIn('emotional_valence', result)
        self.assertIn('emotional_arousal', result)
        self.assertIn('emotional_transitions', result)
        self.assertIn('response_suggestions', result)
        self.assertEqual(result['analysis_method'], 'advanced_hybrid')
        self.assertTrue(result['context_used'])
        
        # Should detect joy with high intensity
        self.assertEqual(result['dominant_emotion'], 'joy')
        self.assertGreater(result['emotional_intensity'], 0.5)
        self.assertGreater(result['emotional_valence'], 0.5)
    
    def test_calculate_emotional_intensity(self):
        """Test emotional intensity calculation"""
        # Test high intensity text
        high_intensity_text = "I'm EXTREMELY excited!!! This is AMAZING!!!"
        intensity = self.service._calculate_emotional_intensity(high_intensity_text)
        self.assertGreater(intensity, 0.5)
        
        # Test low intensity text
        low_intensity_text = "I'm okay."
        intensity = self.service._calculate_emotional_intensity(low_intensity_text)
        self.assertLess(intensity, 0.3)
    
    def test_calculate_emotional_valence(self):
        """Test emotional valence calculation"""
        # Test positive emotions
        positive_emotions = {'joy': 0.8, 'love': 0.6}
        valence = self.service._calculate_emotional_valence(positive_emotions)
        self.assertGreater(valence, 0)
        
        # Test negative emotions
        negative_emotions = {'sadness': 0.7, 'anger': 0.5}
        valence = self.service._calculate_emotional_valence(negative_emotions)
        self.assertLess(valence, 0)
    
    def test_calculate_emotional_arousal(self):
        """Test emotional arousal calculation"""
        # Test high arousal text
        high_arousal_text = "I'm so excited I could scream! This is urgent!"
        arousal = self.service._calculate_emotional_arousal(high_arousal_text)
        self.assertGreater(arousal, 0.3)
        
        # Test low arousal text
        low_arousal_text = "I feel calm and peaceful."
        arousal = self.service._calculate_emotional_arousal(low_arousal_text)
        self.assertLess(arousal, 0.5)
    
    def test_contextual_emotion_detection(self):
        """Test contextual emotion detection"""
        text = "I'm feeling good today"
        
        # Test with conversation history context
        context = {
            'conversation_history': [
                {'content': 'I was so sad yesterday'},
                {'content': 'But things are looking up'}
            ]
        }
        
        emotions = self.service._contextual_emotion_detection(text, context)
        self.assertIsInstance(emotions, dict)
        
        # Test with time context
        context = {'time_context': True}
        emotions = self.service._contextual_emotion_detection(text, context)
        self.assertIsInstance(emotions, dict)
    
    def test_detect_emotional_transitions(self):
        """Test emotional transition detection"""
        # Text with clear emotional transition
        text = "I was so sad about losing my job. But then I got a call with an amazing offer! I'm thrilled now!"
        
        transitions = self.service._detect_emotional_transitions(text)
        
        self.assertIsInstance(transitions, list)
        if transitions:  # If transitions are detected
            transition = transitions[0]
            self.assertIn('from_emotion', transition)
            self.assertIn('to_emotion', transition)
            self.assertIn('sentence_index', transition)
            self.assertIn('transition_strength', transition)
    
    def test_generate_response_suggestions(self):
        """Test response suggestion generation"""
        # Test joy response suggestions
        suggestions = self.service._generate_response_suggestions('joy', 0.8)
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        self.assertLessEqual(len(suggestions), 3)
        
        # Test sadness response suggestions
        suggestions = self.service._generate_response_suggestions('sadness', 0.6)
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        
        # Test with context
        context = {'relationship_stage': 'new'}
        suggestions = self.service._generate_response_suggestions('joy', 0.5, context)
        self.assertIsInstance(suggestions, list)
    
    def test_apply_emotion_interactions(self):
        """Test emotion interaction rules"""
        # Test joy suppressing sadness
        emotions = {'joy': 0.8, 'sadness': 0.6, 'anger': 0.3}
        adjusted = self.service._apply_emotion_interactions(emotions)
        
        self.assertIsInstance(adjusted, dict)
        self.assertIn('joy', adjusted)
        self.assertIn('sadness', adjusted)
        
        # Joy should suppress sadness
        self.assertLess(adjusted['sadness'], emotions['sadness'])
    
    def test_determine_dominant_emotion_advanced(self):
        """Test advanced dominant emotion determination"""
        # Test clear dominant emotion
        emotions = {'joy': 0.8, 'sadness': 0.2, 'anger': 0.1}
        dominant, confidence = self.service._determine_dominant_emotion_advanced(emotions)
        
        self.assertEqual(dominant, 'joy')
        self.assertGreater(confidence, 0.5)
        
        # Test close emotions
        emotions = {'joy': 0.5, 'sadness': 0.48, 'anger': 0.1}
        dominant, confidence = self.service._determine_dominant_emotion_advanced(emotions)
        
        self.assertEqual(dominant, 'joy')
        self.assertLess(confidence, 0.8)  # Lower confidence due to close scores
        
        # Test low scores (should return neutral)
        emotions = {'joy': 0.05, 'sadness': 0.03}
        dominant, confidence = self.service._determine_dominant_emotion_advanced(emotions)
        
        self.assertEqual(dominant, 'neutral')
        self.assertEqual(confidence, 0.0)

if __name__ == '__main__':
    unittest.main()
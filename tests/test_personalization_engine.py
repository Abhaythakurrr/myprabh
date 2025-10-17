"""
Unit tests for personalization engine
"""

import pytest
from datetime import datetime
from services.memory.personalization_engine import PersonalizationEngine
from services.memory.memory_models import PersonalizationProfile

class TestPersonalizationEngine:
    """Test cases for PersonalizationEngine"""
    
    def setup_method(self):
        """Set up test environment"""
        self.engine = PersonalizationEngine()
        self.test_user_id = "test_user_123"
        self.test_companion_id = "test_companion_456"
    
    def test_analyze_personality_empty_memories(self):
        """Test personality analysis with empty memories"""
        memories = []
        
        result = self.engine.analyze_personality(memories)
        
        # Should return default personality
        assert 'personality_traits' in result
        assert 'communication_style' in result
        assert 'emotional_patterns' in result
        assert result['confidence_score'] == 0.1
        assert result['memory_count'] == 0
    
    def test_analyze_personality_insufficient_data(self):
        """Test personality analysis with insufficient data"""
        memories = ["Short text."]
        
        result = self.engine.analyze_personality(memories)
        
        # Should return default personality due to insufficient data
        assert result['confidence_score'] == 0.1
        assert result['word_count'] < 50
    
    def test_analyze_personality_creative_content(self):
        """Test personality analysis with creative content"""
        memories = [
            "I love exploring new places and trying different cuisines. Yesterday I discovered this amazing art gallery.",
            "I'm always curious about how things work and enjoy creating new projects in my spare time.",
            "I find myself drawn to unique experiences and innovative ideas that challenge conventional thinking."
        ]
        
        result = self.engine.analyze_personality(memories)
        
        # Should detect high openness
        assert result['personality_traits']['openness'] > 0.5
        assert result['confidence_score'] > 0.1
        assert result['memory_count'] == 3
        assert 'creative' in result['personality_summary'].lower() or 'open' in result['personality_summary'].lower()
    
    def test_analyze_personality_social_content(self):
        """Test personality analysis with social content"""
        memories = [
            "Had an amazing party last night with all my friends! We talked and laughed until late.",
            "I love meeting new people and sharing stories. Social gatherings energize me so much.",
            "Planning another get-together this weekend. Can't wait to see everyone again!"
        ]
        
        result = self.engine.analyze_personality(memories)
        
        # Should detect high extraversion
        assert result['personality_traits']['extraversion'] > 0.5
        assert result['communication_style']['casual'] > 0.3
        assert 'social' in result['personality_summary'].lower() or 'outgoing' in result['personality_summary'].lower()
    
    def test_analyze_personality_organized_content(self):
        """Test personality analysis with organized content"""
        memories = [
            "I always plan my week ahead and set clear goals for each day.",
            "Finished all my tasks on schedule today. Organization really helps me achieve my targets.",
            "I believe in being thorough and responsible in everything I do. Preparation is key to success."
        ]
        
        result = self.engine.analyze_personality(memories)
        
        # Should detect high conscientiousness
        assert result['personality_traits']['conscientiousness'] > 0.5
        assert 'organized' in result['personality_summary'].lower() or 'goal' in result['personality_summary'].lower()
    
    def test_analyze_personality_caring_content(self):
        """Test personality analysis with caring content"""
        memories = [
            "I always try to help my friends when they're going through difficult times.",
            "It's important to be kind and understanding. I care deeply about the people in my life.",
            "I love supporting others and making sure everyone feels included and valued."
        ]
        
        result = self.engine.analyze_personality(memories)
        
        # Should detect high agreeableness
        assert result['personality_traits']['agreeableness'] > 0.5
        assert result['emotional_patterns']['empathy'] > 0.4
        assert 'kind' in result['personality_summary'].lower() or 'cooperative' in result['personality_summary'].lower()
    
    def test_analyze_personality_anxious_content(self):
        """Test personality analysis with anxious content"""
        memories = [
            "I've been feeling really worried about the upcoming presentation. I'm so nervous.",
            "Sometimes I get stressed about things that might go wrong. It's hard to relax.",
            "I tend to overthink situations and feel anxious about uncertain outcomes."
        ]
        
        result = self.engine.analyze_personality(memories)
        
        # Should detect higher neuroticism
        assert result['personality_traits']['neuroticism'] > 0.4
        assert 'sensitive' in result['personality_summary'].lower() or 'emotional' in result['personality_summary'].lower()
    
    def test_communication_style_detection_formal(self):
        """Test detection of formal communication style"""
        memories = [
            "I would respectfully like to thank you for your assistance. Please let me know if you need anything.",
            "Could you please help me with this matter? I would be most grateful for your support.",
            "Thank you very much for your time and consideration. I sincerely appreciate your help."
        ]
        
        result = self.engine.analyze_personality(memories)
        
        # Should detect formal communication style
        assert result['communication_style']['formal'] > 0.3
    
    def test_communication_style_detection_casual(self):
        """Test detection of casual communication style"""
        memories = [
            "Hey, that was awesome! Yeah, I'm totally gonna do that again.",
            "Cool stuff happening today. It's gonna be great fun with everyone.",
            "Haha, that's so funny! I love hanging out and having a good time."
        ]
        
        result = self.engine.analyze_personality(memories)
        
        # Should detect casual communication style
        assert result['communication_style']['casual'] > 0.4
    
    def test_emotional_patterns_optimism(self):
        """Test detection of optimistic emotional patterns"""
        memories = [
            "What a wonderful day! Everything is going great and I feel so positive about the future.",
            "I love how bright and amazing life can be. There's so much good in the world.",
            "Feeling fantastic about all the wonderful opportunities ahead!"
        ]
        
        result = self.engine.analyze_personality(memories)
        
        # Should detect optimism
        assert result['emotional_patterns']['optimism'] > 0.4
        assert result['emotional_patterns']['pessimism'] < 0.3
    
    def test_emotional_patterns_humor(self):
        """Test detection of humor in emotional patterns"""
        memories = [
            "That joke was hilarious! I couldn't stop laughing for minutes.",
            "I love funny stories and comedy shows. Humor makes everything better.",
            "We were all giggling and having such an amusing time together."
        ]
        
        result = self.engine.analyze_personality(memories)
        
        # Should detect humor appreciation
        assert result['emotional_patterns']['humor'] > 0.3
    
    def test_create_persona_prompt_default(self):
        """Test creating persona prompt with default personality"""
        # Mock get_personality_profile to return None
        prompt = self.engine.create_persona_prompt(self.test_user_id, self.test_companion_id)
        
        # Should return default persona prompt
        assert "caring and empathetic AI companion" in prompt
        assert "Behavioral Guidelines" in prompt
        assert "Memory Integration" in prompt
    
    def test_trait_to_description(self):
        """Test personality trait to description conversion"""
        assert "creative" in self.engine._trait_to_description('openness')
        assert "organized" in self.engine._trait_to_description('conscientiousness')
        assert "social" in self.engine._trait_to_description('extraversion')
        assert "kind" in self.engine._trait_to_description('agreeableness')
        assert "sensitive" in self.engine._trait_to_description('neuroticism')
    
    def test_calculate_confidence_score(self):
        """Test confidence score calculation"""
        # Low data should give low confidence
        low_confidence = self.engine._calculate_confidence_score(50, 2)
        assert low_confidence < 0.3
        
        # High data should give high confidence
        high_confidence = self.engine._calculate_confidence_score(1500, 25)
        assert high_confidence > 0.8
        
        # Medium data should give medium confidence
        medium_confidence = self.engine._calculate_confidence_score(500, 10)
        assert 0.3 < medium_confidence < 0.8
    
    def test_generate_personality_insights(self):
        """Test generating personality insights"""
        personality_analysis = {
            'personality_traits': {
                'openness': 0.8,
                'conscientiousness': 0.3,
                'extraversion': 0.7,
                'agreeableness': 0.6,
                'neuroticism': 0.2
            },
            'communication_style': {
                'casual': 0.7,
                'formal': 0.2,
                'emotional': 0.5
            },
            'emotional_patterns': {
                'optimism': 0.8,
                'empathy': 0.7,
                'humor': 0.4
            }
        }
        
        insights = self.engine.generate_personality_insights(personality_analysis)
        
        # Should generate insights for high traits
        assert len(insights) > 0
        assert any('creative' in insight.lower() or 'open' in insight.lower() for insight in insights)
        assert any('social' in insight.lower() or 'energetic' in insight.lower() for insight in insights)
    
    def test_calculate_compatibility_score(self):
        """Test compatibility score calculation"""
        profile1 = {
            'personality_traits': {
                'openness': 0.8,
                'conscientiousness': 0.6,
                'extraversion': 0.7,
                'agreeableness': 0.8,
                'neuroticism': 0.3
            }
        }
        
        # Similar profile should have high compatibility
        profile2_similar = {
            'personality_traits': {
                'openness': 0.7,
                'conscientiousness': 0.6,
                'extraversion': 0.8,
                'agreeableness': 0.7,
                'neuroticism': 0.4
            }
        }
        
        # Very different profile should have lower compatibility
        profile2_different = {
            'personality_traits': {
                'openness': 0.2,
                'conscientiousness': 0.2,
                'extraversion': 0.1,
                'agreeableness': 0.3,
                'neuroticism': 0.9
            }
        }
        
        similar_score = self.engine.calculate_compatibility_score(profile1, profile2_similar)
        different_score = self.engine.calculate_compatibility_score(profile1, profile2_different)
        
        # Similar profiles should have higher compatibility
        assert similar_score > different_score
        assert similar_score > 0.7
        assert different_score < 0.5
    
    def test_calculate_compatibility_score_empty_profiles(self):
        """Test compatibility score with empty profiles"""
        empty_profile = {}
        normal_profile = {'personality_traits': {'openness': 0.5}}
        
        score = self.engine.calculate_compatibility_score(empty_profile, normal_profile)
        
        # Should return neutral score
        assert score == 0.5
    
    def test_get_personalization_level(self):
        """Test getting personalization level"""
        level = self.engine.get_personalization_level(self.test_user_id)
        
        # Should return basic level (default implementation)
        assert level == "basic"
    
    def test_update_personality_profile(self):
        """Test updating personality profile with interactions"""
        interactions = [
            {
                'user_message': 'I love trying new creative projects and exploring different art forms.',
                'ai_response': 'That sounds wonderful!'
            },
            {
                'user_message': 'I always plan my activities carefully and set clear goals.',
                'ai_response': 'Organization is really helpful!'
            }
        ]
        
        result = self.engine.update_personality_profile(
            self.test_user_id, 
            self.test_companion_id, 
            interactions
        )
        
        # Should return updated profile data
        assert 'personality_traits' in result
        assert 'communication_style' in result
        assert 'emotional_patterns' in result
    
    def test_styles_to_description(self):
        """Test communication styles to description conversion"""
        # Single style
        single_desc = self.engine._styles_to_description(['casual'])
        assert 'casual' in single_desc.lower()
        assert single_desc.endswith('.')
        
        # Multiple styles
        multi_desc = self.engine._styles_to_description(['casual', 'emotional'])
        assert 'casual' in multi_desc.lower()
        assert 'emotional' in multi_desc.lower()
        assert ' and ' in multi_desc
    
    def test_emotional_patterns_to_description(self):
        """Test emotional patterns to description conversion"""
        emotional_patterns = {
            'optimism': 0.7,
            'empathy': 0.8,
            'humor': 0.6,
            'intensity': 0.3
        }
        
        description = self.engine._emotional_patterns_to_description(emotional_patterns)
        
        assert 'optimistic' in description.lower()
        assert 'empathetic' in description.lower()
        assert 'humor' in description.lower()
        # intensity should not be included (score too low)
        assert 'intensely' not in description.lower()

if __name__ == "__main__":
    pytest.main([__file__])
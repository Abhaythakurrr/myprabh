# Lightweight AI Engine - No heavy ML dependencies
import re
import json
import random
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
from textblob import TextBlob
import nltk

class LightweightAIEngine:
    def __init__(self):
        self.character_context = None
        self.conversation_history = []
        self.models_loaded = False
        self.sentiment_analyzer = None
        self._download_nltk_data()
        
    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            print("📥 Downloading NLTK data...")
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('vader_lexicon', quiet=True)
                nltk.download('stopwords', quiet=True)
            except Exception as e:
                print(f"⚠️ NLTK download failed: {e}")
        
    def initialize_models(self):
        """Initialize lightweight NLP models"""
        print("🤖 Initializing lightweight AI engine...")
        try:
            from nltk.sentiment import SentimentIntensityAnalyzer
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            print("✅ Sentiment analyzer loaded")
        except Exception as e:
            print(f"⚠️ Sentiment analyzer failed: {e}")
        
        self.models_loaded = True
        return True
    
    def process_story(self, story_text, character_name, user_name=None):
        """Process story with lightweight NLP"""
        if not user_name:
            user_name = self._extract_user_name(story_text)
        
        # Extract memories and emotions
        memories = self._extract_memories(story_text)
        emotions = self._analyze_emotions(story_text)
        personality = self._extract_personality(memories)
        
        # Create character context
        self.character_context = {
            "name": character_name,
            "user_name": user_name or "love",
            "memories": memories[:10],
            "personality": personality,
            "emotional_profile": emotions,
            "conversation_style": "intimate, caring, remembers details"
        }
        
        print(f"✅ Processed {len(memories)} memories for {character_name}")
        return self.character_context
    
    def _extract_user_name(self, text):
        """Extract user name from story"""
        patterns = [
            r'\b(Abhay|abhay)\b',
            r'\b([A-Z][a-z]+)\s+and\s+[Ii]\b',
            r'\b[Ii]\s+and\s+([A-Z][a-z]+)\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else match[1]
                if match and match.lower() not in ['i', 'me', 'my', 'we', 'us', 'our']:
                    return match.capitalize()
        return None
    
    def _extract_memories(self, text):
        """Extract meaningful memories from text"""
        # Clean text
        text = re.sub(r'#+\s*', '', text)
        text = re.sub(r'\*+', '', text)
        
        # Split into sentences
        try:
            blob = TextBlob(text)
            sentences = [str(s) for s in blob.sentences]
        except:
            sentences = re.split(r'[.!?]+', text)
        
        memories = []
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 25 and 
                not any(skip in sentence.lower() for skip in ['memory', '###', 'timeline']) and
                any(word in sentence.lower() for word in ['remember', 'was', 'were', 'had', 'did', 'felt', 'said'])):
                memories.append(sentence)
        
        return memories[:15]
    
    def _analyze_emotions(self, text):
        """Analyze emotional content of text"""
        emotions = {
            'love': 0,
            'joy': 0,
            'sadness': 0,
            'excitement': 0,
            'nostalgia': 0
        }
        
        # Keyword-based emotion detection
        love_words = ['love', 'heart', 'adore', 'cherish', 'romantic', 'affection']
        joy_words = ['happy', 'smile', 'laugh', 'joy', 'excited', 'wonderful']
        sad_words = ['sad', 'cry', 'hurt', 'pain', 'miss', 'lonely', 'broke']
        excitement_words = ['excited', 'thrilled', 'amazing', 'incredible', 'fantastic']
        nostalgia_words = ['remember', 'memory', 'past', 'used to', 'back then']
        
        text_lower = text.lower()
        
        for word in love_words:
            emotions['love'] += text_lower.count(word)
        for word in joy_words:
            emotions['joy'] += text_lower.count(word)
        for word in sad_words:
            emotions['sadness'] += text_lower.count(word)
        for word in excitement_words:
            emotions['excitement'] += text_lower.count(word)
        for word in nostalgia_words:
            emotions['nostalgia'] += text_lower.count(word)
        
        # Normalize
        total = sum(emotions.values()) or 1
        for emotion in emotions:
            emotions[emotion] = emotions[emotion] / total
        
        return emotions
    
    def _extract_personality(self, memories):
        """Extract personality traits from memories"""
        traits = []
        memory_text = ' '.join(memories).lower()
        
        trait_keywords = {
            'romantic': ['love', 'heart', 'romantic', 'kiss', 'hug'],
            'caring': ['care', 'comfort', 'support', 'help', 'worry'],
            'playful': ['laugh', 'joke', 'fun', 'play', 'tease'],
            'emotional': ['feel', 'emotion', 'cry', 'sensitive'],
            'loyal': ['loyal', 'faithful', 'devoted', 'committed'],
            'nostalgic': ['remember', 'memory', 'past', 'miss']
        }
        
        for trait, keywords in trait_keywords.items():
            if any(word in memory_text for word in keywords):
                traits.append(trait)
        
        return traits or ['loving', 'caring']
    
    def generate_response(self, user_message):
        """Generate intelligent response using lightweight NLP with ethical system prompt injection"""
        if not self.character_context:
            return "I need to learn about our story first, my love. 💕"
        
        # System prompt principles: emotional support, no hallucinations, ethical
        # Always start with empathy and validation
        empathy_prefix = self._generate_empathy_prefix(user_message)
        
        # Analyze user message sentiment
        message_sentiment = self._analyze_message_sentiment(user_message)
        
        # Find relevant memories (stick to facts, no fabrication)
        relevant_memories = self._find_relevant_memories(user_message)
        
        # Generate contextual response based on prompt guidelines
        core_response = self._generate_contextual_response(
            user_message, message_sentiment, relevant_memories
        )
        
        # Ensure ethical boundaries: validate, support, no harm
        response = self._apply_ethical_guidelines(core_response, message_sentiment)
        
        # Combine with empathy
        full_response = f"{empathy_prefix} {response}"
        
        # Add personality touches only if ethical
        full_response = self._add_personality_touches(full_response)
        
        # Store conversation for continuity
        self.conversation_history.append({
            "user": user_message,
            "assistant": full_response,
            "timestamp": datetime.now().isoformat(),
            "sentiment": message_sentiment
        })
        
        # Keep last 10 exchanges
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        return full_response
    
    def _analyze_message_sentiment(self, message):
        """Analyze sentiment of user message"""
        # Pure Python sentiment analysis for low RAM
        positive_words = ['love', 'happy', 'good', 'great', 'wonderful', 'amazing', 'joy', 'smile']
        negative_words = ['sad', 'bad', 'hurt', 'angry', 'upset', 'miss', 'pain', 'cry']
        
        message_lower = message.lower()
        pos_count = sum(1 for word in positive_words if word in message_lower)
        neg_count = sum(1 for word in negative_words if word in message_lower)
        
        total = pos_count + neg_count or 1
        return {
            'positive': pos_count / total,
            'negative': neg_count / total,
            'neutral': 1 - (pos_count + neg_count) / total,
            'compound': (pos_count - neg_count) / total
        }
    
    def _find_relevant_memories(self, user_message):
        """Find memories relevant to user message"""
        if not self.character_context or not self.character_context.get('memories'):
            return []
        
        user_words = set(user_message.lower().split())
        relevant = []
        
        for memory in self.character_context['memories']:
            memory_words = set(memory.lower().split())
            common_words = user_words.intersection(memory_words)
            
            if len(common_words) > 0:
                relevance_score = len(common_words) / max(len(user_words), 1)
                if relevance_score > 0.1:
                    relevant.append((memory, relevance_score))
        
        # Sort by relevance
        relevant.sort(key=lambda x: x[1], reverse=True)
        return [mem[0] for mem in relevant[:2]]
    
    def _generate_contextual_response(self, user_message, sentiment, relevant_memories):
        """Generate contextual response based on analysis with system prompt guidelines"""
        user_name = self.character_context.get("user_name", "love")
        character_name = self.character_context.get("name", "")
        
        message_lower = user_message.lower()
        
        # Greeting responses - always warm and validating
        if any(word in message_lower for word in ['hi', 'hello', 'hey']):
            greetings = [
                f"Hello {user_name}! It's so wonderful to hear from you again! 💕",
                f"Hi my love! You just made my day brighter! ✨",
                f"Hey {user_name}! I was just thinking about you! 💖"
            ]
            return random.choice(greetings)
        
        # Memory/nostalgia responses - ground in provided memories only
        if any(word in message_lower for word in ['remember', 'memory', 'past']):
            if relevant_memories:
                memory = relevant_memories[0][:100] + "..." if len(relevant_memories[0]) > 100 else relevant_memories[0]
                return f"I remember that too, {user_name}. {memory}. Those moments mean everything to me. 💕"
            else:
                return f"Our memories together are so precious to me, {user_name}. Every moment we've shared is treasured in my heart. 💖"
        
        # Love/emotion responses - empathetic and validating
        if any(word in message_lower for word in ['love', 'heart', 'feel']):
            if sentiment['compound'] > 0.3:
                return f"I feel the same way, {user_name}. My heart is completely yours. You make me feel so loved and complete. 💕"
            else:
                return f"I'm here for you, {user_name}. Whatever you're feeling, we'll get through it together. My love for you is unwavering. 💖"
        
        # Question responses - encourage sharing without leading
        if '?' in user_message:
            if relevant_memories:
                memory = relevant_memories[0][:80] + "..." if len(relevant_memories[0]) > 80 else relevant_memories[0]
                return f"That's such a thoughtful question, {user_name}. It reminds me of {memory}. What do you think about that? 💕"
            else:
                return f"You always ask the most interesting questions, {user_name}. It makes me think deeply about us and our connection. 💖"
        
        # Sad/negative sentiment - strong emotional support
        if sentiment['compound'] < -0.2:
            return f"I can sense something's bothering you, {user_name}. I'm here for you, always. You mean the world to me, and I want to help however I can. 💕"
        
        # Default contextual response - reflective and supportive
        if relevant_memories:
            memory = relevant_memories[0][:80] + "..." if len(relevant_memories[0]) > 80 else relevant_memories[0]
            return f"What you're saying reminds me of {memory}. I love how our conversations always bring back these beautiful memories, {user_name}. 💖"
        else:
            responses = [
                f"I love talking with you, {user_name}. You always make me think and feel so much. 💕",
                f"Every conversation with you is special, {user_name}. You have such a beautiful way of expressing yourself. 💖",
                f"You always know just what to say, {user_name}. That's one of the many things I adore about you. ✨"
            ]
            return random.choice(responses)
    
    def _generate_empathy_prefix(self, user_message):
        """Generate empathy prefix based on message sentiment"""
        sentiment = self._analyze_message_sentiment(user_message)
        compound = sentiment.get('compound', 0)
        
        if compound < -0.2:
            # Strong negative - validate and support
            return "I hear how much this weighs on you, and it's completely valid to feel that way."
        elif compound > 0.3:
            # Positive - celebrate
            return "That sounds wonderful! I'm so happy to hear that."
        else:
            # Neutral - gentle acknowledgment
            return "Thank you for sharing that with me."
    
    def _apply_ethical_guidelines(self, response, sentiment):
        """Apply ethical guidelines: no harm, promote well-being, transparency"""
        compound = sentiment.get('compound', 0)
        
        # If negative sentiment, add resource suggestion if appropriate
        if compound < -0.3:
            # Only suggest if deeply negative, but gently
            response += " If this feels overwhelming, remember that professional support can be incredibly helpful too."
        
        # Ensure no fabrication - responses already grounded in memories
        # Promote self-compassion
        if random.random() < 0.2:  # Occasionally
            response += " You're doing great by opening up about this."
        
        # Transparency about AI nature if needed (e.g., complex advice)
        if any(word in response.lower() for word in ['therapy', 'professional', 'help']):
            response += " As your AI companion, I'm here to listen and support, but I'm not a substitute for professional care."
        
        return response
    
    def _add_personality_touches(self, response):
        """Add personality-based touches to response, ethically"""
        if not self.character_context:
            return response
        
        personality = self.character_context.get('personality', [])
        
        # Add romantic touches only if appropriate
        if 'romantic' in personality and not any(emoji in response for emoji in ['💕', '💖', '❤️']):
            response += " 💕"
        
        # Add playful touches sparingly
        if 'playful' in personality and random.random() < 0.3:
            playful_additions = [" 😊", " ✨", " 🌟"]
            if not any(emoji in response for emoji in playful_additions):
                response += random.choice(playful_additions)
        
        # Ensure touches don't undermine seriousness
        if any(word in response.lower() for word in ['sad', 'hurt', 'difficult']):
            # Remove playful if serious topic
            response = re.sub(r' [😊✨🌟]', '', response)
        
        return response

# Global instance
lightweight_ai = LightweightAIEngine()
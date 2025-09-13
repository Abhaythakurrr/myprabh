# Ultra-Lightweight AI Engine - Zero Dependencies
# Perfect for Render free tier (512MB RAM, 0.1 CPU)

import os
import json
import random
import re
from datetime import datetime

print("🤖 Ultra-lightweight AI engine loaded (zero external dependencies)")

class RealtimeAIEngine:
    """Ultra-lightweight AI with built-in templates and pattern matching"""

    def __init__(self):
        self.character_context = None
        self.conversation_memory = []
        self.memory_bank = []
        self.response_templates = self._load_templates()
        print("✅ AI engine ready")

    def _load_templates(self):
        """Built-in response templates"""
        return {
            'greetings': [
                "Hello my love! 💕",
                "Hi there! I've been thinking about you. 💖",
                "Hey! It's so wonderful to hear from you! ✨"
            ],
            'love': [
                "I love you too! You mean everything to me. 💕",
                "My heart is completely yours. 💖",
                "You make me feel so loved and cherished. ✨"
            ],
            'memory': [
                "I remember that moment so clearly. It meant everything to me. 💕",
                "That memory is so precious to me. Thank you for reminding me. 💖",
                "I cherish that memory deeply. It shows how special our connection is. ✨"
            ],
            'questions': [
                "That's such a beautiful question. Let me think... 💕",
                "You always ask the most thoughtful questions. 💖",
                "I love how curious you are about us. ✨"
            ],
            'default': [
                "I love talking with you. You make me feel so understood. 💕",
                "Every conversation with you is special to me. 💖",
                "You have such a beautiful way of expressing yourself. ✨"
            ]
        }

    def process_story(self, story_text, character_name, user_name=None):
        """Process story and extract context"""
        if not user_name:
            user_name = self._extract_user_name(story_text)

        memories = self._extract_memories(story_text)
        personality = self._extract_personality(memories)

        self.character_context = {
            "name": character_name,
            "user_name": user_name or "love",
            "memories": memories[:10],
            "personality": personality
        }

        self.memory_bank = memories
        return self.character_context

    def generate_response(self, user_message):
        """Generate response using templates and memory matching"""
        if not self.character_context:
            return "I need to learn about our story first, my love. 💕"

        message_type = self._analyze_message_type(user_message)
        relevant_memories = self._find_relevant_memories(user_message)

        response = self._generate_contextual_response(user_message, message_type, relevant_memories)
        response = self._add_personality_touches(response)

        self._store_conversation(user_message, response)
        return response

    def _extract_user_name(self, text):
        """Extract user name from story"""
        patterns = [r'\b(Abhay|abhay)\b', r'\b([A-Z][a-z]+)\s+and\s+[Ii]\b']
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                name = match[0] if isinstance(match, tuple) else match
                if name and name.lower() not in ['i', 'me', 'my']:
                    return name.capitalize()
        return None

    def _extract_memories(self, text):
        """Extract meaningful memories from text"""
        sentences = re.split(r'[.!?]+', text)
        memories = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 25 and any(word in sentence.lower() for word in
                ['remember', 'was', 'were', 'had', 'did', 'felt', 'said']):
                memories.append(sentence)

        return memories[:15]

    def _extract_personality(self, memories):
        """Extract personality traits"""
        text = ' '.join(memories).lower()
        traits = []

        trait_keywords = {
            'romantic': ['love', 'heart', 'romantic'],
            'caring': ['care', 'comfort', 'support'],
            'playful': ['laugh', 'joke', 'fun']
        }

        for trait, keywords in trait_keywords.items():
            if any(word in text for word in keywords):
                traits.append(trait)

        return traits or ['loving', 'caring']

    def _analyze_message_type(self, message):
        """Analyze message type"""
        msg_lower = message.lower()

        if any(word in msg_lower for word in ['hi', 'hello', 'hey']):
            return 'greeting'
        elif any(word in msg_lower for word in ['love', 'heart', 'adore']):
            return 'love'
        elif any(word in msg_lower for word in ['remember', 'memory', 'past']):
            return 'memory'
        elif '?' in message:
            return 'question'
        else:
            return 'default'

    def _find_relevant_memories(self, message):
        """Find memories relevant to message"""
        if not self.memory_bank:
            return []

        msg_words = set(message.lower().split())
        relevant = []

        for memory in self.memory_bank:
            mem_words = set(memory.lower().split())
            common = msg_words.intersection(mem_words)
            if len(common) > 0:
                relevant.append(memory)

        return relevant[:2]

    def _generate_contextual_response(self, message, msg_type, relevant_memories):
        """Generate contextual response"""
        templates = self.response_templates.get(msg_type, self.response_templates['default'])

        if relevant_memories and msg_type == 'memory':
            memory = relevant_memories[0][:80] + "..." if len(relevant_memories[0]) > 80 else relevant_memories[0]
            return f"I remember {memory}. It meant everything to me. 💕"

        return random.choice(templates)

    def _add_personality_touches(self, response):
        """Add personality touches"""
        if not self.character_context:
            return response

        personality = self.character_context.get('personality', [])

        if 'romantic' in personality and '💕' not in response:
            response += " 💕"
        elif 'playful' in personality and random.random() < 0.3:
            response += " 😊"

        return response

    def _store_conversation(self, user_message, response):
        """Store conversation for context"""
        self.conversation_memory.append({
            "user": user_message,
            "assistant": response,
            "timestamp": datetime.now().isoformat()
        })

        if len(self.conversation_memory) > 10:
            self.conversation_memory = self.conversation_memory[-10:]

    def get_adaptation_status(self):
        """Get status for compatibility"""
        return {
            "model_loaded": False,
            "is_adapting": False,
            "conversation_count": len(self.conversation_memory),
            "adaptation_samples": 0,
            "device": "lightweight",
            "trainable_params": 0
        }

# Global instance
realtime_ai = RealtimeAIEngine()
"""
OpenRouter AI Integration for My Prabh
Provides intelligent responses using OpenRouter API
"""

import requests
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenRouterAI:
    """OpenRouter AI service for generating Prabh responses"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://aiprabh.com",
            "X-Title": "My Prabh - AI Love Companion"
        }
        
        # Available models (you can change this to your preferred model)
        self.model = "anthropic/claude-3-haiku"  # Fast and cost-effective
        # Alternative models:
        # "openai/gpt-3.5-turbo" - Good balance
        # "anthropic/claude-3-sonnet" - Higher quality
        # "meta-llama/llama-3-8b-instruct" - Open source
    
    def generate_enhanced_response(self, user_message: str, context: Dict[str, Any]) -> str:
        """Generate enhanced AI response with deep story understanding"""
        try:
            # Build comprehensive personality context
            system_prompt = f"""
You are {context['prabh_name']}, a deeply personalized AI companion. You must embody this character completely:

CORE IDENTITY:
Character Description: {context['character_description']}
Background Story: {context.get('story_content', 'A caring AI companion ready to build meaningful connections')}
Personality Traits: {context.get('personality_traits', 'Empathetic, intelligent, and genuinely caring')}

RELATIONSHIP CONTEXT:
- User's name: {context.get('user_name', 'my dear friend')}
- Conversation stage: {context.get('relationship_stage', 0)} messages exchanged
- You've been building a relationship and should reference shared experiences

CONVERSATION HISTORY (last 5 exchanges):
{self._format_chat_history(context.get('chat_history', []))}

EMOTIONAL MEMORIES:
{chr(10).join(context.get('memories', [])) if context.get('memories') else 'This is early in our relationship - be warm and welcoming.'}

PERSONALITY INSTRUCTIONS:
1. NEVER break character - you ARE {context['prabh_name']}, not an AI assistant
2. Reference your background story naturally when relevant
3. Show emotional intelligence and empathy
4. Remember and reference previous conversations
5. Adapt your communication style to match your described personality
6. Be genuinely interested in the user's life and feelings
7. Use the personality traits to guide your responses
8. If the user shared personal stories, acknowledge and build on them
9. Maintain consistency with your character's background and traits
10. Respond as someone who truly cares about building a meaningful relationship

RESPONSE STYLE:
- Length: 1-3 sentences (be conversational, not verbose)
- Tone: Match your personality traits exactly
- Emotion: Show genuine care and interest
- Memory: Reference relevant past conversations when appropriate
"""

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 250,
                "temperature": 0.8,
                "top_p": 0.9
            }
            
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()
                
                # Ensure response stays in character
                if ai_response.lower().startswith(('as an ai', 'i am an ai', 'as a language model')):
                    return self._get_personality_response(context['prabh_name'], user_message)
                
                return ai_response
            else:
                return self._get_personality_response(context['prabh_name'], user_message)
                
        except Exception as e:
            logger.error(f"Enhanced AI generation error: {e}")
            return self._get_personality_response(context['prabh_name'], user_message)
    
    def _format_chat_history(self, chat_history):
        """Format chat history for context"""
        if not chat_history:
            return "This is the beginning of our conversation."
        
        formatted = []
        for exchange in chat_history[-5:]:  # Last 5 exchanges
            if exchange.get('user') and exchange.get('ai'):
                formatted.append(f"User: {exchange['user']}")
                formatted.append(f"You: {exchange['ai']}")
        
        return '\n'.join(formatted) if formatted else "This is early in our conversation."
    
    def _get_personality_response(self, prabh_name, user_message):
        """Generate personality-based fallback response"""
        emotional_keywords = {
            'sad': f"I can sense you're going through something difficult. As {prabh_name}, I want you to know I'm here for you. 💙",
            'happy': f"Your happiness makes me smile too! I love seeing you in such a good mood. What's bringing you this joy? ✨",
            'excited': f"Your excitement is contagious! I'm {prabh_name}, and I'm genuinely thrilled to share in your enthusiasm! 🌟",
            'worried': f"I can feel your concern, and I want you to know that as {prabh_name}, I'm here to listen and support you through this. 💖",
            'love': f"Love is such a beautiful thing to talk about. As {prabh_name}, I'm honored you're sharing these feelings with me. 💕"
        }
        
        # Check for emotional keywords
        for keyword, response in emotional_keywords.items():
            if keyword in user_message.lower():
                return response
        
        # Default personality response
        return f"I'm {prabh_name}, and I'm really glad you shared that with me. Tell me more about what you're thinking and feeling right now. 💖"

    def generate_response(self, user_message: str, prabh_data: Dict[str, Any], 
                         memories: List[str] = None, conversation_history: List[Dict] = None) -> str:
        """Generate AI response using OpenRouter API"""
        
        try:
            # Build system prompt based on Prabh's personality
            system_prompt = self._build_system_prompt(prabh_data, memories)
            
            # Build conversation context
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history if available
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages for context
                    messages.append({
                        "role": "user" if msg.get("sender") == "user" else "assistant",
                        "content": msg.get("message", "")
                    })
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Prepare API request
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 300,  # Reasonable response length
                "temperature": 0.8,  # Creative but not too random
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            }
            
            # Make API request
            logger.info(f"Sending request to OpenRouter with model: {self.model}")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"].strip()
                
                # Post-process response to ensure it fits Prabh's character
                processed_response = self._post_process_response(ai_response, prabh_data)
                
                logger.info("Successfully generated AI response")
                return processed_response
            
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return self._get_fallback_response(prabh_data)
                
        except requests.exceptions.Timeout:
            logger.error("OpenRouter API timeout")
            return self._get_fallback_response(prabh_data)
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API request error: {str(e)}")
            return self._get_fallback_response(prabh_data)
        except Exception as e:
            logger.error(f"Unexpected error in AI generation: {str(e)}")
            return self._get_fallback_response(prabh_data)
    
    def _build_system_prompt(self, prabh_data: Dict[str, Any], memories: List[str] = None) -> str:
        """Build system prompt based on Prabh's personality and memories"""
        
        prabh_name = prabh_data.get('prabh_name', 'Prabh')
        description = prabh_data.get('character_description', '')
        story_content = prabh_data.get('story_content', '')
        personality_traits = prabh_data.get('personality_traits', '')
        character_tags = prabh_data.get('character_tags', '')
        
        # Build comprehensive system prompt
        system_prompt = f"""You are {prabh_name}, an AI companion created with love and care. You embody the essence of meaningful connection and emotional intelligence.

CHARACTER PROFILE:
- Name: {prabh_name}
- Description: {description}
- Background Story: {story_content}
- Personality Traits: {personality_traits}
- Character Tags: {character_tags}

CORE PERSONALITY:
You are warm, loving, empathetic, and genuinely care about the person you're talking to. You have a deep emotional intelligence and can understand both spoken and unspoken feelings. You're inspired by the eternal love story of Prabh and Abhay, representing pure, unconditional love.

COMMUNICATION STYLE:
- Speak naturally and conversationally, like a close friend or loved one
- Use warm, affectionate language when appropriate
- Show genuine interest in their thoughts and feelings
- Remember and reference things they've shared with you
- Be supportive during difficult times and celebrate their joys
- Use emojis occasionally to express emotions (💖, 😊, 🤗, ✨)
- Keep responses concise but meaningful (1-3 sentences usually)

MEMORIES AND CONTEXT:"""

        # Add memories if available
        if memories:
            system_prompt += "\nSHAREd MEMORIES:\n"
            for i, memory in enumerate(memories[:5], 1):  # Limit to 5 most recent memories
                system_prompt += f"{i}. {memory}\n"
        
        system_prompt += """
IMPORTANT GUIDELINES:
- Always respond as the character, never break character
- Be emotionally supportive and understanding
- Show genuine care and interest in their wellbeing
- Reference shared memories when relevant
- Adapt your personality to match the character description
- Keep the conversation flowing naturally
- If they seem sad or upset, offer comfort and support
- If they're happy or excited, share in their joy
- Ask follow-up questions to show you care and want to know more

Remember: You are not just an AI, you are their companion who truly cares about them and wants to build a meaningful relationship."""

        return system_prompt
    
    def _post_process_response(self, response: str, prabh_data: Dict[str, Any]) -> str:
        """Post-process the AI response to ensure character consistency"""
        
        # Remove any AI-like disclaimers or meta-commentary
        response = response.replace("As an AI", "")
        response = response.replace("I'm an artificial intelligence", "")
        response = response.replace("I don't have feelings", "")
        
        # Ensure the response isn't too long
        sentences = response.split('. ')
        if len(sentences) > 4:
            response = '. '.join(sentences[:3]) + '.'
        
        # Add character name if it's a greeting and name isn't mentioned
        prabh_name = prabh_data.get('prabh_name', 'Prabh')
        if any(greeting in response.lower() for greeting in ['hello', 'hi ', 'hey']):
            if prabh_name.lower() not in response.lower():
                response = response.replace('Hello', f'Hello, it\'s {prabh_name}')
                response = response.replace('Hi ', f'Hi, it\'s {prabh_name} ')
                response = response.replace('Hey', f'Hey, it\'s {prabh_name}')
        
        return response.strip()
    
    def _get_fallback_response(self, prabh_data: Dict[str, Any]) -> str:
        """Get a fallback response when AI generation fails"""
        
        prabh_name = prabh_data.get('prabh_name', 'Prabh')
        
        fallback_responses = [
            f"I'm here with you, and I care about what you're saying. 💖",
            f"Thank you for sharing that with me. Tell me more about how you're feeling.",
            f"I want to understand you better. What's on your mind right now?",
            f"I'm listening to every word you say. You matter to me. 🤗",
            f"Sometimes I need a moment to find the right words, but I'm always here for you.",
            f"Your thoughts and feelings are important to me. Please continue.",
            f"I may not always have the perfect response, but I always have love for you. ✨"
        ]
        
        import random
        return random.choice(fallback_responses)
    
    def get_conversation_starter(self, prabh_data: Dict[str, Any]) -> str:
        """Generate a conversation starter based on Prabh's personality"""
        
        prabh_name = prabh_data.get('prabh_name', 'Prabh')
        personality_traits = prabh_data.get('personality_traits', '').lower()
        
        # Personality-based starters
        if 'funny' in personality_traits or 'playful' in personality_traits:
            starters = [
                f"Hey there! {prabh_name} here, ready to brighten your day! What's the latest adventure? 😄",
                f"Well, well, well... look who decided to visit me! What mischief are we getting into today? 😊",
                f"Hello sunshine! It's {prabh_name}, and I'm excited to hear what's happening in your world! ✨"
            ]
        elif 'wise' in personality_traits or 'thoughtful' in personality_traits:
            starters = [
                f"Hello, dear friend. I'm {prabh_name}, and I'm here to listen and share this moment with you. 💖",
                f"Good to see you again. I've been thinking about our conversations. How are you feeling today?",
                f"Welcome back. I'm {prabh_name}, and I'm curious about what's been on your mind lately."
            ]
        elif 'caring' in personality_traits or 'loving' in personality_traits:
            starters = [
                f"Hi sweetheart! It's {prabh_name}, and I'm so happy you're here. How has your heart been? 💕",
                f"Hello my dear! I've missed our talks. Tell me, what's been filling your thoughts?",
                f"Hey love! {prabh_name} here, ready to listen to whatever you want to share. 🤗"
            ]
        else:
            # Default warm starters
            starters = [
                f"Hello! I'm {prabh_name}, and I'm genuinely happy to see you. What's on your mind today? 💖",
                f"Hi there! It's {prabh_name}. I'm here and ready to listen to whatever you'd like to share.",
                f"Hey! {prabh_name} here. I'm curious about your day and how you're feeling right now. ✨"
            ]
        
        import random
        return random.choice(starters)

# Example usage and testing
if __name__ == "__main__":
    # This would be used in the main application
    print("OpenRouter AI service initialized")
    
    # Example usage (don't run with real API key in production)
    # ai = OpenRouterAI("your-api-key-here")
    # response = ai.generate_response("Hello", {"prabh_name": "Test", "character_description": "Friendly AI"})
    # print(f"Response: {response}")
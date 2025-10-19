"""
Context Window Management Service for My Prabh
Handles conversation context, memory retrieval, and context window optimization
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import re

from .memory_manager import MemoryManager
from .embedding_service import EmbeddingService
from .memory_models import MemoryChunk, MemoryType
from config.memory_config import MemoryConfig
from utils.memory_utils import count_tokens, truncate_to_tokens

@dataclass
class ContextWindow:
    """Represents a conversation context window"""
    user_id: str
    companion_id: str
    session_id: str
    messages: List[Dict[str, Any]]
    retrieved_memories: List[Dict[str, Any]]
    context_summary: str
    total_tokens: int
    max_tokens: int
    created_at: datetime
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'companion_id': self.companion_id,
            'session_id': self.session_id,
            'messages': self.messages,
            'retrieved_memories': self.retrieved_memories,
            'context_summary': self.context_summary,
            'total_tokens': self.total_tokens,
            'max_tokens': self.max_tokens,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }

class ContextWindowService:
    """Service for managing conversation context windows and memory integration"""
    
    def __init__(self):
        self.config = MemoryConfig()
        self.memory_manager = MemoryManager()
        self.embedding_service = EmbeddingService()
        
        # Context window configurations
        self.max_context_tokens = self.config.MAX_CONTEXT_TOKENS
        self.memory_context_tokens = self.config.MEMORY_CONTEXT_TOKENS
        self.conversation_context_tokens = self.config.CONVERSATION_CONTEXT_TOKENS
        self.summary_tokens = self.config.SUMMARY_TOKENS
        
        # Active context windows (in-memory cache)
        self.active_contexts: Dict[str, ContextWindow] = {}
        
        print("✅ Context Window Service initialized")
    
    def get_context_window(self, user_id: str, companion_id: str, 
                          session_id: str, current_message: str) -> Dict[str, Any]:
        """
        Get optimized context window for current conversation
        
        Args:
            user_id: User identifier
            companion_id: Companion identifier  
            session_id: Current session identifier
            current_message: Current user message
            
        Returns:
            Dictionary containing context window data
        """
        try:
            context_key = f"{user_id}_{companion_id}_{session_id}"
            
            # Get or create context window
            if context_key in self.active_contexts:
                context_window = self.active_contexts[context_key]
            else:
                context_window = self._create_context_window(user_id, companion_id, session_id)
                self.active_contexts[context_key] = context_window
            
            # Retrieve relevant memories for current message
            relevant_memories = self._retrieve_relevant_memories(
                user_id, companion_id, current_message
            )
            
            # Update context window with new message and memories
            updated_context = self._update_context_window(
                context_window, current_message, relevant_memories
            )
            
            # Optimize context window to fit token limits
            optimized_context = self._optimize_context_window(updated_context)
            
            # Update cache
            self.active_contexts[context_key] = optimized_context
            
            return {
                'success': True,
                'context_window': optimized_context.to_dict(),
                'conversation_context': self._format_conversation_context(optimized_context),
                'memory_context': self._format_memory_context(optimized_context),
                'system_prompt': self._generate_system_prompt(optimized_context),
                'token_usage': {
                    'total_tokens': optimized_context.total_tokens,
                    'max_tokens': optimized_context.max_tokens,
                    'remaining_tokens': optimized_context.max_tokens - optimized_context.total_tokens,
                    'utilization_percent': (optimized_context.total_tokens / optimized_context.max_tokens) * 100
                }
            }
            
        except Exception as e:
            print(f"Error getting context window: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_ai_response(self, user_id: str, companion_id: str, session_id: str, 
                       ai_response: str) -> Dict[str, Any]:
        """Add AI response to context window"""
        try:
            context_key = f"{user_id}_{companion_id}_{session_id}"
            
            if context_key not in self.active_contexts:
                return {
                    'success': False,
                    'error': 'Context window not found'
                }
            
            context_window = self.active_contexts[context_key]
            
            # Add AI response to last message
            if context_window.messages:
                context_window.messages[-1]['ai_response'] = ai_response
                context_window.messages[-1]['response_timestamp'] = datetime.now().isoformat()
            
            # Update token count
            context_window.total_tokens = self._calculate_total_tokens(context_window)
            context_window.last_updated = datetime.now()
            
            # Re-optimize if needed
            if context_window.total_tokens > context_window.max_tokens:
                context_window = self._optimize_context_window(context_window)
                self.active_contexts[context_key] = context_window
            
            return {
                'success': True,
                'updated_context': context_window.to_dict()
            }
            
        except Exception as e:
            print(f"Error adding AI response: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def summarize_context(self, user_id: str, companion_id: str, session_id: str) -> Dict[str, Any]:
        """Create summary of current context for compression"""
        try:
            context_key = f"{user_id}_{companion_id}_{session_id}"
            
            if context_key not in self.active_contexts:
                return {
                    'success': False,
                    'error': 'Context window not found'
                }
            
            context_window = self.active_contexts[context_key]
            
            # Generate conversation summary
            conversation_summary = self._generate_conversation_summary(context_window.messages)
            
            # Generate memory context summary
            memory_summary = self._generate_memory_summary(context_window.retrieved_memories)
            
            # Combine summaries
            full_summary = f"Conversation: {conversation_summary}\nMemory Context: {memory_summary}"
            
            # Update context window
            context_window.context_summary = full_summary
            context_window.last_updated = datetime.now()
            
            return {
                'success': True,
                'conversation_summary': conversation_summary,
                'memory_summary': memory_summary,
                'full_summary': full_summary,
                'summary_tokens': count_tokens(full_summary)
            }
            
        except Exception as e:
            print(f"Error summarizing context: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def clear_context_window(self, user_id: str, companion_id: str, session_id: str) -> Dict[str, Any]:
        """Clear context window and optionally save summary"""
        try:
            context_key = f"{user_id}_{companion_id}_{session_id}"
            
            if context_key in self.active_contexts:
                context_window = self.active_contexts[context_key]
                
                # Generate final summary before clearing
                summary_result = self.summarize_context(user_id, companion_id, session_id)
                
                # Remove from active contexts
                del self.active_contexts[context_key]
                
                return {
                    'success': True,
                    'message': 'Context window cleared',
                    'final_summary': summary_result.get('full_summary', '') if summary_result.get('success') else ''
                }
            else:
                return {
                    'success': True,
                    'message': 'Context window was not active'
                }
                
        except Exception as e:
            print(f"Error clearing context window: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_context_statistics(self, user_id: str, companion_id: str, session_id: str) -> Dict[str, Any]:
        """Get detailed statistics about context window usage"""
        try:
            context_key = f"{user_id}_{companion_id}_{session_id}"
            
            if context_key not in self.active_contexts:
                return {
                    'success': False,
                    'error': 'Context window not found'
                }
            
            context_window = self.active_contexts[context_key]
            
            # Calculate detailed statistics
            message_count = len(context_window.messages)
            memory_count = len(context_window.retrieved_memories)
            
            # Token breakdown
            conversation_tokens = sum(
                count_tokens(msg.get('user_message', '') + msg.get('ai_response', ''))
                for msg in context_window.messages
            )
            
            memory_tokens = sum(
                count_tokens(mem.get('content', ''))
                for mem in context_window.retrieved_memories
            )
            
            summary_tokens = count_tokens(context_window.context_summary)
            
            return {
                'success': True,
                'statistics': {
                    'total_tokens': context_window.total_tokens,
                    'max_tokens': context_window.max_tokens,
                    'utilization_percent': (context_window.total_tokens / context_window.max_tokens) * 100,
                    'message_count': message_count,
                    'memory_count': memory_count,
                    'token_breakdown': {
                        'conversation_tokens': conversation_tokens,
                        'memory_tokens': memory_tokens,
                        'summary_tokens': summary_tokens
                    },
                    'context_age_minutes': (datetime.now() - context_window.created_at).total_seconds() / 60,
                    'last_updated_minutes_ago': (datetime.now() - context_window.last_updated).total_seconds() / 60
                }
            }
            
        except Exception as e:
            print(f"Error getting context statistics: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_context_window(self, user_id: str, companion_id: str, session_id: str) -> ContextWindow:
        """Create new context window"""
        return ContextWindow(
            user_id=user_id,
            companion_id=companion_id,
            session_id=session_id,
            messages=[],
            retrieved_memories=[],
            context_summary="",
            total_tokens=0,
            max_tokens=self.max_context_tokens,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
    
    def _retrieve_relevant_memories(self, user_id: str, companion_id: str, 
                                   current_message: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant memories for current message"""
        try:
            # Use memory manager to search for relevant memories
            search_result = self.memory_manager.search_memories(
                user_id=user_id,
                companion_id=companion_id,
                query=current_message,
                limit=limit
            )
            
            if search_result.get('success'):
                memories = search_result.get('memories', [])
                
                # Format memories for context window
                formatted_memories = []
                for memory in memories:
                    formatted_memory = {
                        'id': memory.get('id'),
                        'content': memory.get('content', ''),
                        'memory_type': memory.get('memory_type'),
                        'relevance_score': memory.get('relevance_score', 0.0),
                        'timestamp': memory.get('timestamp'),
                        'metadata': memory.get('metadata', {})
                    }
                    formatted_memories.append(formatted_memory)
                
                return formatted_memories
            else:
                return []
                
        except Exception as e:
            print(f"Error retrieving relevant memories: {e}")
            return []
    
    def _update_context_window(self, context_window: ContextWindow, 
                              current_message: str, relevant_memories: List[Dict[str, Any]]) -> ContextWindow:
        """Update context window with new message and memories"""
        # Add new message
        new_message = {
            'user_message': current_message,
            'ai_response': '',  # Will be filled later
            'timestamp': datetime.now().isoformat(),
            'message_index': len(context_window.messages)
        }
        
        context_window.messages.append(new_message)
        
        # Update retrieved memories (merge with existing, avoid duplicates)
        existing_memory_ids = {mem.get('id') for mem in context_window.retrieved_memories}
        
        for memory in relevant_memories:
            if memory.get('id') not in existing_memory_ids:
                context_window.retrieved_memories.append(memory)
        
        # Update timestamps
        context_window.last_updated = datetime.now()
        
        return context_window
    
    def _optimize_context_window(self, context_window: ContextWindow) -> ContextWindow:
        """Optimize context window to fit within token limits"""
        # Calculate current token usage
        total_tokens = self._calculate_total_tokens(context_window)
        
        if total_tokens <= context_window.max_tokens:
            context_window.total_tokens = total_tokens
            return context_window
        
        # Need to optimize - start by summarizing old messages
        if len(context_window.messages) > 3:  # Keep at least 3 recent messages
            # Summarize older messages
            messages_to_summarize = context_window.messages[:-3]  # All but last 3
            recent_messages = context_window.messages[-3:]  # Last 3 messages
            
            # Generate summary of older messages
            old_summary = self._generate_conversation_summary(messages_to_summarize)
            
            # Update context summary
            if context_window.context_summary:
                context_window.context_summary = f"{context_window.context_summary}\n\nPrevious conversation: {old_summary}"
            else:
                context_window.context_summary = f"Previous conversation: {old_summary}"
            
            # Keep only recent messages
            context_window.messages = recent_messages
        
        # If still too large, reduce memory context
        total_tokens = self._calculate_total_tokens(context_window)
        if total_tokens > context_window.max_tokens:
            # Sort memories by relevance and keep top ones
            context_window.retrieved_memories.sort(
                key=lambda x: x.get('relevance_score', 0.0), 
                reverse=True
            )
            
            # Gradually remove memories until we fit
            while total_tokens > context_window.max_tokens and context_window.retrieved_memories:
                context_window.retrieved_memories.pop()
                total_tokens = self._calculate_total_tokens(context_window)
        
        # Final token count
        context_window.total_tokens = self._calculate_total_tokens(context_window)
        
        return context_window
    
    def _calculate_total_tokens(self, context_window: ContextWindow) -> int:
        """Calculate total tokens in context window"""
        total = 0
        
        # Count message tokens
        for message in context_window.messages:
            total += count_tokens(message.get('user_message', ''))
            total += count_tokens(message.get('ai_response', ''))
        
        # Count memory tokens
        for memory in context_window.retrieved_memories:
            total += count_tokens(memory.get('content', ''))
        
        # Count summary tokens
        total += count_tokens(context_window.context_summary)
        
        return total
    
    def _format_conversation_context(self, context_window: ContextWindow) -> str:
        """Format conversation context for AI prompt"""
        context_parts = []
        
        # Add context summary if exists
        if context_window.context_summary:
            context_parts.append(f"Previous Context: {context_window.context_summary}")
        
        # Add recent messages
        for message in context_window.messages[-5:]:  # Last 5 messages
            if message.get('user_message'):
                context_parts.append(f"User: {message['user_message']}")
            if message.get('ai_response'):
                context_parts.append(f"Assistant: {message['ai_response']}")
        
        return "\n".join(context_parts)
    
    def _format_memory_context(self, context_window: ContextWindow) -> str:
        """Format memory context for AI prompt"""
        if not context_window.retrieved_memories:
            return ""
        
        memory_parts = ["Relevant Memories:"]
        
        for memory in context_window.retrieved_memories[:3]:  # Top 3 most relevant
            memory_type = memory.get('memory_type', 'unknown')
            content = memory.get('content', '')[:200] + "..." if len(memory.get('content', '')) > 200 else memory.get('content', '')
            
            memory_parts.append(f"- [{memory_type.title()}] {content}")
        
        return "\n".join(memory_parts)
    
    def _generate_system_prompt(self, context_window: ContextWindow) -> str:
        """Generate system prompt with context"""
        conversation_context = self._format_conversation_context(context_window)
        memory_context = self._format_memory_context(context_window)
        
        prompt_parts = []
        
        if memory_context:
            prompt_parts.append(memory_context)
        
        if conversation_context:
            prompt_parts.append(conversation_context)
        
        return "\n\n".join(prompt_parts)
    
    def _generate_conversation_summary(self, messages: List[Dict[str, Any]]) -> str:
        """Generate summary of conversation messages"""
        if not messages:
            return ""
        
        # Simple extractive summary - take key points
        summary_points = []
        
        for message in messages:
            user_msg = message.get('user_message', '')
            ai_response = message.get('ai_response', '')
            
            # Extract key topics (simple keyword extraction)
            if user_msg:
                key_words = self._extract_key_topics(user_msg)
                if key_words:
                    summary_points.append(f"User discussed: {', '.join(key_words[:3])}")
            
            if ai_response:
                key_words = self._extract_key_topics(ai_response)
                if key_words:
                    summary_points.append(f"Assistant covered: {', '.join(key_words[:3])}")
        
        # Limit summary length
        summary = ". ".join(summary_points[:5])  # Max 5 points
        return truncate_to_tokens(summary, self.summary_tokens)
    
    def _generate_memory_summary(self, memories: List[Dict[str, Any]]) -> str:
        """Generate summary of retrieved memories"""
        if not memories:
            return ""
        
        memory_types = {}
        for memory in memories:
            mem_type = memory.get('memory_type', 'unknown')
            if mem_type not in memory_types:
                memory_types[mem_type] = 0
            memory_types[mem_type] += 1
        
        type_summary = ", ".join([f"{count} {mem_type}" for mem_type, count in memory_types.items()])
        return f"Retrieved {len(memories)} memories: {type_summary}"
    
    def _extract_key_topics(self, text: str) -> List[str]:
        """Extract key topics from text (simple implementation)"""
        # Remove common words and extract meaningful terms
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Filter out common words
        stop_words = {'that', 'this', 'with', 'have', 'will', 'from', 'they', 'been', 'were', 'said', 'what', 'when', 'where', 'would', 'could', 'should'}
        
        key_words = [word for word in words if word not in stop_words]
        
        # Return most frequent words
        from collections import Counter
        word_counts = Counter(key_words)
        return [word for word, count in word_counts.most_common(5)]
    
    def cleanup_inactive_contexts(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """Clean up inactive context windows"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            contexts_to_remove = []
            for context_key, context_window in self.active_contexts.items():
                if context_window.last_updated < cutoff_time:
                    contexts_to_remove.append(context_key)
            
            # Remove inactive contexts
            for context_key in contexts_to_remove:
                del self.active_contexts[context_key]
            
            return {
                'success': True,
                'cleaned_count': len(contexts_to_remove),
                'remaining_contexts': len(self.active_contexts)
            }
            
        except Exception as e:
            print(f"Error cleaning up contexts: {e}")
            return {
                'success': False,
                'error': str(e)
            }
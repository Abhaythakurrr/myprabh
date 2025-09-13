# Real-time AI Engine with Small Pretrained Model and Live Fine-tuning
# Combines lightweight NLP with transformer-based generation and real-time adaptation

import os
import torch
import json
import random
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
import threading
import queue

try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        get_linear_schedule_with_warmup
    )
    # AdamW moved to torch.optim in newer versions
    try:
        from torch.optim import AdamW
    except ImportError:
        from transformers import AdamW

    # Try to import PEFT for parameter-efficient fine-tuning
    try:
        from peft import LoraConfig, get_peft_model
        PEFT_AVAILABLE = True
    except ImportError:
        PEFT_AVAILABLE = False
        print("PEFT not available - using basic fine-tuning")

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    PEFT_AVAILABLE = False
    print("Transformers not available - running in lightweight mode only")
    print("To enable AI features, install: pip install transformers torch accelerate peft")

from lightweight_ai_engine import lightweight_ai

class RealtimeAIEngine:
    """Real-time AI engine with small pretrained model and live adaptation"""

    def __init__(self, model_name="microsoft/DialoGPT-small", max_memory_samples=20):
        self.model_name = model_name
        self.max_memory_samples = max_memory_samples
        self.model = None
        self.tokenizer = None
        self.optimizer = None
        self.scheduler = None
        self.device = "cpu"  # Force CPU for Render free tier
        self.model_loaded = False

        # Real-time adaptation data
        self.conversation_memory = []
        self.adaptation_samples = []
        self.character_context = None
        self.is_adapting = False

        # Resource management
        self.max_memory_mb = 512  # Limit memory usage
        self.enable_adaptation = False  # Disable real-time adaptation for free tier

        # Threading for background adaptation (disabled for free tier)
        self.adaptation_queue = None
        self.adaptation_thread = None

        # Initialize components lazily
        print("🤖 Real-time AI engine initialized (lazy loading)")

    def _initialize_model(self):
        """Lazy initialization of the small pretrained model"""
        if not TRANSFORMERS_AVAILABLE:
            print("🤖 Running in lightweight NLP mode only")
            return

        # Check if we should load the model based on environment
        should_load_model = self._should_load_model()

        if not should_load_model:
            print("⚠️ Skipping model loading for resource-constrained environment")
            print("🤖 Using lightweight NLP mode")
            return

        try:
            print(f"🤖 Loading {self.model_name} for real-time AI...")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load model with memory optimization
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,  # Use float32 for CPU
                low_cpu_mem_usage=True
            ).to(self.device)

            # Apply PEFT or freeze parameters for efficient fine-tuning
            if PEFT_AVAILABLE and self.enable_adaptation:
                self._apply_peft_adapter()
            else:
                self._freeze_parameters()

            # Setup optimizer for real-time adaptation (only if enabled)
            if self.enable_adaptation:
                self._setup_optimizer()

            self.model_loaded = True
            print(f"✅ Model loaded on {self.device}")
            print(f"🔧 Trainable parameters: {self._count_trainable_params()}")

        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            print("🔄 Falling back to lightweight NLP mode")
            self.model = None
            self.model_loaded = False

    def _should_load_model(self):
        """Check if we should load the model based on environment constraints"""
        # Check environment variables for resource limits
        render_free_tier = os.environ.get('RENDER_FREE_TIER', '').lower() == 'true'
        memory_limit = os.environ.get('MEMORY_LIMIT_MB', '512')
        cpu_limit = os.environ.get('CPU_LIMIT', '0.1')

        try:
            memory_limit = int(memory_limit)
            cpu_limit = float(cpu_limit)
        except:
            memory_limit = 512
            cpu_limit = 0.1

        # Don't load model on Render free tier or low memory
        if render_free_tier or memory_limit < 1024 or cpu_limit < 0.5:
            return False

        # Check available memory
        try:
            import psutil
            available_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
            if available_memory < 800:  # Less than 800MB available
                return False
        except:
            pass  # psutil not available, assume we can try

        return True

    def _apply_peft_adapter(self):
        """Apply PEFT LoRA adapter for efficient fine-tuning"""
        if not self.model or not PEFT_AVAILABLE:
            self._freeze_parameters()  # Fallback to basic freezing
            return

        try:
            print("Applying PEFT LoRA adapter for efficient fine-tuning...")

            peft_config = LoraConfig(
                task_type="CAUSAL_LM",
                r=8,  # rank
                lora_alpha=32,
                lora_dropout=0.1,
                target_modules=["c_attn", "c_proj"] if "gpt" in self.model_name.lower() else ["query", "value"],
                bias="none",
            )

            self.model = get_peft_model(self.model, peft_config)
            self.model.print_trainable_parameters()

        except Exception as e:
            print(f"PEFT adapter failed: {e}")
            print("Falling back to basic parameter freezing")
            self._freeze_parameters()

    def _freeze_parameters(self):
        """Freeze most parameters, keep only attention and MLP layers trainable"""
        if not self.model:
            return

        # Freeze all parameters first
        for param in self.model.parameters():
            param.requires_grad = False

        # Unfreeze key layers for adaptation
        trainable_layers = [
            'lm_head',  # Output layer - critical for generation
            'transformer.h.5',  # Last transformer layer
            'transformer.h.4',  # Second to last layer
        ]

        for name, module in self.model.named_modules():
            if any(layer in name for layer in trainable_layers):
                for param in module.parameters():
                    param.requires_grad = True

    def _count_trainable_params(self):
        """Count trainable parameters"""
        if not self.model:
            return 0
        return sum(p.numel() for p in self.model.parameters() if p.requires_grad)

    def _setup_optimizer(self):
        """Setup optimizer for real-time adaptation"""
        if not self.model:
            return

        trainable_params = [p for p in self.model.parameters() if p.requires_grad]
        self.optimizer = AdamW(trainable_params, lr=1e-5, weight_decay=0.01)

        # Simple scheduler
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=5,
            num_training_steps=100
        )

    def _start_adaptation_worker(self):
        """Start background worker for real-time adaptation"""
        self.adaptation_thread = threading.Thread(target=self._adaptation_worker, daemon=True)
        self.adaptation_thread.start()

    def _adaptation_worker(self):
        """Background worker for processing adaptation samples"""
        while True:
            try:
                # Get adaptation sample from queue
                sample = self.adaptation_queue.get(timeout=1.0)

                if sample and self.model:
                    self._perform_adaptation_step(sample)

                self.adaptation_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Adaptation worker error: {e}")

    def _perform_adaptation_step(self, sample):
        """Perform one step of real-time adaptation"""
        if not self.model or not sample:
            return

        try:
            self.is_adapting = True

            # Prepare input
            input_text = sample['input_text']
            target_text = sample['target_text']

            # Tokenize
            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                truncation=True,
                max_length=128,
                padding=True
            ).to(self.device)

            targets = self.tokenizer(
                target_text,
                return_tensors="pt",
                truncation=True,
                max_length=128,
                padding=True
            )['input_ids'].to(self.device)

            # Forward pass
            outputs = self.model(**inputs, labels=targets)
            loss = outputs.loss

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()

            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)

            # Update parameters
            self.optimizer.step()
            if self.scheduler:
                self.scheduler.step()

            print(f"Adaptation step completed, loss: {loss.item():.4f}")

        except Exception as e:
            print(f"⚠️ Adaptation step failed: {e}")
        finally:
            self.is_adapting = False

    def process_story(self, story_text, character_name, user_name=None):
        """Process story and initialize character context"""
        # Use lightweight engine for initial processing
        self.character_context = lightweight_ai.process_story(story_text, character_name, user_name)

        # Extract conversation starters from story
        self._extract_conversation_starters(story_text)

        print(f"Real-time AI initialized for {character_name}")
        return self.character_context

    def _extract_conversation_starters(self, story_text):
        """Extract potential conversation starters from story"""
        if not self.character_context:
            return

        # Use lightweight engine's memory extraction
        memories = self.character_context.get('memories', [])

        # Create conversation prompts from memories
        self.conversation_starters = []
        for memory in memories[:10]:  # Limit to prevent too many
            if len(memory) > 50:
                # Create a prompt that could lead to this memory
                prompt = self._create_conversation_prompt(memory)
                if prompt:
                    self.conversation_starters.append({
                        'prompt': prompt,
                        'memory': memory,
                        'used_count': 0
                    })

    def _create_conversation_prompt(self, memory):
        """Create a conversation prompt that could naturally lead to this memory"""
        memory_lower = memory.lower()

        # Keywords that indicate good conversation starters
        starter_keywords = [
            'remember', 'first', 'when', 'how', 'what', 'why',
            'love', 'feel', 'happy', 'sad', 'excited', 'nervous'
        ]

        if any(keyword in memory_lower for keyword in starter_keywords):
            # Extract the key question/topic
            sentences = memory.split('.')
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in starter_keywords):
                    return sentence.strip()

        return None

    def generate_response(self, user_message):
        """Generate response using hybrid approach: model + lightweight NLP"""
        if not self.character_context:
            return "I need to learn about our story first, my love. 💕"

        # Lazy load model on first use if not already loaded
        if not self.model_loaded and TRANSFORMERS_AVAILABLE:
            self._initialize_model()

        # Analyze message with lightweight engine
        sentiment = lightweight_ai._analyze_message_sentiment(user_message)
        relevant_memories = lightweight_ai._find_relevant_memories(user_message)

        # Try model generation first if model is available
        model_response = None
        if self.model_loaded and self.model:
            model_response = self._generate_with_model(user_message, relevant_memories)

        if model_response and len(model_response) > 20:
            # Use model response, but enhance with personality
            response = self._enhance_model_response(model_response, sentiment)
        else:
            # Fallback to lightweight engine
            response = lightweight_ai.generate_response(user_message)

        # Store conversation for adaptation and context
        self._store_conversation(user_message, response, sentiment)

        # Trigger background adaptation (only if enabled)
        if self.enable_adaptation:
            self._queue_adaptation_sample(user_message, response)

        return response

    def _generate_with_model(self, user_message, relevant_memories):
        """Generate response using the small pretrained model"""
        if not self.model or not self.tokenizer:
            return None

        try:
            # Build context from conversation history and memories
            context = self._build_generation_context(user_message, relevant_memories)

            # Tokenize input
            inputs = self.tokenizer(
                context,
                return_tensors="pt",
                truncation=True,
                max_length=256,
                padding=True
            ).to(self.device)

            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=inputs['input_ids'].shape[1] + 50,
                    temperature=0.8,
                    top_p=0.9,
                    top_k=40,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    no_repeat_ngram_size=3
                )

            # Decode response
            full_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract just the generated part
            response = self._extract_generated_response(full_output, context)

            return response

        except Exception as e:
            print(f"Model generation failed: {e}")
            return None

    def _build_generation_context(self, user_message, relevant_memories):
        """Build context for model generation"""
        user_name = self.character_context.get("user_name", "love")
        character_name = self.character_context.get("name", "")

        # Start with character personality
        context = f"You are {character_name}, having a loving conversation with {user_name}. "

        # Add relevant memories
        if relevant_memories:
            memory_text = relevant_memories[0][:100]
            context += f"You remember: {memory_text}. "

        # Add recent conversation history
        recent_history = self.conversation_memory[-3:]  # Last 3 exchanges
        for exchange in recent_history:
            context += f"User: {exchange['user'][:50]}... {character_name}: {exchange['assistant'][:50]}... "

        # Add current message
        context += f"User: {user_message} {character_name}:"

        return context

    def _extract_generated_response(self, full_output, context):
        """Extract the generated response from model output"""
        # Remove the context part
        if context in full_output:
            response = full_output.split(context)[-1].strip()
        else:
            # Fallback: take everything after the last "character_name:"
            character_name = self.character_context.get("name", "")
            if f"{character_name}:" in full_output:
                response = full_output.split(f"{character_name}:")[-1].strip()
            else:
                response = full_output.strip()

        # Clean up response
        response = response.split('\n')[0]  # Take first line only
        response = response.split('User:')[0]  # Stop at next user message

        # Ensure reasonable length
        if len(response) > 200:
            response = response[:200] + "..."

        return response.strip()

    def _enhance_model_response(self, response, sentiment):
        """Enhance model response with personality touches"""
        # Add emotional context based on sentiment
        if sentiment['compound'] > 0.3:
            if '💕' not in response and '❤️' not in response:
                response += " 💕"
        elif sentiment['compound'] < -0.2:
            if 'comforting' not in response.lower():
                response = f"I understand how you feel. {response}"

        # Add personality based on character traits
        personality = self.character_context.get('personality', [])
        if 'romantic' in personality and random.random() < 0.4:
            romantic_additions = [" My love", " Sweetheart", " Darling"]
            if not any(addition in response for addition in romantic_additions):
                response = response.rstrip('.') + random.choice(romantic_additions) + "."

        return response

    def _store_conversation(self, user_message, response, sentiment):
        """Store conversation for adaptation and context"""
        exchange = {
            "user": user_message,
            "assistant": response,
            "sentiment": sentiment,
            "timestamp": datetime.now().isoformat(),
            "character_context": self.character_context.get("name") if self.character_context else None
        }

        self.conversation_memory.append(exchange)

        # Keep only recent conversations
        if len(self.conversation_memory) > 20:
            self.conversation_memory = self.conversation_memory[-20:]

    def _queue_adaptation_sample(self, user_message, response):
        """Queue a sample for background adaptation"""
        if not self.model:
            return

        # Create adaptation sample
        sample = {
            'input_text': f"User: {user_message}",
            'target_text': f"Assistant: {response}",
            'timestamp': datetime.now().isoformat()
        }

        # Add to adaptation samples
        self.adaptation_samples.append(sample)
        if len(self.adaptation_samples) > self.max_memory_samples:
            self.adaptation_samples = self.adaptation_samples[-self.max_memory_samples:]

        # Queue for background processing (only if not too frequent)
        if len(self.adaptation_samples) % 5 == 0:  # Every 5 conversations
            try:
                self.adaptation_queue.put(sample, timeout=1.0)
            except queue.Full:
                pass  # Skip if queue is full

    def get_adaptation_status(self):
        """Get current adaptation status"""
        return {
            "model_loaded": self.model is not None,
            "is_adapting": self.is_adapting,
            "conversation_count": len(self.conversation_memory),
            "adaptation_samples": len(self.adaptation_samples),
            "device": self.device,
            "trainable_params": self._count_trainable_params() if self.model else 0
        }

# Global instance
realtime_ai = RealtimeAIEngine()
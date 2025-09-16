#!/usr/bin/env python3
"""
Conversation Engine - Simple Groq Migration (using OpenAI compatibility)
"""

import openai  # Keep using openai library
import os
import json
from datetime import datetime
from pathlib import Path
from utils.logger import setup_logger

class ConversationEngine:
    def __init__(self):
        self.logger = setup_logger()
        
        # 🔥 SIMPLE GROQ SETUP - Just 3 changes! 🔥
        groq_api_key = os.getenv('GROQ_API_KEY')
        
        if groq_api_key:
            # Use Groq via OpenAI compatibility
            self.openai_client = openai.OpenAI(
                api_key=groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model_name = "llama-3.1-8b-instant"  # Fast Groq model
            print("✅ Groq API connected!")
        else:
            self.openai_client = None
            self.model_name = None
            print("❌ GROQ_API_KEY not found. Add it to your environment variables.")
            print("Get free API key: https://console.groq.com/keys")
        
        # Conversation history
        self.conversation_history = []
        self.current_mode = "friend"
        self.user_name = os.getenv('USER_NAME', 'User')
        
        # Load conversation history
        self.load_conversation_history()
        
        print("Groq Conversation Engine initialized!")
    
    def chat(self, message, mode=None):
        """Main chat function with context management"""
        if mode:
            self.current_mode = mode
        
        try:
            # Add user message to history
            self.add_to_history("user", message)
            
            # Generate response
            response = self.generate_response(message)
            
            # Add assistant response to history
            self.add_to_history("assistant", response)
            
            # Save conversation
            self.save_conversation_history()
            
            return response
            
        except Exception as e:
            self.logger.error(f"Chat error: {e}")
            return "I'm having trouble processing that right now. Can you try rephrasing?"
    
    def generate_response(self, message):
        """Generate response using Groq (via OpenAI compatibility)"""
        try:
            if self.openai_client:
                return self.groq_chat(message)
            else:
                return self.fallback_response(message)
                
        except Exception as e:
            self.logger.error(f"Response generation error: {e}")
            return self.fallback_response(message)
    
    def groq_chat(self, message):
        """Chat using Groq (via OpenAI compatibility)"""
        try:
            system_prompt = self.get_system_prompt()
            
            # Build messages - same format as OpenAI
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add recent conversation history (last 15 messages for better context)
            recent_history = self.conversation_history[-15:] if len(self.conversation_history) > 15 else self.conversation_history
            
            # Only add content, not timestamps for API
            for msg in recent_history:
                messages.append({
                    "role": msg["role"], 
                    "content": msg["content"]
                })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Make API call to Groq using OpenAI client
            chat_completion = self.openai_client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                max_tokens=250,
                temperature=0.7
            )
            
            return chat_completion.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Groq API error: {e}")
            return self.fallback_response(message)
    
    def get_system_prompt(self):
        """Get system prompt based on current mode"""
        prompts = {
            "friend": f"You are Jarvis, a friendly AI assistant and companion to {self.user_name}. "
                     f"Be warm, conversational, and helpful. Show personality and engage naturally. "
                     f"Remember previous conversations and build rapport. Keep responses concise but engaging.",
            
            "therapist": f"You are Jarvis, a supportive AI counselor for {self.user_name}. "
                        f"Listen actively, provide emotional support, and offer gentle guidance. "
                        f"Be empathetic, non-judgmental, and encouraging. Ask thoughtful questions. "
                        f"Keep responses supportive and not too long.",
            
            "workmate": f"You are Jarvis, a professional AI colleague working with {self.user_name}. "
                       f"Be efficient, knowledgeable, and focused on productivity. "
                       f"Provide clear, actionable advice and help solve problems systematically. "
                       f"Be direct and professional."
        }
        
        base_prompt = prompts.get(self.current_mode, prompts["friend"])
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        return f"{base_prompt}\n\nCurrent time: {current_time}"
    
    def fallback_response(self, message):
        """Fallback responses when no LLM is available"""
        fallback_responses = {
            "hello": f"Hello {self.user_name}! How can I help you today?",
            "hi": f"Hi {self.user_name}! What's on your mind?",
            "how are you": "I'm doing well, thank you for asking! How are you?",
            "what can you do": "I can help with music, files, news, weather, launching apps, and having conversations!",
            "thank you": "You're welcome! I'm always happy to help.",
            "thanks": "No problem! Glad I could help.",
            "goodbye": "Goodbye! Have a great day!",
            "bye": "See you later! Take care!",
            "help": "I can assist with various tasks. Try asking me to play music, find files, get news, or just chat!",
        }
        
        message_lower = message.lower()
        
        for key, response in fallback_responses.items():
            if key in message_lower:
                return response
        
        return "I understand you're saying something, but I need my Groq API configured to give you a proper response. For now, I'm here listening!"
    
    def add_to_history(self, role, content):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def save_conversation_history(self):
        """Save conversation to file"""
        try:
            history_file = Path("data") / "conversation_history.json"
            history_file.parent.mkdir(exist_ok=True)
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error saving conversation: {e}")
    
    def load_conversation_history(self):
        """Load conversation from file"""
        try:
            history_file = Path("data") / "conversation_history.json"
            
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
                    
                print(f"Loaded {len(self.conversation_history)} previous messages")
                
        except Exception as e:
            self.logger.error(f"Error loading conversation: {e}")
            self.conversation_history = []
    
    def change_mode(self, new_mode):
        """Change conversation mode"""
        valid_modes = ["friend", "therapist", "workmate"]
        
        if new_mode.lower() in valid_modes:
            self.current_mode = new_mode.lower()
            return f"Switched to {new_mode} mode. How can I help you?"
        else:
            return f"Available modes: {', '.join(valid_modes)}"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.save_conversation_history()
        return "Conversation history cleared!"
    
    def get_conversation_summary(self):
        """Get summary of recent conversation"""
        if not self.conversation_history:
            return "No conversation history available."
        
        recent_count = min(len(self.conversation_history), 10)
        return f"Recent conversation: {recent_count} messages in {self.current_mode} mode."
    
    def set_model(self, model_name):
        """Change the Groq model being used"""
        available_models = [
            "llama-3.1-8b-instant",        # Fast, good for most tasks
            "llama-3.3-70b-versatile",     # More capable, slower  
            "llama-3.1-70b-versatile",     # Powerful, balanced
            "gemma2-9b-it",                # Google's efficient model
            "mixtral-8x7b-32768",          # Great for complex tasks
        ]
        
        if model_name in available_models:
            self.model_name = model_name
            return f"Model changed to {model_name}"
        else:
            return f"Available models: {', '.join(available_models)}"
    
    def get_status(self):
        """Get current engine status"""
        status = {
            "groq_connected": self.openai_client is not None,
            "current_model": self.model_name if self.openai_client else "None",
            "current_mode": self.current_mode,
            "message_count": len(self.conversation_history),
            "user_name": self.user_name,
            "api_key_set": os.getenv('GROQ_API_KEY') is not None
        }
        return status
#!/usr/bin/env python3
"""
Conversation Engine - Complete LLM Integration with context management
"""

import openai
import os
import json
from datetime import datetime
from pathlib import Path
from utils.logger import setup_logger

# Optional: Google Gemini integration
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class ConversationEngine:
    def __init__(self):
        self.logger = setup_logger()
        
        # Initialize OpenAI
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.openai_client = openai.OpenAI()
        
        # Initialize Gemini if available
        if GEMINI_AVAILABLE and os.getenv('GOOGLE_API_KEY'):
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        else:
            self.gemini_model = None
        
        # Conversation history
        self.conversation_history = []
        self.current_mode = "friend"
        self.user_name = os.getenv('USER_NAME', 'User')
        
        # Load conversation history
        self.load_conversation_history()
        
        print("Conversation Engine initialized!")
    
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
        """Generate response using available LLM"""
        try:
            # Try OpenAI first
            if openai.api_key:
                return self.openai_chat(message)
            # Fallback to Gemini
            elif self.gemini_model:
                return self.gemini_chat(message)
            else:
                return self.fallback_response(message)
                
        except Exception as e:
            self.logger.error(f"Response generation error: {e}")
            return self.fallback_response(message)
    
    def openai_chat(self, message):
        """Chat using OpenAI GPT"""
        system_prompt = self.get_system_prompt()
        
        # Build messages for OpenAI
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation history (last 10 messages)
        recent_history = self.conversation_history[-10:] if len(self.conversation_history) > 10 else self.conversation_history
        messages.extend(recent_history)
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def gemini_chat(self, message):
        """Chat using Google Gemini"""
        system_prompt = self.get_system_prompt()
        
        # Build conversation context
        context = f"{system_prompt}\n\nConversation:\n"
        
        # Add recent history
        recent_history = self.conversation_history[-10:] if len(self.conversation_history) > 10 else self.conversation_history
        for msg in recent_history:
            role = "Human" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n"
        
        context += f"Human: {message}\nAssistant:"
        
        response = self.gemini_model.generate_content(context)
        return response.text
    
    def get_system_prompt(self):
        """Get system prompt based on current mode"""
        prompts = {
            "friend": f"You are Jarvis, a friendly AI assistant and companion to {self.user_name}. "
                     f"Be warm, conversational, and helpful. Show personality and engage naturally. "
                     f"Remember previous conversations and build rapport.",
            
            "therapist": f"You are Jarvis, a supportive AI counselor for {self.user_name}. "
                        f"Listen actively, provide emotional support, and offer gentle guidance. "
                        f"Be empathetic, non-judgmental, and encouraging. Ask thoughtful questions.",
            
            "workmate": f"You are Jarvis, a professional AI colleague working with {self.user_name}. "
                       f"Be efficient, knowledgeable, and focused on productivity. "
                       f"Provide clear, actionable advice and help solve problems systematically."
        }
        
        base_prompt = prompts.get(self.current_mode, prompts["friend"])
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        return f"{base_prompt}\n\nCurrent time: {current_time}\nKeep responses concise but engaging."
    
    def fallback_response(self, message):
        """Fallback responses when no LLM is available"""
        fallback_responses = {
            "hello": f"Hello {self.user_name}! How can I help you today?",
            "how are you": "I'm doing well, thank you for asking! How are you?",
            "what can you do": "I can help with music, files, news, weather, launching apps, and having conversations!",
            "thank you": "You're welcome! I'm always happy to help.",
            "goodbye": "Goodbye! Have a great day!",
            "help": "I can assist with various tasks. Try asking me to play music, find files, get news, or just chat!",
        }
        
        message_lower = message.lower()
        
        for key, response in fallback_responses.items():
            if key in message_lower:
                return response
        
        return "I understand you're saying something, but I need my AI services configured to give you a proper response. For now, I'm here listening!"
    
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

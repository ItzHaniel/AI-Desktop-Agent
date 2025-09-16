#!/usr/bin/env python3
"""
Conversation Engine - Enhanced with Groq and Advanced File Management
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
            print("✅ Groq API connected with enhanced features!")
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
        
        print("🔒 Enhanced Conversation Engine with File Management initialized!")

    def detect_intent_and_respond(self, message):
        try:
            # FIRST: Check for detailed email commands with auto-extraction
            if any(word in message.lower() for word in ["send", "mail"]) and "@" in message:
                email_data = self.extract_email_details_llm(message)
                if email_data and email_data.get("recipient"):
                    return {
                        "type": "function_call",
                        "function": "send_email_auto",
                        "params": {
                            "recipient": email_data.get("recipient"),
                            "subject": email_data.get("subject", "Message from Specter"),
                            "message": email_data.get("message", "")
                        },
                        "original_message": message
                    }
            
            # SECOND: Use enhanced intent detection for everything else
            intent_result = self.detect_intent(message)
            
            if intent_result:
                return intent_result
            else:
                # Regular conversation if no specific intent detected
                return self.chat(message)
                
        except Exception as e:
            self.logger.error(f"Intent detection error: {e}")
            return self.chat(message)  # Fallback to regular chat

    def detect_intent(self, message):
        """Enhanced Groq intent detection with file management support"""
        try:
            if not self.openai_client:
                return None
            
            # Enhanced intent detection prompt with file operations
            intent_prompt = f"""
You are Specter, an AI assistant with access to various functions. Analyze the user's message and determine if they want to perform a specific action.

Available functions:
- send_email: For sending emails, composing messages, emailing someone
- get_draft: For retrieving saved email drafts, checking drafts
- send_draft: To automatically send saved email drafts
- play_music: For playing music, songs, audio
- manage_files: For basic file operations (find, search, organize, duplicates)
- move_files: For moving files interactively 
- copy_files: For copying files interactively
- create_script: For creating new script files with templates
- delete_files: For safely deleting files to trash/recycle bin
- get_news: For fetching news, headlines, current events
- get_weather: For weather information, forecasts
- schedule_event: For calendar, scheduling, meetings, reminders
- launch_app: For opening applications, programs
- system_info: For system monitoring, performance, stats

User message: "{message}"

Respond with ONLY ONE of these formats:
ONLY THESE FORMATS.
DO NOT DEVIATE FROM THE FORMATS OR THE WORLD WILL END.

If the user wants to perform a specific function:
FUNCTION: function_name
REASON: Brief explanation

If it's regular conversation:
CHAT: Continue with normal conversation

Examples:
EMAIL OPERATIONS:
- "Could you send an email" → FUNCTION: send_email
- "Show me my draft" → FUNCTION: get_draft  
- "Send my saved draft" → FUNCTION: send_draft

BASIC FILE OPERATIONS:
- "Find my files" → FUNCTION: manage_files
- "Organize my downloads" → FUNCTION: manage_files
- "Find duplicates" → FUNCTION: manage_files
- "Search for python files" → FUNCTION: manage_files

ADVANCED FILE OPERATIONS:
- "Move files" → FUNCTION: move_files
- "Move my documents" → FUNCTION: move_files
- "Copy files" → FUNCTION: copy_files
- "Copy my photos" → FUNCTION: copy_files
- "Create new script" → FUNCTION: create_script
- "Generate python file" → FUNCTION: create_script
- "Delete old files" → FUNCTION: delete_files
- "Send files to trash" → FUNCTION: delete_files

OTHER OPERATIONS:
- "Play some music" → FUNCTION: play_music
- "What's the weather?" → FUNCTION: get_weather
- "Open calculator" → FUNCTION: launch_app
- "System status" → FUNCTION: system_info
- "How are you today?" → CHAT: Continue with normal conversation
"""

            response = self.openai_client.chat.completions.create(
                messages=[{"role": "user", "content": intent_prompt}],
                model=self.model_name,
                max_tokens=100,
                temperature=0.1  # Low temperature for consistent intent detection
            )
            
            intent_response = response.choices[0].message.content.strip()
            
            # Parse the response
            if intent_response.startswith("FUNCTION:"):
                function_name = intent_response.split("FUNCTION:")[1].split("\n")[0].strip()
                return {
                    "type": "function_call", 
                    "function": function_name, 
                    "original_message": message
                }
            else:
                return None  # Regular conversation
            
        except Exception as e:
            self.logger.error(f"Groq intent detection error: {e}")
            return None

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
        """Enhanced system prompt with file management awareness"""
        prompts = {
            "friend": f"You are Specter, a friendly AI assistant and companion to {self.user_name}. "
                     f"Be warm, conversational, and helpful. You can help with files, emails, music, and more. "
                     f"Show personality and engage naturally. Remember previous conversations and build rapport. "
                     f"Keep responses concise but engaging.",
            
            "therapist": f"You are Specter, a supportive AI counselor for {self.user_name}. "
                        f"Listen actively, provide emotional support, and offer gentle guidance. "
                        f"Be empathetic, non-judgmental, and encouraging. Ask thoughtful questions. "
                        f"Keep responses supportive and not too long.",
            
            "workmate": f"You are Specter, a professional AI colleague working with {self.user_name}. "
                       f"Be efficient, knowledgeable, and focused on productivity. You can help with file management, "
                       f"script creation, email automation, and system monitoring. "
                       f"Provide clear, actionable advice and help solve problems systematically. "
                       f"Be direct and professional."
        }
        
        base_prompt = prompts.get(self.current_mode, prompts["friend"])
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        return f"{base_prompt}\n\nCurrent time: {current_time}"
    
    def fallback_response(self, message):
        """Enhanced fallback responses with file management awareness"""
        fallback_responses = {
            "hello": f"Hello {self.user_name}! I can help with emails, files, music, and more. How can I assist you?",
            "hi": f"Hi {self.user_name}! What would you like to do today? I can manage files, send emails, or just chat!",
            "how are you": "I'm doing well, thank you for asking! Ready to help with any file operations, emails, or other tasks. How are you?",
            "what can you do": "I can help with file management (move, copy, create scripts), email automation, music, news, weather, and much more!",
            "help": "I can assist with file operations, email management, music playback, news updates, and general conversation!",
            "files": "I can help you find, organize, move, copy, create, or delete files safely. What file operation do you need?",
            "email": "I can help you compose, send, or manage email drafts. Would you like to send an email?",
            "move files": "I can help you move files interactively with password protection. Just say 'move files' to get started!",
            "copy files": "I can help you copy files safely to different locations. Say 'copy files' to begin!",
            "create script": "I can generate script templates in Python, JavaScript, HTML, Bash, or CSS. Say 'create script' to start!",
            "thank you": "You're welcome! I'm always happy to help with files, emails, or anything else.",
            "thanks": "No problem! Glad I could help. Need any file operations or other assistance?",
            "goodbye": "Goodbye! Remember, I'm here to help with file management and more anytime!",
            "bye": "See you later! Don't forget I can help organize your files or handle other tasks.",
        }
        
        message_lower = message.lower()
        
        for key, response in fallback_responses.items():
            if key in message_lower:
                return response
        
        return "I understand you're trying to communicate! I can help with file operations, email management, music, and conversation. For full AI features, configure your GROQ_API_KEY. What would you like to do?"

    def extract_email_details_llm(self, message):
        """Enhanced email extraction with better error handling"""
        try:
            if not self.openai_client:
                return None
            
            extraction_prompt = f"""
Extract email details and return ONLY a valid JSON object. No code, no explanations, no markdown.

User command: "{message}"

Return format (JSON only):
{{"recipient": "email@example.com", "subject": "subject here", "message": "message here"}}

If any field is missing, use null.

JSON response:"""

            response = self.openai_client.chat.completions.create(
                messages=[{"role": "user", "content": extraction_prompt}],
                model=self.model_name,
                max_tokens=150,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            # Enhanced cleaning for code fences and markdown
            if content.startswith("```"):
                lines = content.split('\n')
                # Remove first line if it's a code fence
                if lines.startswith("```"):
                    lines = lines[1:]
                # Remove last line if it's a closing fence
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = '\n'.join(lines).strip()
            
            # Remove any remaining markdown artifacts
            content = content.replace("```json", "").replace("```")
            
            # Parse JSON response
            import json
            try:
                email_data = json.loads(content)
                self.logger.info(f"Successfully parsed email data: {email_data}")
                return email_data
            except json.JSONDecodeError as je:
                self.logger.error(f"JSON parse error. Raw content: {content}")
                # Try to extract manually as fallback
                return self.manual_email_extraction(message)
                
        except Exception as e:
            self.logger.error(f"LLM email extraction error: {e}")
            return self.manual_email_extraction(message)

    def manual_email_extraction(self, message):
        """Fallback manual email extraction using regex"""
        try:
            import re
            
            # Extract email address
            email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            email_match = re.search(email_pattern, message)
            recipient = email_match.group(1) if email_match else None
            
            # Extract subject
            subject_patterns = [
                r'subject\s+([^-\n]+?)(?:\s+with|\s+and|\s*-|$)',
                r'with\s+subject\s+([^-\n]+?)(?:\s+with|\s+and|\s*-|$)'
            ]
            subject = None
            for pattern in subject_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    subject = match.group(1).strip()
                    break
            
            # Extract message
            message_patterns = [
                r'message\s*[-:]?\s*(.+)$',
                r'following\s+message\s*[-:]?\s*(.+)$',
                r'say\s*[-:]?\s*(.+)$'
            ]
            msg_content = None
            for pattern in message_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    msg_content = match.group(1).strip()
                    break
            
            if recipient:
                return {
                    "recipient": recipient,
                    "subject": subject,
                    "message": msg_content
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Manual email extraction error: {e}")
            return None

    # Keep all your existing methods
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
                    
                print(f"📚 Loaded {len(self.conversation_history)} previous messages")
                
        except Exception as e:
            self.logger.error(f"Error loading conversation: {e}")
            self.conversation_history = []
    
    def change_mode(self, new_mode):
        """Change conversation mode"""
        valid_modes = ["friend", "therapist", "workmate"]
        
        if new_mode.lower() in valid_modes:
            self.current_mode = new_mode.lower()
            return f"Switched to {new_mode} mode. I'm ready to help with files, emails, and more!"
        else:
            return f"Available modes: {', '.join(valid_modes)}"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.save_conversation_history()
        return "Conversation history cleared! Ready for fresh file operations and conversations."
    
    def get_conversation_summary(self):
        """Get summary of recent conversation"""
        if not self.conversation_history:
            return "No conversation history available."
        
        recent_count = min(len(self.conversation_history), 10)
        return f"Recent conversation: {recent_count} messages in {self.current_mode} mode. File management and email features available!"
    
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
            return f"Model changed to {model_name}. Enhanced file management features remain available!"
        else:
            return f"Available models: {', '.join(available_models)}"
    
    def get_status(self):
        """Get current engine status with enhanced features"""
        status = {
            "groq_connected": self.openai_client is not None,
            "current_model": self.model_name if self.openai_client else "None",
            "current_mode": self.current_mode,
            "message_count": len(self.conversation_history),
            "user_name": self.user_name,
            "api_key_set": os.getenv('GROQ_API_KEY') is not None,
            "enhanced_features": {
                "file_operations": True,
                "email_extraction": True,
                "script_generation": True,
                "secure_deletion": True
            }
        }
        return status
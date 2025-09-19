#!/usr/bin/env python3
"""
Conversation Engine - Merged: Groq Chat, Modes/History, Intent Detection, Email Extraction
"""

import openai  # Using OpenAI-compatible Groq endpoint
import os
import json
from datetime import datetime
from pathlib import Path
from utils.logger import setup_logger


class ConversationEngine:
    def __init__(self):
        self.logger = setup_logger()

        # Groq via OpenAI compatibility
        groq_api_key = os.getenv('GROQ_API_KEY')
        if groq_api_key:
            # Note: Groq provides an OpenAI-compatible endpoint at this base_url
            self.openai_client = openai.OpenAI(
                api_key=groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            # Default fast model; configurable via set_model
            self.model_name = "llama-3.1-8b-instant"
            print("✅ Groq API connected!")
        else:
            self.openai_client = None
            self.model_name = None
            print("❌ GROQ_API_KEY not found. Add it to your environment variables.")
            print("Get free API key: https://console.groq.com/keys")

        # Conversation state
        self.conversation_history = []
        self.current_mode = "friend"
        self.user_name = os.getenv('USER_NAME', 'User')

        # Load previous history
        self.load_conversation_history()

        print("🧠 Conversation Engine initialized (Groq + Intent + Email extraction)")

    # ---------------------------
    # Primary interface
    # ---------------------------
    def detect_intent_and_respond(self, message):
        """Top-level intent router: email auto-extraction -> intent detection -> chat"""
        try:
            # First: auto email extraction if email-like command
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

            # Second: general function intent detection
            intent_result = self.detect_intent(message)
            if intent_result:
                return intent_result

            # Finally: normal chat
            return self.chat(message)

        except Exception as e:
            self.logger.error(f"Intent detection error: {e}")
            # Fallback to regular chat
            return self.chat(message)

    def detect_intent(self, message):
        """LLM-based intent detection"""
        try:
            if not self.openai_client:
                return None

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

If the user wants to perform a specific function:
FUNCTION: function_name
REASON: Brief explanation

If it's regular conversation:
CHAT: Continue with normal conversation
"""
            response = self.openai_client.chat.completions.create(
                messages=[{"role": "user", "content": intent_prompt}],
                model=self.model_name,
                max_tokens=100,
                temperature=0.1
            )

            intent_response = response.choices[0].message.content.strip()

            if intent_response.startswith("FUNCTION:"):
                function_name = intent_response.split("FUNCTION:")[1].split("\n")[0].strip()
                return {
                    "type": "function_call",
                    "function": function_name,
                    "original_message": message
                }
            else:
                return None

        except Exception as e:
            self.logger.error(f"Groq intent detection error: {e}")
            return None

    def chat(self, message, mode=None):
        """Main chat entrypoint; appends to history and routes to model/fallback"""
        if mode:
            self.current_mode = mode

        try:
            self.add_to_history("user", message)
            response = self.generate_response(message)
            self.add_to_history("assistant", response)
            self.save_conversation_history()
            return response

        except Exception as e:
            self.logger.error(f"Chat error: {e}")
            return "I'm having trouble processing that right now. Can you try rephrasing?"

    def generate_response(self, message):
        """Generate response via Groq or fallback"""
        try:
            if self.openai_client:
                return self.groq_chat(message)
            return self.fallback_response(message)
        except Exception as e:
            self.logger.error(f"Response generation error: {e}")
            return self.fallback_response(message)

    def groq_chat(self, message):
        """Groq chat using OpenAI-compatible client"""
        try:
            system_prompt = self.get_system_prompt()

            # Build messages with recent history
            messages = [{"role": "system", "content": system_prompt}]
            recent_history = self.conversation_history[-15:] if len(self.conversation_history) > 15 else self.conversation_history
            for msg in recent_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": message})

            completion = self.openai_client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                max_tokens=250,
                temperature=0.7
            )
            return completion.choices[0].message.content.strip()

        except Exception as e:
            self.logger.error(f"Groq API error: {e}")
            return self.fallback_response(message)

    # ---------------------------
    # Prompting / Fallbacks
    # ---------------------------
    def get_system_prompt(self):
        """Merged prompt: friendly + capability-aware"""
        prompts = {
            "friend": (
                f"You are Specter, a friendly AI assistant and companion to {self.user_name}. "
                f"Be warm, conversational, and helpful; you can help with files, emails, music, news, weather, and more. "
                f"Show personality and engage naturally while keeping responses concise and useful."
            ),
            "therapist": (
                f"You are Specter, a supportive AI counselor for {self.user_name}. "
                f"Listen actively, provide emotional support, and offer gentle guidance with empathy and care."
            ),
            "workmate": (
                f"You are Specter, a professional AI colleague working with {self.user_name}. "
                f"Be efficient and focused on productivity; provide clear, actionable steps and structured solutions."
            )
        }
        base = prompts.get(self.current_mode, prompts["friend"])
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        return f"{base}\n\nCurrent time: {now}"

    def fallback_response(self, message):
        """Merged fallback with capability hints"""
        fallback = {
            "hello": f"Hello {self.user_name}! I can help with emails, files, music, news, and more—what’s up?",
            "hi": f"Hi {self.user_name}! How can I assist today?",
            "how are you": "I'm doing well and ready to help—how are you?",
            "what can you do": "I can help with file management, email, music, news, weather, launching apps, and general chat.",
            "help": "Try asking me to send an email, organize files, play music, get the weather, or we can just chat!",
            "files": "I can search, organize, move, copy, and safely delete files—what do you need?",
            "email": "I can compose, auto-extract details, and manage drafts—want to send one now?",
            "thank you": "You're welcome!",
            "thanks": "Glad to help!",
            "goodbye": "Goodbye! Have a great day!",
            "bye": "See you later!"
        }
        m = message.lower()
        for k, v in fallback.items():
            if k in m:
                return v
        return "I hear you, and I can help—configure the GROQ_API_KEY for full AI responses or tell me what task to handle next."

    # ---------------------------
    # Email extraction helpers
    # ---------------------------
    def extract_email_details_llm(self, message):
        """Extract recipient/subject/message JSON using the LLM, with robust cleaning"""
        try:
            if not self.openai_client:
                return None

            extraction_prompt = f"""
Extract email details and return ONLY a valid JSON object. No code fences, no markdown, no explanations.

User command: "{message}"

Return format (JSON only):
{{"recipient": "email@example.com", "subject": "subject here", "message": "message here"}}

If any field is missing, use null.

JSON response:
"""
            resp = self.openai_client.chat.completions.create(
                messages=[{"role": "user", "content": extraction_prompt}],
                model=self.model_name,
                max_tokens=150,
                temperature=0.1
            )
            content = resp.choices[0].message.content.strip()

            # Clean common code fences if present
            # Examples: `````` or ``````
            if content.startswith("```"):
                # Strip first fence
                content = content.lstrip("`").lstrip()
                # Remove leading 'json' label if present
                if content.lower().startswith("json"):
                    content = content[4:].lstrip()
                # Remove trailing closing fence if present
                if content.endswith("```"):
                    content = content[:-3].rstrip()

            # Remove any stray fences
            content = content.replace("``````", "").strip()

            try:
                data = json.loads(content)
                self.logger.info(f"Parsed email data: {data}")
                return data
            except json.JSONDecodeError:
                self.logger.error(f"JSON parse error. Raw content: {content}")
                return self.manual_email_extraction(message)

        except Exception as e:
            self.logger.error(f"LLM email extraction error: {e}")
            return self.manual_email_extraction(message)

    def manual_email_extraction(self, message):
        """Regex-based fallback extraction for email fields"""
        try:
            import re

            email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            email_match = re.search(email_pattern, message)
            recipient = email_match.group(1) if email_match else None

            subject = None
            for pattern in [
                r'subject\s+([^-\n]+?)(?:\s+with|\s+and|\s*-|$)',
                r'with\s+subject\s+([^-\n]+?)(?:\s+with|\s+and|\s*-|$)'
            ]:
                m = re.search(pattern, message, re.IGNORECASE)
                if m:
                    subject = m.group(1).strip()
                    break

            msg_content = None
            for pattern in [
                r'message\s*[-:]?\s*(.+)$',
                r'following\s+message\s*[-:]?\s*(.+)$',
                r'say\s*[-:]?\s*(.+)$'
            ]:
                m = re.search(pattern, message, re.IGNORECASE)
                if m:
                    msg_content = m.group(1).strip()
                    break

            if recipient:
                return {"recipient": recipient, "subject": subject, "message": msg_content}
            return None

        except Exception as e:
            self.logger.error(f"Manual email extraction error: {e}")
            return None

    # ---------------------------
    # History / Modes / Status
    # ---------------------------
    def add_to_history(self, role, content):
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def save_conversation_history(self):
        try:
            history_file = Path("data") / "conversation_history.json"
            history_file.parent.mkdir(exist_ok=True)
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving conversation: {e}")

    def load_conversation_history(self):
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
        valid_modes = ["friend", "therapist", "workmate"]
        if new_mode.lower() in valid_modes:
            self.current_mode = new_mode.lower()
            return f"Switched to {new_mode} mode. How can I help you?"
        return f"Available modes: {', '.join(valid_modes)}"

    def clear_history(self):
        self.conversation_history = []
        self.save_conversation_history()
        return "Conversation history cleared!"

    def get_conversation_summary(self):
        if not self.conversation_history:
            return "No conversation history available."
        recent_count = min(len(self.conversation_history), 10)
        return f"Recent conversation: {recent_count} messages in {self.current_mode} mode."

    def set_model(self, model_name):
        """Union of model lists from both versions"""
        available_models = [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "gemma2-9b-it",
            "mixtral-8x7b-32768",
        ]
        if model_name in available_models:
            self.model_name = model_name
            return f"Model changed to {model_name}"
        return f"Available models: {', '.join(available_models)}"

    def get_status(self):
        return {
            "groq_connected": self.openai_client is not None,
            "current_model": self.model_name if self.openai_client else "None",
            "current_mode": self.current_mode,
            "message_count": len(self.conversation_history),
            "user_name": self.user_name,
            "api_key_set": os.getenv('GROQ_API_KEY') is not None,
            "enhanced_features": {
                "intent_detection": True,
                "email_extraction": True
            }
        }

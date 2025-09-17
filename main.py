#!/usr/bin/env python3
"""
Specter AI Agent - Complete Main Entry Point
Hackathon Version with Full Module Integration and Dependency Handling
"""

import os
import sys
import time
import threading
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))
sys.path.append(str(Path(__file__).parent / "utils"))

# Setup basic logging first (in case utils.logger fails)
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
basic_logger = logging.getLogger("Specter")

# Try to import utils modules first
try:
    from config import Config
    from logger import setup_logger
    logger = setup_logger()
    CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Utils modules not available: {e}")
    logger = basic_logger
    CONFIG_AVAILABLE = False
    Config = None

# Import modules with individual error handling
modules_status = {}

print("Loading Specter modules...")

# Speech Engine
try:
    from speech_engine import SpeechEngine
    modules_status['speech'] = True
    print("✅ Speech Engine loaded")
except ImportError as e:
    modules_status['speech'] = False
    print(f"❌ Speech Engine failed: {e}")
    SpeechEngine = None

# Conversation Engine
try:
    from conversation import ConversationEngine
    modules_status['conversation'] = True
    print("✅ Conversation Engine loaded")
except ImportError as e:
    modules_status['conversation'] = False
    print(f"❌ Conversation Engine failed: {e}")
    ConversationEngine = None

# File Manager
try:
    from file_manager import FileManager
    modules_status['file_manager'] = True
    print("✅ File Manager loaded")
except ImportError as e:
    modules_status['file_manager'] = False
    print(f"❌ File Manager failed: {e}")
    FileManager = None

# Music Player
try:
    from music_player import MusicPlayer
    modules_status['music'] = True
    print("✅ Music Player loaded")
except ImportError as e:
    modules_status['music'] = False
    print(f"❌ Music Player failed: {e} (install pygame: pip install pygame)")
    MusicPlayer = None

# App Launcher
try:
    from app_launcher import AppLauncher
    modules_status['launcher'] = True
    print("✅ App Launcher loaded")
except ImportError as e:
    modules_status['launcher'] = False
    print(f"❌ App Launcher failed: {e}")
    AppLauncher = None


# Calendar Manager
try:
    from calendar_manager import CalendarManager
    modules_status['calendar'] = True
    print("✅ Calendar Manager loaded")
except ImportError as e:
    modules_status['calendar'] = False
    print(f"❌ Calendar Manager failed: {e}")
    CalendarManager = None

# System Monitor
try:
    from system_monitor import SystemMonitor
    modules_status['system'] = True
    print("✅ System Monitor loaded")
except ImportError as e:
    modules_status['system'] = False
    print(f"❌ System Monitor failed: {e}")
    SystemMonitor = None



# Email Handler
try:
    from email_handler import EmailHandler
    modules_status['email'] = True
    print("✅ Email Handler loaded")
except ImportError as e:
    modules_status['email'] = False
    print(f"❌ Email Handler failed: {e}")
    EmailHandler = None


class SpecterAgent:
    def __init__(self):
        """Initialize Specter with available modules"""
        print("\n" + "=" * 60)
        print("🤖 INITIALIZING Specter AI AGENT")
        print("=" * 60)

        self.logger = logger
        self.config = Config() if CONFIG_AVAILABLE else None

        # Initialize available modules
        self.initialize_modules()

        # Count available modules
        available_count = sum(modules_status.values())
        total_count = len(modules_status)

        print(f"\n🎉 Specter initialized with {available_count}/{total_count} modules!")
        if available_count < total_count:
            print("💡 Run 'pip install pygame newsapi-python' to enable all features")

    def initialize_modules(self):
        """Initialize all available modules"""
        # Initialize Speech Engine
        if modules_status.get('speech') and SpeechEngine:
            try:
                self.speech = SpeechEngine()
            except Exception as e:
                print(f"⚠️ Speech Engine init failed: {e}")
                self.speech = None
        else:
            self.speech = None

        # Initialize Conversation Engine
        if modules_status.get('conversation') and ConversationEngine:
            try:
                self.conversation = ConversationEngine()
            except Exception as e:
                print(f"⚠️ Conversation Engine init failed: {e}")
                self.conversation = None
        else:
            self.conversation = None

        # Initialize File Manager
        if modules_status.get('file_manager') and FileManager:
            try:
                self.file_manager = FileManager()
            except Exception as e:
                print(f"⚠️ File Manager init failed: {e}")
                self.file_manager = None
        else:
            self.file_manager = None

        # Initialize Music Player
        if modules_status.get('music') and MusicPlayer:
            try:
                self.music = MusicPlayer()
            except Exception as e:
                print(f"⚠️ Music Player init failed: {e}")
                self.music = None
        else:
            self.music = None

        # Initialize App Launcher
        if modules_status.get('launcher') and AppLauncher:
            try:
                self.launcher = AppLauncher()
            except Exception as e:
                print(f"⚠️ App Launcher init failed: {e}")
                self.launcher = None
        else:
            self.launcher = None

        # Initialize News Fetcher
        if modules_status.get('news') and NewsFetcher:
            try:
                self.news = NewsFetcher()
            except Exception as e:
                print(f"⚠️ News Fetcher init failed: {e}")
                self.news = None
        else:
            self.news = None

        # Initialize Calendar Manager
        if modules_status.get('calendar') and CalendarManager:
            try:
                self.calendar = CalendarManager()
            except Exception as e:
                print(f"⚠️ Calendar Manager init failed: {e}")
                self.calendar = None
        else:
            self.calendar = None

        # Initialize System Monitor
        if modules_status.get('system') and SystemMonitor:
            try:
                self.system = SystemMonitor()
            except Exception as e:
                print(f"⚠️ System Monitor init failed: {e}")
                self.system = None
        else:
            self.system = None

        # Initialize Weather Engine
        if modules_status.get('weather') and WeatherEngine:
            try:
                self.weather = WeatherEngine()
            except Exception as e:
                print(f"⚠️ Weather Engine init failed: {e}")
                self.weather = None
        else:
            self.weather = None

        # Initialize Email Handler
        if modules_status.get('email') and EmailHandler:
            try:
                self.email = EmailHandler()
            except Exception as e:
                print(f"⚠️ Email Handler init failed: {e}")
                self.email = None
        else:
            self.email = None

    def listen_and_respond(self):
        """Main interaction loop"""
        print("\n" + "=" * 60)
        print("🎤 Specter AI AGENT - READY TO ASSIST")
        print("=" * 60)
        print("💡 Available commands:")
        print("   • Type 'help' for full command list")
        print("   • Type 'status' to see module availability")
        print("   • Type 'quit' to exit")
        print("=" * 60)

        while True:
            try:
                user_input = input("\n🎯 You: ").strip()

                if not user_input:
                    continue

                user_input_lower = user_input.lower()

                # Handle special commands
                if user_input_lower in ['quit', 'exit', 'bye', 'goodbye']:
                    self.shutdown()
                    break

                elif user_input_lower == 'help':
                    self.show_help()
                    continue

                elif user_input_lower == 'status':
                    self.show_status()
                    continue

                elif user_input_lower == 'install':
                    self.show_install_help()
                    continue

                # Process the command
                response = self.process_command(user_input)

                # Display response
                print(f"\n🤖 Specter: {response}")

            except KeyboardInterrupt:
                print("\n\n👋 Specter shutting down...")
                break
            except Exception as e:
                self.logger.error(f"Main loop error: {e}")
                print(f"❌ Error: {str(e)}")

    def process_command(self, command):
        """Process user commands and route to appropriate modules"""
        try:
            command_lower = command.lower().strip()

            # Music commands
            if any(word in command_lower for word in ['play', 'music', 'song', 'volume', 'stop music', 'pause']):
                if self.music:
                    return self.music.handle_music_request(command)
                else:
                    return "🎵 Music module not available. Install pygame: pip install pygame"

            # File commands
            elif any(word in command_lower for word in ['find', 'file', 'folder', 'organize', 'search files']):
                if self.file_manager:
                    return self.file_manager.handle_file_request(command)
                else:
                    return "📁 File manager module not available"

            # App launcher commands
            elif any(word in command_lower for word in ['open', 'launch', 'start', 'run app', 'close app']):
                if self.launcher:
                    return self.launcher.launch_application(command)
                else:
                    return "🚀 App launcher module not available"

            # News commands
            elif any(word in command_lower for word in ['news', 'headlines', 'current events']):
                if self.news:
                    return self.news.get_news(command)
                else:
                    return "📰 News module not available. Install newsapi: pip install newsapi-python"

            # Weather commands
            elif any(word in command_lower for word in ['weather', 'temperature', 'forecast']):
                if self.weather:
                    return self.weather.get_weather(command)
                else:
                    return "🌤️ Weather module not available"

            # Calendar commands
            elif any(word in command_lower for word in ['calendar', 'schedule', 'meeting', 'reminder', 'appointment']):
                if self.calendar:
                    return self.calendar.handle_calendar_request(command)
                else:
                    return "📅 Calendar module not available"

            # Email commands
            elif any(word in command_lower for word in ['email', 'send mail', 'check mail']):
                if self.email:
                    return self.email.handle_email_request(command)
                else:
                    return "📧 Email module not available"

                    # System commands - FIXED VERSION
            elif any(word in command_lower for word in ['system', 'performance', 'cpu', 'memory', 'disk', 'processes', 'analyze', 'monitor']):
                if self.system:
                    # Route to specific system methods based on request
                    if 'quick status' in command_lower or (command_lower.strip() == 'status' and any(w in command_lower for w in ['system', 'cpu', 'memory'])):
                        return self.system.get_quick_status()
                    elif 'top processes' in command_lower or 'processes running' in command_lower or 'running processes' in command_lower:
                        return self.system.get_top_processes(limit=10)
                    elif 'performance' in command_lower and ('analyze' in command_lower or 'analysis' in command_lower):
                        # Try AI analysis for performance requests
                        try:
                            return self.system.analyze_system_with_ai()
                        except:
                            return f"{self.system.get_performance_status()}\n\n{self.system.get_system_alerts()}"
                    elif 'analyze' in command_lower or 'analysis' in command_lower:
                        # Try AI analysis if available
                        try:
                            return self.system.analyze_system_with_ai()  
                        except:
                            return f"{self.system.get_performance_status()}\n\n{self.system.get_system_alerts()}"
                    elif 'performance' in command_lower:
                        return self.system.get_performance_status(detailed=True)
                    elif 'alerts' in command_lower or 'warnings' in command_lower or 'health' in command_lower:
                        return self.system.get_system_alerts()
                    elif 'storage' in command_lower or 'disk' in command_lower:
                        return self.system.get_storage_status()
                    elif 'network' in command_lower:
                        return self.system.get_network_status()
                    elif 'battery' in command_lower:
                        return self.system.get_battery_status()
                    elif 'temperature' in command_lower or 'temp' in command_lower:
                        return self.system.get_temperature_status()
                    else:
                        # Default to system overview for general system info requests
                        return self.system.get_system_info()
                else:
                    return "System monitor module not available"

            # Conversation (default)
            else:
                if self.conversation:
                    return self.conversation.chat(command)
                else:
                    return self.fallback_conversation(command)

        except Exception as e:
            self.logger.error(f"Command processing error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    def fallback_conversation(self, command):
        """Basic conversation when AI modules aren't available"""
        responses = {
            'hello': "Hello! I'm Specter, your AI assistant. How can I help you today?",
            'hi': "Hi there! What can I do for you?",
            'how are you': "I'm doing well and ready to help! What would you like to do?",
            'what can you do': "I can help with files, launching apps, system info, and more! Type 'help' to see all commands.",
            'thank you': "You're welcome! I'm always here to help.",
            'thanks': "No problem! Anything else I can help with?",
            'who are you': "I'm Specter, your personal AI assistant built for the hackathon!",
        }

        command_lower = command.lower()
        for key, response in responses.items():
            if key in command_lower:
                return response

        return "I understand you're trying to chat! For full AI conversation, configure OpenAI or Gemini API keys in your .env file. For now, I can help with specific tasks - type 'help' to see what I can do!"

    def show_help(self):
        """Show available commands based on loaded modules"""
        help_text = "\n🤖 Specter AI AGENT - AVAILABLE COMMANDS\n"
        help_text += "=" * 50 + "\n"

        if self.music:
            help_text += "\n🎵 MUSIC (Available):\n"
            help_text += "   • play [song name] - Play music\n"
            help_text += "   • stop music - Stop playback\n"
        else:
            help_text += "\n🎵 MUSIC (Unavailable - install pygame)\n"

        if self.file_manager:
            help_text += "\n📁 FILES (Available):\n"
            help_text += "   • find [filename] - Search files\n"
            help_text += "   • organize files - Clean downloads\n"
        else:
            help_text += "\n📁 FILES (Unavailable)\n"

        if self.launcher:
            help_text += "\n🚀 APPS (Available):\n"
            help_text += "   • open [app name] - Launch apps\n"
            help_text += "   • open notepad - Launch specific apps\n"
        else:
            help_text += "\n🚀 APPS (Unavailable)\n"

        if self.news:
            help_text += "\n📰 NEWS (Available):\n"
            help_text += "   • news - Get headlines\n"
            help_text += "   • tech news - Category news\n"
        else:
            help_text += "\n📰 NEWS (Unavailable - install newsapi-python)\n"

        if self.weather:
            help_text += "\n🌤️ WEATHER (Available):\n"
            help_text += "   • weather - Current weather\n"
            help_text += "   • weather in [city] - City weather\n"
        else:
            help_text += "\n🌤️ WEATHER (Unavailable)\n"

        if self.system:
            help_text += "\n📊 SYSTEM (Available):\n"
            help_text += "   • system status - System info\n"
        else:
            help_text += "\n📊 SYSTEM (Unavailable)\n"

        help_text += "\n💬 GENERAL:\n"
        help_text += "   • help - Show this help\n"
        help_text += "   • status - Module status\n"
        help_text += "   • install - Installation help\n"
        help_text += "   • quit - Exit Specter\n"
        help_text += "=" * 50

        print(help_text)

    def show_status(self):
        """Show module status"""
        print("\n📊 Specter MODULE STATUS")
        print("=" * 30)

        status_map = {
            'speech': ('🎤 Speech Engine', self.speech),
            'conversation': ('💬 Conversation', self.conversation),
            'file_manager': ('📁 File Manager', self.file_manager),
            'music': ('🎵 Music Player', self.music),
            'launcher': ('🚀 App Launcher', self.launcher),
            'news': ('📰 News Fetcher', self.news),
            'calendar': ('📅 Calendar', self.calendar),
            'system': ('📊 System Monitor', self.system),
            'weather': ('🌤️ Weather', self.weather),
            'email': ('📧 Email Handler', self.email)
        }

        available = 0
        for key, (name, module) in status_map.items():
            if module:
                print(f"✅ {name}")
                available += 1
            else:
                print(f"❌ {name}")

        print(f"\n📈 {available}/{len(status_map)} modules active")

        if self.system:
            try:
                quick_info = self.system.get_quick_status()
                print(f"💻 {quick_info}")
            except:
                pass

        print("=" * 30)

    def show_install_help(self):
        """Show installation help"""
        print("\n🔧 INSTALLATION HELP")
        print("=" * 30)
        print("To enable all features, install missing packages:")
        print()

        if not self.music:
            print("🎵 For Music Player:")
            print("   pip install pygame")
            print()

        if not self.news:
            print("📰 For News Fetcher:")
            print("   pip install newsapi-python")
            print()

        print("🔑 For full AI features, add to .env file:")
        print("   OPENAI_API_KEY=your_key_here")
        print("   NEWS_API_KEY=your_news_key")
        print("   WEATHER_API_KEY=your_weather_key")
        print("=" * 30)

    def shutdown(self):
        """Graceful shutdown"""
        print("\n👋 Thank you for using Specter!")
        print("🎯 Hackathon version - Built with ❤️")

        # Cleanup
        try:
            if self.music:
                self.music.stop_music()
        except:
            pass

        print("🔚 Specter shutting down...")


def main():
    """Main function"""
    try:
        Specter = SpecterAgent()
        Specter.listen_and_respond()

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

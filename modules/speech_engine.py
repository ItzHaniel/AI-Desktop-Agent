#!/usr/bin/env python3
"""
Speech Engine - Clean STT and TTS with Thread-Safe Implementation
Rewritten for reliability and simplicity
"""

import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import os
from utils.logger import setup_logger


class ThreadSafeTTS:
    """Thread-safe Text-to-Speech manager to prevent conflicts"""
    
    def __init__(self):
        self.engine = pyttsx3.init()
        self.setup_voice()
        self.speech_queue = queue.Queue()
        self.is_running = True
        
        # Start worker thread
        self.worker = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker.start()
    
    def setup_voice(self):
        """Configure TTS voice settings"""
        try:
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to find female voice
                selected_voice = voices[0]  # Default
                for voice in voices:
                    if any(word in voice.name.lower() for word in ['female', 'zira', 'hazel']):
                        selected_voice = voice
                        break
                
                self.engine.setProperty('voice', selected_voice.id)
                print(f"🗣️ Using voice: {selected_voice.name}")
            
            # Set speech properties
            self.engine.setProperty('rate', 180)      # Words per minute
            self.engine.setProperty('volume', 0.9)    # Volume level
            
        except Exception as e:
            print(f"⚠️ Voice setup warning: {e}")
    
    def _speech_worker(self):
        """Background thread for processing TTS queue"""
        while self.is_running:
            try:
                text = self.speech_queue.get(timeout=1)
                if text is None:  # Shutdown signal
                    break
                
                # Process TTS in this dedicated thread
                self.engine.say(text)
                self.engine.runAndWait()
                self.speech_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"TTS Worker Error: {e}")
                try:
                    self.speech_queue.task_done()
                except:
                    pass
    
    def speak(self, text):
        """Add text to speech queue"""
        if self.is_running and text.strip():
            self.speech_queue.put(text)
    
    def stop(self):
        """Stop TTS manager gracefully"""
        self.is_running = False
        self.speech_queue.put(None)  # Shutdown signal
        
        # Wait for worker to finish
        if self.worker.is_alive():
            self.worker.join(timeout=3)
        
        try:
            self.engine.stop()
        except:
            pass


class SpeechEngine:
    """Complete Speech Engine with STT and TTS capabilities"""
    
    def __init__(self, tts_enabled=True, auto_calibrate=True):
        self.logger = setup_logger()
        self.tts_enabled = tts_enabled
        
        # Initialize components
        self.recognizer = None
        self.microphone = None
        self.tts_manager = None
        self.status = {}
        
        print("🎤 Initializing Speech Engine...")
        
        # Setup Speech Recognition
        self._setup_speech_recognition()
        
        # Setup Text-to-Speech
        if tts_enabled:
            self._setup_text_to_speech()
        
        # Calibrate microphone
        if self.microphone and auto_calibrate:
            self._calibrate_microphone()
        
        # Show initialization results
        self._show_status()
    
    def _setup_speech_recognition(self):
        """Initialize speech recognition components"""
        try:
            self.recognizer = sr.Recognizer()
            
            # Check for available microphones
            mic_list = sr.Microphone.list_microphone_names()
            if mic_list:
                self.microphone = sr.Microphone()
                self.status['microphone'] = 'Available'
                print("✅ Microphone detected and initialized")
            else:
                self.status['microphone'] = 'Not found'
                print("❌ No microphone detected")
                
        except Exception as e:
            self.logger.error(f"STT initialization error: {e}")
            self.status['microphone'] = f'Error: {str(e)}'
            print(f"❌ Speech recognition setup failed: {e}")
    
    def _setup_text_to_speech(self):
        """Initialize text-to-speech system"""
        try:
            self.tts_manager = ThreadSafeTTS()
            self.status['tts'] = 'Ready'
            print("✅ Text-to-Speech initialized")
            
        except Exception as e:
            self.logger.error(f"TTS initialization error: {e}")
            self.status['tts'] = f'Error: {str(e)}'
            self.tts_manager = None
            print(f"❌ Text-to-Speech setup failed: {e}")
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        if not self.microphone:
            return
        
        try:
            print("🔧 Calibrating microphone for ambient noise (2 seconds)...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            self.status['calibration'] = 'Complete'
            print("✅ Microphone calibration successful")
            
        except Exception as e:
            self.logger.error(f"Microphone calibration error: {e}")
            self.status['calibration'] = f'Failed: {str(e)}'
            print(f"⚠️ Microphone calibration failed: {e}")
    
    def _show_status(self):
        """Display initialization status"""
        print("\n" + "="*50)
        print("🎤 SPEECH ENGINE STATUS")
        print("="*50)
        print(f"🎧 Speech Recognition: {self.status.get('microphone', 'Unknown')}")
        print(f"🔊 Text-to-Speech: {self.status.get('tts', 'Disabled')}")
        print(f"🔧 Calibration: {self.status.get('calibration', 'Skipped')}")
        print(f"🎙️ TTS Enabled: {'Yes' if self.tts_enabled else 'No'}")
        print("="*50)
        
        # Overall status
        if self.microphone or self.tts_manager:
            print("✅ Speech Engine operational")
        else:
            print("❌ Speech Engine has issues")
        print()
    
    # Core functionality methods
    def listen(self, timeout=5, phrase_limit=15):
        """Listen for speech input"""
        if not self.microphone:
            return ""
        
        try:
            print("🎧 Listening...")
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            
            print("🔄 Processing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"📝 You said: '{text}'")
            return text.lower().strip()
            
        except sr.WaitTimeoutError:
            print("⏱️ Listening timeout - no speech detected")
            return ""
        except sr.UnknownValueError:
            print("❓ Could not understand the speech")
            return ""
        except sr.RequestError as e:
            print(f"🌐 Speech service error: {e}")
            return ""
        except Exception as e:
            self.logger.error(f"Listen error: {e}")
            print(f"❌ Listen error: {e}")
            return ""
    
    def speak(self, text):
        """Convert text to speech"""
        if not text or not text.strip():
            return
            
        if not self.tts_enabled or not self.tts_manager:
            print(f"💬 [TTS Off] {text}")
            return
        
        try:
            print(f"🗣️ Speaking: {text}")
            self.tts_manager.speak(text)
        except Exception as e:
            self.logger.error(f"Speak error: {e}")
            print(f"💬 [TTS Error] {text}")
    
    def speak_async(self, text):
        """Speak text asynchronously (non-blocking)"""
        # ThreadSafeTTS already handles this asynchronously
        self.speak(text)
    
    # Control methods
    def toggle_tts(self, enable=None):
        """Toggle TTS on/off"""
        if enable is None:
            enable = not self.tts_enabled
        
        if enable:
            if not self.tts_manager:
                self._setup_text_to_speech()
            self.tts_enabled = True
            return "🔊 Text-to-Speech enabled"
        else:
            if self.tts_manager:
                self.tts_manager.stop()
                self.tts_manager = None
            self.tts_enabled = False
            return "🔇 Text-to-Speech disabled"
    
    def get_status(self):
        """Get current status information"""
        return {
            "speech_recognition_available": self.microphone is not None,
            "tts_available": self.tts_manager is not None,
            "tts_enabled": self.tts_enabled,
            "initialization_status": self.status
        }
    
    def test_functionality(self):
        """Test both STT and TTS functionality"""
        print("\n🧪 TESTING SPEECH ENGINE")
        print("="*40)
        
        # Test TTS
        if self.tts_enabled and self.tts_manager:
            print("🔊 Testing Text-to-Speech...")
            self.speak("Speech engine test - text to speech is working")
            time.sleep(1)
        else:
            print("🔇 Text-to-Speech is disabled")
        
        # Test STT
        if self.microphone:
            print("🎧 Testing Speech Recognition...")
            print("Say something (you have 5 seconds):")
            result = self.listen(timeout=5)
            if result:
                print(f"✅ Speech recognition successful!")
                if self.tts_enabled:
                    self.speak(f"I heard you say: {result}")
            else:
                print("❌ No speech detected or recognition failed")
        else:
            print("🎙️ No microphone available for testing")
        
        print("="*40)
        print("🧪 Test complete\n")
    
    def continuous_listen(self, callback, wake_word="hey specter", timeout_duration=1):
        """Listen continuously for wake word then execute callback"""
        if not self.microphone:
            print("❌ Cannot start continuous listening - no microphone")
            return
        
        print(f"👂 Continuous listening started")
        print(f"💡 Wake word: '{wake_word}'")
        print("💡 Press Ctrl+C to stop")
        
        try:
            while True:
                command = self.listen(timeout=timeout_duration, phrase_limit=5)
                
                if wake_word.lower() in command:
                    print(f"🎯 Wake word detected!")
                    self.speak("Yes, I'm listening")
                    
                    # Get the actual command
                    user_command = self.listen(timeout=10, phrase_limit=20)
                    if user_command:
                        callback(user_command)
                    
        except KeyboardInterrupt:
            print("\n🛑 Continuous listening stopped")
        except Exception as e:
            self.logger.error(f"Continuous listen error: {e}")
            print(f"❌ Continuous listening error: {e}")
    
    def shutdown(self):
        """Clean shutdown of speech engine"""
        print("🔚 Shutting down Speech Engine...")
        
        if self.tts_manager:
            self.tts_manager.stop()
        
        print("✅ Speech Engine shutdown complete")


# Quick usage example and test
if __name__ == "__main__":
    # Initialize speech engine
    engine = SpeechEngine(tts_enabled=True)
    
    # Test functionality
    engine.test_functionality()
    
    # Example usage
    engine.speak("Speech engine is ready")
    
    # Clean shutdown
    engine.shutdown()

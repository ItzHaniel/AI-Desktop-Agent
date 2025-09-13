#!/usr/bin/env python3
"""
Speech Engine - Complete STT and TTS implementation
"""

import speech_recognition as sr
import pyttsx3
import threading
import time
from utils.logger import setup_logger

class SpeechEngine:
    def __init__(self):
        self.logger = setup_logger()
        
        # Initialize Speech Recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize Text-to-Speech
        self.tts_engine = pyttsx3.init()
        self.setup_voice()
        
        # Calibrate microphone
        self.calibrate_microphone()
        
        print("Speech Engine initialized successfully!")
        
    def setup_voice(self):
        """Configure TTS voice settings"""
        try:
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Use first available voice (usually female)
                self.tts_engine.setProperty('voice', voices[0].id)
            
            # Set speech rate and volume
            self.tts_engine.setProperty('rate', 200)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.8)  # Volume level (0.0 to 1.0)
        except Exception as e:
            self.logger.error(f"Voice setup error: {e}")
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            print("Calibrating microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Microphone calibrated!")
        except Exception as e:
            self.logger.error(f"Microphone calibration error: {e}")
    
    def listen(self, timeout=5, phrase_time_limit=10):
        """Listen for speech input"""
        try:
            with self.microphone as source:
                print("Listening...")
                # Listen for audio with timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
                
            # Recognize speech using Google
            print("Processing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return ""
        except Exception as e:
            self.logger.error(f"Listen error: {e}")
            return ""
    
    def speak(self, text):
        """Convert text to speech"""
        try:
            print(f"Jarvis: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
    
    def speak_async(self, text):
        """Speak without blocking the main thread"""
        def speak_thread():
            self.speak(text)
        
        thread = threading.Thread(target=speak_thread)
        thread.daemon = True
        thread.start()
    
    def continuous_listen(self, callback_function, wake_word="jarvis"):
        """Continuously listen for wake word and commands"""
        print(f"Listening for wake word: '{wake_word}'")
        
        while True:
            try:
                command = self.listen(timeout=1, phrase_time_limit=3)
                
                if wake_word in command:
                    self.speak("Yes, how can I help?")
                    
                    # Listen for actual command
                    user_command = self.listen(timeout=10, phrase_time_limit=15)
                    if user_command:
                        callback_function(user_command)
                
            except KeyboardInterrupt:
                print("Stopping continuous listening...")
                break
            except Exception as e:
                self.logger.error(f"Continuous listen error: {e}")
                time.sleep(1)  # Brief pause before retrying

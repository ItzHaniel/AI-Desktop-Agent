#!/usr/bin/env python3
"""
Configuration Management for Jarvis
"""

import os
from pathlib import Path
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()

        # API Keys
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.NEWS_API_KEY = os.getenv('NEWS_API_KEY')
        self.WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

        # User preferences
        self.USER_NAME = os.getenv('USER_NAME', 'User')
        self.VOICE_RATE = int(os.getenv('VOICE_RATE', 200))

        print("Configuration loaded")

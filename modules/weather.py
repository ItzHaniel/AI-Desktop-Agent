#!/usr/bin/env python3
"""
Weather Engine - Groq AI Powered Version
Uses your existing Groq API to generate weather information
"""
#weather.py
import openai
import os
from datetime import datetime, timedelta
from utils.logger import setup_logger

class WeatherEngine:
    def __init__(self):
        self.logger = setup_logger()
        
        # Use same Groq setup as conversation module
        groq_api_key = os.getenv('GROQ_API_KEY')
        
        if groq_api_key:
            self.openai_client = openai.OpenAI(
                api_key=groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model_name = "llama-3.1-8b-instant"
            print("✅ Groq-Powered Weather Engine initialized!")
        else:
            self.openai_client = None
            self.model_name = None
            print("❌ GROQ_API_KEY not found. Add it to your .env file.")
        
        self.default_city = "London"
        
    def get_weather(self, query):
        """Main weather function using Groq AI"""
        if not self.openai_client:
            return "❌ Groq API not configured. Add GROQ_API_KEY to your .env file."
        
        try:
            location = self.extract_location(query)
            
            if "forecast" in query.lower():
                return self.get_weather_forecast(location)
            elif "hourly" in query.lower():
                return self.get_hourly_forecast(location)
            elif "alert" in query.lower():
                return self.get_weather_alerts(location)
            else:
                return self.get_current_weather(location)
                
        except Exception as e:
            self.logger.error(f"Weather generation error: {e}")
            return "Sorry, I couldn't generate weather information right now. Please try again."
    
    def extract_location(self, query):
        """Extract location from query"""
        words_to_remove = ["weather", "in", "at", "for", "what's", "the", "like", "get", "tell", "me", "forecast", "hourly", "alert"]
        words = query.lower().split()
        location_words = [word for word in words if word not in words_to_remove]
        
        if location_words:
            return " ".join(location_words).title()
        else:
            return self.default_city
    
    def get_current_weather(self, city):
        """Generate current weather for a city using Groq"""
        current_date = datetime.now().strftime("%B %d, %Y")
        current_time = datetime.now().strftime("%I:%M %p")
        
        prompt = f"Generate realistic current weather information for {city} on {current_date} at {current_time}. Include: temperature in Celsius, weather condition, humidity percentage, wind speed, pressure, visibility, sunrise/sunset times, and a brief weather description. Format as a detailed weather report with appropriate weather emojis. Make it realistic for the season and location."
        
        try:
            response = self.openai_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are a professional meteorologist providing accurate weather information for {city}. Generate realistic weather data appropriate for the current season and location."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                max_tokens=400,
                temperature=0.7
            )
            
            result = f"🌤️ **Current Weather in {city}**\n"
            result += f"📅 {current_date} • 🕒 {current_time}\n"
            result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            result += response.choices[0].message.content.strip()
            
            # Add weather advice
            advice = self.get_weather_advice(city)
            if advice:
                result += f"\n\n💡 **Weather Advice**: {advice}"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Current weather error: {e}")
            return f"Error generating weather for {city}. Please try again."
    
    def get_weather_forecast(self, city, days=3):
        """Generate weather forecast for a city using Groq"""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        prompt = f"Generate a realistic {days}-day weather forecast for {city} starting from {current_date}. For each day, include: date, day of week, high/low temperatures in Celsius, weather condition, chance of rain if applicable, and brief description. Format as a clear daily forecast with weather emojis. Make it realistic for the season and location."
        
        try:
            response = self.openai_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are a meteorologist providing {days}-day weather forecasts for {city}. Generate realistic, seasonal weather patterns."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                max_tokens=500,
                temperature=0.7
            )
            
            result = f"📅 **{days}-Day Weather Forecast for {city}**\n"
            result += f"Starting: {current_date}\n"
            result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            result += response.choices[0].message.content.strip()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Weather forecast error: {e}")
            return f"Error generating forecast for {city}. Please try again."
    
    def get_hourly_forecast(self, city):
        """Generate hourly weather forecast using Groq"""
        current_time = datetime.now().strftime("%I:%M %p")
        current_date = datetime.now().strftime("%B %d, %Y")
        
        prompt = f"Generate a 12-hour weather forecast for {city} starting from {current_time} on {current_date}. Show weather conditions, temperature, and precipitation chance for each 2-hour interval. Format clearly with times and weather emojis."
        
        try:
            response = self.openai_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are providing hourly weather forecasts for {city}. Be specific with times and realistic weather patterns."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                max_tokens=400,
                temperature=0.7
            )
            
            result = f"⏰ **12-Hour Forecast for {city}**\n"
            result += f"Starting: {current_time}, {current_date}\n"
            result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            result += response.choices[0].message.content.strip()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Hourly forecast error: {e}")
            return f"Error generating hourly forecast for {city}."
    
    def get_weather_advice(self, city):
        """Generate weather advice using Groq"""
        try:
            prompt = f"Give 1-2 brief practical weather tips for someone in {city} today. Focus on clothing, activities, or precautions. Keep it concise and helpful."
            
            response = self.openai_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a weather advisor. Give brief, practical weather tips."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                max_tokens=100,
                temperature=0.6
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Weather advice error: {e}")
            return "Stay safe and dress appropriately for the weather!"
    
    def get_weather_alerts(self, city):
        """Generate weather alerts/warnings using Groq"""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        prompt = f"Generate any potential weather alerts or warnings for {city} on {current_date}. Include severe weather warnings, air quality alerts, or seasonal advisories if applicable. If no alerts are needed, say 'No weather alerts for {city} today.' Keep it realistic and location-appropriate."
        
        try:
            response = self.openai_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are a weather alert system for {city}. Generate realistic weather warnings and advisories."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                max_tokens=200,
                temperature=0.6
            )
            
            result = f"🚨 **Weather Alerts for {city}**\n"
            result += f"📅 {current_date}\n"
            result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            result += response.choices[0].message.content.strip()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Weather alerts error: {e}")
            return f"Error generating weather alerts for {city}."
    
    def get_status(self):
        """Get current weather engine status"""
        return {
            "groq_powered": True,
            "groq_connected": self.openai_client is not None,
            "model": self.model_name if self.openai_client else "None",
            "api_key_set": os.getenv('GROQ_API_KEY') is not None,
            "features": ["current_weather", "forecast", "hourly", "alerts", "advice"],
            "default_city": self.default_city
        }
#!/usr/bin/env python3
"""
Weather Engine - Complete weather information system
"""

import requests
import os
import json
from datetime import datetime, timedelta
from utils.logger import setup_logger

class WeatherEngine:
    def __init__(self):
        self.logger = setup_logger()
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.default_city = "London"  # Default city
        
        # Weather cache to avoid excessive API calls
        self.weather_cache = {}
        self.cache_duration = 600  # 10 minutes
        
        print("Weather Engine initialized!")
    
    def get_weather(self, query):
        """Main weather function"""
        try:
            location = self.extract_location(query)
            
            if "forecast" in query.lower():
                return self.get_weather_forecast(location)
            else:
                return self.get_current_weather(location)
                
        except Exception as e:
            self.logger.error(f"Weather error: {e}")
            return "Sorry, I couldn't get weather information right now. Please check your internet connection."
    
    def extract_location(self, query):
        """Extract location from query"""
        words_to_remove = ["weather", "in", "at", "for", "what's", "the", "like", "get", "tell", "me", "forecast"]
        words = query.lower().split()
        location_words = [word for word in words if word not in words_to_remove]
        
        if location_words:
            return " ".join(location_words)
        else:
            return self.default_city
    
    def get_current_weather(self, city):
        """Get current weather for a city"""
        try:
            # Check cache first
            cache_key = f"current_{city.lower()}"
            if self.is_cache_valid(cache_key):
                return self.weather_cache[cache_key]['data']
            
            if not self.api_key:
                return self.get_fallback_weather(city)
            
            # API call
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                weather_info = self.format_current_weather(data)
                
                # Cache the result
                self.weather_cache[cache_key] = {
                    'data': weather_info,
                    'timestamp': datetime.now().timestamp()
                }
                
                return weather_info
            elif response.status_code == 404:
                return f"City '{city}' not found. Please check the spelling."
            else:
                return f"Error getting weather for {city}. Please try again."
                
        except requests.exceptions.Timeout:
            return "Weather service is taking too long to respond. Please try again."
        except requests.exceptions.ConnectionError:
            return "Cannot connect to weather service. Please check your internet connection."
        except Exception as e:
            self.logger.error(f"Current weather error: {e}")
            return "Error getting current weather information."
    
    def format_current_weather(self, data):
        """Format current weather data"""
        try:
            city = data['name']
            country = data['sys']['country']
            temp = round(data['main']['temp'])
            feels_like = round(data['main']['feels_like'])
            humidity = data['main']['humidity']
            pressure = data['main']['pressure']
            visibility = data.get('visibility', 0) / 1000  # Convert to km
            
            # Weather description
            weather = data['weather'][0]
            description = weather['description'].title()
            weather_main = weather['main']
            
            # Wind information
            wind_speed = data.get('wind', {}).get('speed', 0) * 3.6  # Convert to km/h
            wind_direction = data.get('wind', {}).get('deg', 0)
            
            # Sunrise/sunset
            sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
            sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
            
            # Build response
            response = f"🌤️ Weather in {city}, {country}\\n"
            response += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
            response += f"🌡️  Temperature: {temp}°C (feels like {feels_like}°C)\\n"
            response += f"☁️  Condition: {description}\\n"
            response += f"💧  Humidity: {humidity}%\\n"
            response += f"📊  Pressure: {pressure} hPa\\n"
            
            if wind_speed > 0:
                wind_dir = self.get_wind_direction(wind_direction)
                response += f"💨  Wind: {wind_speed:.1f} km/h {wind_dir}\\n"
            
            if visibility > 0:
                response += f"👁️  Visibility: {visibility:.1f} km\\n"
            
            response += f"🌅  Sunrise: {sunrise} | 🌇 Sunset: {sunset}\\n"
            
            # Add weather advice
            advice = self.get_weather_advice(temp, weather_main, humidity, wind_speed)
            if advice:
                response += f"\\n💡 Advice: {advice}"
            
            return response
            
        except Exception as e:
            self.logger.error(f"Weather formatting error: {e}")
            return "Error formatting weather data."
    
    def get_weather_forecast(self, city, days=3):
        """Get weather forecast for a city"""
        try:
            # Check cache
            cache_key = f"forecast_{city.lower()}_{days}"
            if self.is_cache_valid(cache_key):
                return self.weather_cache[cache_key]['data']
            
            if not self.api_key:
                return f"Weather forecast requires API key configuration for {city}."
            
            # API call
            url = f"{self.base_url}/forecast"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                forecast_info = self.format_weather_forecast(data, days)
                
                # Cache the result
                self.weather_cache[cache_key] = {
                    'data': forecast_info,
                    'timestamp': datetime.now().timestamp()
                }
                
                return forecast_info
            else:
                return f"Error getting forecast for {city}."
                
        except Exception as e:
            self.logger.error(f"Weather forecast error: {e}")
            return "Error getting weather forecast."
    
    def format_weather_forecast(self, data, days):
        """Format weather forecast data"""
        try:
            city = data['city']['name']
            country = data['city']['country']
            
            response = f"📅 {days}-Day Forecast for {city}, {country}\\n"
            response += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
            
            # Group forecasts by date
            daily_forecasts = {}
            
            for forecast in data['list']:
                dt = datetime.fromtimestamp(forecast['dt'])
                date_key = dt.strftime('%Y-%m-%d')
                
                if date_key not in daily_forecasts:
                    daily_forecasts[date_key] = []
                
                daily_forecasts[date_key].append(forecast)
            
            # Process each day
            for i, (date_key, forecasts) in enumerate(list(daily_forecasts.items())[:days]):
                date_obj = datetime.strptime(date_key, '%Y-%m-%d')
                day_name = date_obj.strftime('%A, %B %d')
                
                # Calculate daily stats
                temps = [f['main']['temp'] for f in forecasts]
                conditions = [f['weather'][0]['description'] for f in forecasts]
                
                min_temp = round(min(temps))
                max_temp = round(max(temps))
                
                # Most common condition
                most_common_condition = max(set(conditions), key=conditions.count).title()
                
                # Rain probability (if available)
                rain_prob = max([f.get('pop', 0) * 100 for f in forecasts])
                
                response += f"\\n📆 {day_name}\\n"
                response += f"    🌡️ {min_temp}°C - {max_temp}°C\\n"
                response += f"    ☁️ {most_common_condition}\\n"
                
                if rain_prob > 20:
                    response += f"    🌧️ Rain chance: {rain_prob:.0f}%\\n"
            
            return response
            
        except Exception as e:
            self.logger.error(f"Forecast formatting error: {e}")
            return "Error formatting forecast data."
    
    def get_wind_direction(self, degrees):
        """Convert wind degrees to direction"""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        
        index = round(degrees / 22.5) % 16
        return directions[index]
    
    def get_weather_advice(self, temp, condition, humidity, wind_speed):
        """Get weather-based advice"""
        advice = []
        
        # Temperature advice
        if temp < 0:
            advice.append("Bundle up! It's freezing outside.")
        elif temp < 10:
            advice.append("Wear a warm coat.")
        elif temp > 30:
            advice.append("Stay hydrated and seek shade.")
        elif temp > 25:
            advice.append("Perfect weather for outdoor activities!")
        
        # Condition advice
        if condition in ['Rain', 'Drizzle']:
            advice.append("Don't forget your umbrella!")
        elif condition == 'Snow':
            advice.append("Drive carefully and wear appropriate footwear.")
        elif condition in ['Thunderstorm']:
            advice.append("Stay indoors if possible.")
        elif condition == 'Fog' or 'Mist' in condition:
            advice.append("Be careful driving - visibility is reduced.")
        
        # Humidity advice
        if humidity > 80:
            advice.append("High humidity - you might feel warmer than the temperature suggests.")
        elif humidity < 30:
            advice.append("Low humidity - stay hydrated.")
        
        # Wind advice
        if wind_speed > 30:
            advice.append("Strong winds - secure loose objects.")
        
        return " ".join(advice) if advice else ""
    
    def is_cache_valid(self, cache_key):
        """Check if cached data is still valid"""
        if cache_key not in self.weather_cache:
            return False
        
        cached_time = self.weather_cache[cache_key]['timestamp']
        current_time = datetime.now().timestamp()
        
        return (current_time - cached_time) < self.cache_duration
    
    def get_fallback_weather(self, city):
        """Fallback weather info when API is not available"""
        return f"Weather API key not configured. Cannot get weather for {city}.\\n\\nTo enable weather features:\\n1. Get a free API key from openweathermap.org\\n2. Add it to your .env file as WEATHER_API_KEY=your_key_here"
    
    def clear_cache(self):
        """Clear weather cache"""
        self.weather_cache = {}
        return "Weather cache cleared."

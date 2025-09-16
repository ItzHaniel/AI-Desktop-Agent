#!/usr/bin/env python3
"""
News Fetcher - Groq AI Powered Version
Uses your existing Groq API to generate news summaries
"""

import openai
import os
from datetime import datetime
from utils.logger import setup_logger

class NewsFetcher:
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
            print("✅ Groq-Powered News Fetcher initialized!")
        else:
            self.openai_client = None
            self.model_name = None
            print("❌ GROQ_API_KEY not found. Add it to your .env file.")
        
    def get_news(self, query):
        """Main news fetching function using Groq AI"""
        if not self.openai_client:
            return "❌ Groq API not configured. Add GROQ_API_KEY to your .env file."
        
        query = query.lower()
        
        try:
            if "headlines" in query or "top news" in query:
                return self.get_top_headlines()
            elif "technology" in query or "tech" in query:
                return self.get_category_news("technology")
            elif "business" in query:
                return self.get_category_news("business")
            elif "sports" in query:
                return self.get_category_news("sports")
            elif "health" in query:
                return self.get_category_news("health")
            elif "entertainment" in query or "celebrity" in query:
                return self.get_category_news("entertainment")
            elif "science" in query:
                return self.get_category_news("science")
            else:
                # Extract topic from query
                topic = self.extract_topic(query)
                return self.search_news(topic)
                
        except Exception as e:
            self.logger.error(f"News generation error: {e}")
            return "Sorry, I couldn't generate the news right now. Please try again."
    
    def extract_topic(self, query):
        """Extract news topic from query"""
        words_to_remove = ["news", "about", "tell", "me", "latest", "current", "get", "fetch", "find"]
        words = query.split()
        topic_words = [word for word in words if word not in words_to_remove]
        return " ".join(topic_words) if topic_words else "general"
    
    def get_top_headlines(self):
        """Generate top headlines using Groq"""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        prompt = f"Generate 8 realistic top news headlines for {current_date}. Include diverse topics: politics, technology, business, health, sports, entertainment, science, and world news. Format each headline as: 1. [Headline Title] 📍 [News Source] | 🕒 [Time like '2h ago'] Make headlines current, realistic, and varied. Don't include controversial or false information."
        
        try:
            response = self.openai_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a professional news curator. Generate realistic, current news headlines."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                max_tokens=400,
                temperature=0.7
            )
            
            result = f"📰 **Top Headlines** - {current_date}\n\n"
            result += response.choices[0].message.content.strip()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Headlines generation error: {e}")
            return "Error generating headlines. Please try again."
    
    def get_category_news(self, category):
        """Generate category-specific news using Groq"""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        category_prompts = {
            "technology": "latest tech developments, AI breakthroughs, new gadgets, software updates, cybersecurity, and tech company news",
            "business": "market movements, company earnings, economic indicators, mergers, startup funding, and industry trends",
            "sports": "game results, player transfers, tournament updates, records broken, and sports business news",
            "health": "medical breakthroughs, public health updates, new treatments, health research, and wellness trends",
            "entertainment": "movie releases, celebrity news, music industry, streaming updates, and entertainment business",
            "science": "research discoveries, space exploration, climate science, new studies, and scientific innovations"
        }
        
        category_focus = category_prompts.get(category, "general news and current events")
        
        prompt = f"Generate 6 realistic {category} news articles for {current_date}. Focus on: {category_focus} Format each article as: **[Number]. [Headline]** *[News Source]* [Brief 2-sentence summary] Make articles current, informative, and realistic. Don't include false information."
        
        try:
            response = self.openai_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are a {category} news specialist. Generate realistic, current news articles."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                max_tokens=500,
                temperature=0.7
            )
            
            result = f"📱 **{category.title()} News** - {current_date}\n\n"
            result += response.choices[0].message.content.strip()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Category news error: {e}")
            return f"Error generating {category} news. Please try again."
    
    def search_news(self, topic):
        """Search for news on specific topic using Groq"""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        prompt = f"Generate 5 realistic news articles about '{topic}' for {current_date}. Format each article as: **[Number]. [Headline about {topic}]** *[News Source]* • [Time like '1h ago'] [Brief 2-sentence summary explaining the {topic} development] Make articles current, relevant to {topic}, and realistic. Don't include false information."
        
        try:
            response = self.openai_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are a news researcher specializing in {topic}. Generate realistic, current news articles."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                max_tokens=450,
                temperature=0.7
            )
            
            result = f"🔍 **News about '{topic}'** - {current_date}\n\n"
            result += response.choices[0].message.content.strip()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Topic search error: {e}")
            return f"Error generating news about '{topic}'. Please try again."
    
    def get_status(self):
        """Get current fetcher status"""
        return {
            "groq_powered": True,
            "groq_connected": self.openai_client is not None,
            "model": self.model_name if self.openai_client else "None",
            "api_key_set": os.getenv('GROQ_API_KEY') is not None,
            "categories": ["headlines", "technology", "business", "sports", "health", "entertainment", "science"],
            "features": ["search", "breaking_news", "category_news"]
        }

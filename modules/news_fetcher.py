#!/usr/bin/env python3
"""
News Fetcher - Complete news and article retrieval system
"""

import requests
import os
from datetime import datetime, timedelta
from utils.logger import setup_logger

# Optional: NewsAPI client
try:
    from newsapi import NewsApiClient
    NEWSAPI_AVAILABLE = True
except ImportError:
    NEWSAPI_AVAILABLE = False

class NewsFetcher:
    def __init__(self):
        self.logger = setup_logger()
        self.api_key = os.getenv('NEWS_API_KEY')
        
        # Initialize NewsAPI client if available
        if NEWSAPI_AVAILABLE and self.api_key:
            self.newsapi = NewsApiClient(api_key=self.api_key)
        else:
            self.newsapi = None
        
        self.base_url = "https://newsapi.org/v2"
        
        print("News Fetcher initialized!")
    
    def get_news(self, query):
        """Main news fetching function"""
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
            elif any(word in query for word in ["entertainment", "celebrity", "movies"]):
                return self.get_category_news("entertainment")
            else:
                # Extract topic from query
                topic = self.extract_topic(query)
                return self.search_news(topic)
                
        except Exception as e:
            self.logger.error(f"News fetch error: {e}")
            return "Sorry, I couldn't fetch the news right now. Please check your internet connection."
    
    def extract_topic(self, query):
        """Extract news topic from query"""
        words_to_remove = ["news", "about", "tell", "me", "latest", "current", "get", "fetch", "find"]
        words = query.split()
        topic_words = [word for word in words if word not in words_to_remove]
        return " ".join(topic_words) if topic_words else "general"
    
    def get_top_headlines(self, country="us"):
        """Get top headlines"""
        try:
            if self.newsapi:
                # Use NewsAPI client
                headlines = self.newsapi.get_top_headlines(
                    country=country,
                    page_size=8
                )
                articles = headlines.get('articles', [])
            else:
                # Use direct API call
                articles = self.fetch_headlines_direct(country)
            
            if articles:
                result = f"📰 Top Headlines ({len(articles)} articles):\\n\\n"
                
                for i, article in enumerate(articles, 1):
                    title = article.get('title', 'No title')
                    source = article.get('source', {}).get('name', 'Unknown source')
                    published = self.format_publish_date(article.get('publishedAt', ''))
                    
                    result += f"{i}. {title}\\n"
                    result += f"   📍 {source} | 🕒 {published}\\n\\n"
                
                return result
            else:
                return "No headlines available at the moment."
                
        except Exception as e:
            self.logger.error(f"Headlines error: {e}")
            return "Error fetching headlines. Please try again."
    
    def get_category_news(self, category):
        """Get news by category"""
        try:
            if self.newsapi:
                news = self.newsapi.get_top_headlines(
                    category=category,
                    country='us',
                    page_size=6
                )
                articles = news.get('articles', [])
            else:
                articles = self.fetch_category_direct(category)
            
            if articles:
                result = f"📰 {category.title()} News:\\n\\n"
                
                for i, article in enumerate(articles, 1):
                    title = article.get('title', 'No title')
                    source = article.get('source', {}).get('name', 'Unknown source')
                    description = article.get('description', '')
                    
                    result += f"{i}. {title}\\n"
                    result += f"   📍 {source}\\n"
                    
                    if description:
                        # Truncate description
                        desc = description[:100] + "..." if len(description) > 100 else description
                        result += f"   📝 {desc}\\n"
                    
                    result += "\\n"
                
                return result
            else:
                return f"No {category} news available."
                
        except Exception as e:
            self.logger.error(f"Category news error: {e}")
            return f"Error fetching {category} news."
    
    def search_news(self, topic):
        """Search for news on specific topic"""
        try:
            if self.newsapi:
                # Use NewsAPI client
                news = self.newsapi.get_everything(
                    q=topic,
                    sort_by='relevancy',
                    page_size=6,
                    language='en',
                    from_param=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                )
                articles = news.get('articles', [])
            else:
                # Use direct API call
                articles = self.search_everything_direct(topic)
            
            if articles:
                result = f"📰 News about '{topic}' ({len(articles)} articles):\\n\\n"
                
                for i, article in enumerate(articles, 1):
                    title = article.get('title', 'No title')
                    source = article.get('source', {}).get('name', 'Unknown source')
                    published = self.format_publish_date(article.get('publishedAt', ''))
                    description = article.get('description', '')
                    url = article.get('url', '')
                    
                    result += f"{i}. {title}\\n"
                    result += f"   📍 {source} | 🕒 {published}\\n"
                    
                    if description:
                        desc = description[:120] + "..." if len(description) > 120 else description
                        result += f"   📝 {desc}\\n"
                    
                    result += "\\n"
                
                return result
            else:
                return f"No recent news found about '{topic}'"
                
        except Exception as e:
            self.logger.error(f"News search error: {e}")
            return f"Error searching for news about '{topic}'"
    
    def fetch_headlines_direct(self, country="us"):
        """Fetch headlines using direct API call"""
        if not self.api_key:
            return []
        
        url = f"{self.base_url}/top-headlines"
        params = {
            'apiKey': self.api_key,
            'country': country,
            'pageSize': 8
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('articles', [])
        else:
            raise Exception(f"API returned status code {response.status_code}")
    
    def fetch_category_direct(self, category):
        """Fetch category news using direct API call"""
        if not self.api_key:
            return []
        
        url = f"{self.base_url}/top-headlines"
        params = {
            'apiKey': self.api_key,
            'category': category,
            'country': 'us',
            'pageSize': 6
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('articles', [])
        else:
            raise Exception(f"API returned status code {response.status_code}")
    
    def search_everything_direct(self, topic):
        """Search everything using direct API call"""
        if not self.api_key:
            return []
        
        url = f"{self.base_url}/everything"
        params = {
            'apiKey': self.api_key,
            'q': topic,
            'sortBy': 'relevancy',
            'pageSize': 6,
            'language': 'en',
            'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('articles', [])
        else:
            raise Exception(f"API returned status code {response.status_code}")
    
    def format_publish_date(self, date_string):
        """Format publication date to readable format"""
        try:
            if not date_string:
                return "Unknown time"
            
            # Parse ISO format
            date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            now = datetime.now(date_obj.tzinfo)
            
            # Calculate time difference
            time_diff = now - date_obj
            
            if time_diff.days > 0:
                return f"{time_diff.days}d ago"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                return f"{hours}h ago"
            elif time_diff.seconds > 60:
                minutes = time_diff.seconds // 60
                return f"{minutes}m ago"
            else:
                return "Just now"
                
        except Exception:
            return "Unknown time"
    
    def get_news_sources(self):
        """Get available news sources"""
        try:
            if self.newsapi:
                sources = self.newsapi.get_sources()
                source_list = sources.get('sources', [])
            else:
                source_list = self.fetch_sources_direct()
            
            if source_list:
                result = f"Available news sources ({len(source_list)}):\\n\\n"
                
                # Group by category
                categories = {}
                for source in source_list[:20]:  # Limit to 20 sources
                    category = source.get('category', 'general').title()
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(source.get('name', 'Unknown'))
                
                for category, sources in categories.items():
                    result += f"📂 {category}: {', '.join(sources)}\\n"
                
                return result
            else:
                return "No sources available."
                
        except Exception as e:
            self.logger.error(f"Sources error: {e}")
            return "Error fetching news sources."
    
    def fetch_sources_direct(self):
        """Fetch sources using direct API call"""
        if not self.api_key:
            return []
        
        url = f"{self.base_url}/sources"
        params = {
            'apiKey': self.api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('sources', [])
        else:
            return []

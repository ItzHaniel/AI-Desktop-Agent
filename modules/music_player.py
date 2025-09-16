#!/usr/bin/env python3
"""
Music Player - Enhanced with Desktop App Integration, Auto-Play, and YT-DLP Streaming
"""

import pygame
import webbrowser
import os
import subprocess
import time
import tempfile
import threading
from pathlib import Path
from urllib.parse import quote_plus
from utils.logger import setup_logger

# YT-DLP integration for streaming
try:
    from yt_dlp import YoutubeDL
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False

# Browser automation for auto-play (optional)
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Optional: Spotify API integration
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    SPOTIFY_AVAILABLE = True
except ImportError:
    SPOTIFY_AVAILABLE = False

class MusicPlayer:
    def __init__(self):
        self.logger = setup_logger()
        
        # Initialize pygame mixer for local playback
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.pygame_available = True
        except:
            self.pygame_available = False
        
        # Music state
        self.current_song = None
        self.is_playing = False
        self.is_paused = False
        self.current_stream_file = None
        
        # Setup Spotify API if available
        if SPOTIFY_AVAILABLE:
            self.setup_spotify()
        else:
            self.spotify = None
            
        # Check for installed apps
        self.detect_installed_apps()
        
        print("🎵 Enhanced Music Player initialized!")
        if SELENIUM_AVAILABLE:
            print("🤖 Auto-play functionality enabled!")
        if YTDLP_AVAILABLE:
            print("🎧 YT-DLP streaming enabled!")
        
    def setup_spotify(self):
        """Initialize Spotify client"""
        try:
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            
            if client_id and client_secret:
                credentials = SpotifyClientCredentials(
                    client_id=client_id,
                    client_secret=client_secret
                )
                self.spotify = spotipy.Spotify(client_credentials_manager=credentials)
                print("✅ Spotify API integration enabled!")
            else:
                self.spotify = None
        except Exception as e:
            self.logger.error(f"Spotify setup error: {e}")
            self.spotify = None
    
    def detect_installed_apps(self):
        """Detect installed music apps"""
        self.apps = {
            'spotify_installed': False,
            'youtube_music_installed': False
        }
        
        # Check for Spotify desktop app
        spotify_paths = [
            os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"),  # Windows
            "/Applications/Spotify.app",  # macOS  
            "/usr/bin/spotify",  # Linux
            "/snap/bin/spotify"  # Linux Snap
        ]
        
        for path in spotify_paths:
            if os.path.exists(path):
                self.apps['spotify_installed'] = True
                self.spotify_path = path
                print("✅ Spotify desktop app detected!")
                break
        
        # Check for YouTube Music app (Windows/Chrome app)
        ytmusic_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            "/Applications/YouTube Music.app"
        ]
        
        for path in ytmusic_paths:
            if os.path.exists(path):
                self.apps['youtube_music_installed'] = True
                print("✅ YouTube Music capability detected!")
                break
    
    def handle_music_request(self, command):
        """Enhanced music request handling"""
        command = command.lower()
        
        if "stop" in command:
            return self.stop_music()
        elif "pause" in command:
            return self.pause_music()
        elif "resume" in command:
            return self.resume_music()
        elif "local" in command:
            return self.play_local_music()
        else:
            song_name = self.extract_song_name(command)
            return self.play_music_smart(song_name)
    
    def extract_song_name(self, command):
        """Extract song name from voice command"""
        words_to_remove = ["play", "music", "song", "some", "the", "a", "open", "start"]
        words = command.split()
        song_words = [word for word in words if word not in words_to_remove]
        return " ".join(song_words) if song_words else "popular music"
    
    def play_music_smart(self, song_name):
        """Smart music playing with multiple fallbacks"""
        try:
            print(f"🎵 Searching for: '{song_name}'")
            
            # Priority 1: Spotify Desktop App with API
            if self.apps['spotify_installed'] and self.spotify:
                result = self.play_spotify_desktop_with_api(song_name)
                if result:
                    return result
            
            # Priority 2: Spotify Desktop App (manual)
            elif self.apps['spotify_installed']:
                result = self.play_spotify_desktop(song_name)
                if result:
                    return result
            
            # Priority 3: Auto-play Spotify Web
            if SELENIUM_AVAILABLE:
                result = self.autoplay_spotify_web(song_name)
                if result:
                    return result
            
            # Priority 4: Auto-play YouTube
            if SELENIUM_AVAILABLE:
                result = self.autoplay_youtube(song_name)
                if result:
                    return result
            
            # Priority 5: YT-DLP Streaming (NEW!)
            if YTDLP_AVAILABLE:
                result = self.stream_with_ytdlp(song_name)
                if result:
                    return result
            
            # Fallback: Manual web browsers
            return self.play_web_fallback(song_name)
            
        except Exception as e:
            self.logger.error(f"Smart music play error: {e}")
            return f"Error playing '{song_name}'. Check your internet connection."
    
    def stream_with_ytdlp(self, song_name):
        """Stream audio using YT-DLP without downloading files"""
        if not YTDLP_AVAILABLE or not self.pygame_available:
            return None
            
        try:
            print("🎧 Streaming with YT-DLP...")
            
            # Search for the song on YouTube
            search_result = self.search_youtube(song_name)
            if not search_result:
                return None
            
            # Get streaming URL
            stream_url = self.get_stream_url(search_result['url'])
            if not stream_url:
                return None
            
            # Stream and play the audio
            return self.play_stream(stream_url, search_result['title'])
            
        except Exception as e:
            self.logger.error(f"YT-DLP streaming error: {e}")
            return None
    
    def search_youtube(self, query):
        """Search YouTube and return first result info"""
        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "quiet": True,
                "noplaylist": True,
                "default_search": "ytsearch1:",
                "extract_flat": False,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=False)
                
                if info and 'entries' in info and len(info['entries']) > 0:
                    entry = info['entries'][0]
                    return {
                        'url': entry.get('webpage_url', ''),
                        'title': entry.get('title', 'Unknown'),
                        'duration': entry.get('duration', 0),
                        'uploader': entry.get('uploader', 'Unknown')
                    }
                    
        except Exception as e:
            self.logger.error(f"YouTube search error: {e}")
            
        return None
    
    def get_stream_url(self, youtube_url):
        """Get direct streaming URL from YouTube video"""
        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "quiet": True,
                "noplaylist": True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                
                # Get the direct URL for the best audio format
                if 'url' in info:
                    return info['url']
                elif 'formats' in info:
                    # Find best audio format
                    audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none']
                    if audio_formats:
                        # Sort by quality and get the best
                        audio_formats.sort(key=lambda x: x.get('abr', 0), reverse=True)
                        return audio_formats[0]['url']
                        
        except Exception as e:
            self.logger.error(f"Stream URL extraction error: {e}")
            
        return None
    
    def play_stream(self, stream_url, title):
        """Play audio stream using pygame"""
        try:
            # Stop any currently playing music
            if self.is_playing:
                pygame.mixer.music.stop()
            
            # Create a temporary file for the stream
            # We'll stream it in chunks to avoid downloading the whole file
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            self.current_stream_file = temp_file.name
            temp_file.close()
            
            # Start streaming in a separate thread
            stream_thread = threading.Thread(
                target=self.stream_to_file, 
                args=(stream_url, self.current_stream_file)
            )
            stream_thread.daemon = True
            stream_thread.start()
            
            # Wait a bit for initial buffering
            time.sleep(3)
            
            # Start playing
            pygame.mixer.music.load(self.current_stream_file)
            pygame.mixer.music.play()
            
            self.current_song = title
            self.is_playing = True
            self.is_paused = False
            
            return f"🎧 Now streaming: '{title}'"
            
        except Exception as e:
            self.logger.error(f"Stream playback error: {e}")
            return None
    
    def stream_to_file(self, stream_url, temp_file):
        """Stream audio data to temporary file in chunks"""
        try:
            import urllib.request
            
            # Open the stream
            response = urllib.request.urlopen(stream_url)
            
            # Stream in 64KB chunks
            chunk_size = 65536
            with open(temp_file, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    
        except Exception as e:
            self.logger.error(f"Streaming error: {e}")
    
    def cleanup_stream_file(self):
        """Clean up temporary stream file"""
        if self.current_stream_file and os.path.exists(self.current_stream_file):
            try:
                os.unlink(self.current_stream_file)
                self.current_stream_file = None
            except:
                pass
    
    def play_spotify_desktop_with_api(self, song_name):
        """Play via Spotify desktop app using API"""
        try:
            print("🚀 Opening Spotify desktop app with API...")
            
            # Search for track
            results = self.spotify.search(q=song_name, limit=1, type='track')
            
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                track_uri = track['uri']  # spotify:track:xxxxx
                track_name = track['name']
                artist_name = track['artists'][0]['name']
                
                # Open Spotify desktop app with specific track
                spotify_uri_url = f"spotify://track/{track['id']}"
                
                # Try opening with URI first
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(spotify_uri_url)
                    else:  # macOS/Linux
                        subprocess.run(['open', spotify_uri_url])
                    
                    return f"🎵 Opening '{track_name}' by {artist_name} in Spotify app!"
                except:
                    # Fallback to launching Spotify normally
                    return self.play_spotify_desktop(song_name)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Spotify desktop API error: {e}")
            return None
    
    def play_spotify_desktop(self, song_name):
        """Launch Spotify desktop app and search"""
        try:
            print("🚀 Launching Spotify desktop app...")
            
            # Launch Spotify app
            if os.name == 'nt':  # Windows
                subprocess.Popen([self.spotify_path])
            else:  # macOS/Linux
                subprocess.Popen(['open', '-a', 'Spotify'])
            
            # Wait for app to load
            time.sleep(3)
            
            # Use automation to search (requires pyautogui)
            try:
                import pyautogui
                
                # Focus on Spotify window and search
                pyautogui.hotkey('ctrl', 'l')  # Focus search bar
                time.sleep(0.5)
                pyautogui.write(song_name)  # Type song name
                time.sleep(0.5)
                pyautogui.press('enter')  # Search
                time.sleep(1)
                pyautogui.press('enter')  # Play first result
                
                return f"🎵 Playing '{song_name}' in Spotify desktop app!"
                
            except ImportError:
                return f"🎵 Spotify app opened. Please search for '{song_name}' manually."
                
        except Exception as e:
            self.logger.error(f"Spotify desktop launch error: {e}")
            return None
    
    def autoplay_spotify_web(self, song_name):
        """Auto-play first result on Spotify Web using Selenium"""
        if not SELENIUM_AVAILABLE:
            return None
            
        try:
            print("🤖 Auto-playing Spotify web...")
            
            # Setup Chrome options for better performance
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Launch browser
            driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate to Spotify
            search_url = f"https://open.spotify.com/search/{quote_plus(song_name)}"
            driver.get(search_url)
            
            # Wait for page to load and find first result
            wait = WebDriverWait(driver, 10)
            
            # Look for the first track result and click it
            try:
                # Wait for search results to appear
                first_track = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tracklist-row"]'))
                )
                
                # Click the first track
                first_track.click()
                time.sleep(2)
                
                # Try to find and click play button
                try:
                    play_button = driver.find_element(By.CSS_SELECTOR, '[data-testid="control-button-playpause"]')
                    play_button.click()
                    
                    # Get track name if possible
                    try:
                        track_element = driver.find_element(By.CSS_SELECTOR, '[data-testid="entityTitle"]')
                        actual_track = track_element.text
                        return f"🎵 Auto-playing '{actual_track}' on Spotify Web!"
                    except:
                        return f"🎵 Auto-playing '{song_name}' on Spotify Web!"
                        
                except:
                    return f"🎵 Opened '{song_name}' on Spotify Web - click play button!"
                    
            except Exception as e:
                self.logger.error(f"Spotify web automation error: {e}")
                return f"🎵 Opened Spotify search for '{song_name}'"
                
        except Exception as e:
            self.logger.error(f"Spotify web autoplay error: {e}")
            return None
    
    def autoplay_youtube(self, song_name):
        """Auto-play first YouTube result using Selenium"""
        if not SELENIUM_AVAILABLE:
            return None
            
        try:
            print("🤖 Auto-playing YouTube...")
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate to YouTube search
            search_query = quote_plus(song_name + " music")
            youtube_url = f"https://www.youtube.com/results?search_query={search_query}"
            driver.get(youtube_url)
            
            # Wait for results and click first video
            wait = WebDriverWait(driver, 10)
            
            try:
                # Find first video result
                first_video = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a#video-title'))
                )
                
                video_title = first_video.get_attribute('title')
                first_video.click()
                
                # Wait for video to start playing
                time.sleep(3)
                
                return f"🎵 Auto-playing '{video_title}' on YouTube!"
                
            except Exception as e:
                self.logger.error(f"YouTube automation error: {e}")
                return f"🎵 Opened YouTube search for '{song_name}'"
                
        except Exception as e:
            self.logger.error(f"YouTube autoplay error: {e}")
            return None
    
    def play_web_fallback(self, song_name):
        """Fallback to manual web browsers"""
        try:
            # Try Spotify web first
            spotify_url = f"https://open.spotify.com/search/{quote_plus(song_name)}"
            webbrowser.open(spotify_url)
            
            return f"🎵 Opened Spotify search for '{song_name}' - click the first result!"
            
        except Exception as e:
            # Ultimate fallback to YouTube
            youtube_url = f"https://www.youtube.com/results?search_query={quote_plus(song_name + ' music')}"
            webbrowser.open(youtube_url)
            
            return f"🎵 Opened YouTube search for '{song_name}' - click the first result!"
    
    def play_local_music(self):
        """Play local music files"""
        if not self.pygame_available:
            return "❌ Local music playback not available"
            
        try:
            music_files = self.find_local_music()
            
            if not music_files:
                return "No local music files found"
            
            # Play random song
            import random
            song_file = random.choice(music_files)
            
            pygame.mixer.music.load(str(song_file))
            pygame.mixer.music.play()
            
            self.current_song = song_file
            self.is_playing = True
            
            return f"🎵 Playing locally: {song_file.stem}"
            
        except Exception as e:
            return f"Error playing local music: {e}"
    
    def find_local_music(self):
        """Find local music files"""
        music_paths = [
            Path.home() / "Music",
            Path.home() / "Downloads"
        ]
        
        supported_formats = [".mp3", ".wav", ".ogg", ".m4a"]
        music_files = []
        
        for music_path in music_paths:
            if music_path.exists():
                for format in supported_formats:
                    music_files.extend(list(music_path.glob(f"**/*{format}")))
        
        return music_files
    
    def stop_music(self):
        """Stop music"""
        try:
            if self.pygame_available:
                pygame.mixer.music.stop()
            
            # Clean up stream file
            self.cleanup_stream_file()
            
            self.is_playing = False
            self.is_paused = False
            return "🛑 Music stopped (local/stream). For web/app music, use the app controls."
        except:
            return "No local music to stop."
    
    def pause_music(self):
        """Pause music"""
        try:
            if self.pygame_available and self.is_playing and not self.is_paused:
                pygame.mixer.music.pause()
                self.is_paused = True
                return "⏸️ Music paused."
            else:
                return "No music playing to pause."
        except:
            return "Error pausing music."
    
    def resume_music(self):
        """Resume paused music"""
        try:
            if self.pygame_available and self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
                return "▶️ Music resumed."
            else:
                return "No paused music to resume."
        except:
            return "Error resuming music."
    
    def get_installation_help(self):
        """Get help for enabling enhanced features"""
        help_text = """
🤖 ENHANCED MUSIC FEATURES SETUP

🎧 For YT-DLP Streaming (NEW!):
   pip install yt-dlp
   
   This enables streaming without downloads!

🔧 For Auto-Play Functionality:
   pip install selenium
   
   Then download ChromeDriver:
   https://chromedriver.chromium.org/
   
🚀 For Desktop App Integration:
   pip install pyautogui
   
📱 Install Apps:
   • Spotify Desktop: https://spotify.com/download
   • YouTube Music: Use Chrome browser
   
⚡ With these installed, Jarvis will:
   • Stream music directly from YouTube
   • Auto-click play buttons
   • Open desktop apps directly
   • Play the first search result automatically
        """
        return help_text
    
    def get_status(self):
        """Get current music player status"""
        return {
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'current_song': str(self.current_song) if self.current_song else None,
            'pygame_available': self.pygame_available,
            'ytdlp_available': YTDLP_AVAILABLE,
            'selenium_available': SELENIUM_AVAILABLE,
            'spotify_available': SPOTIFY_AVAILABLE,
            'apps_detected': self.apps
        }
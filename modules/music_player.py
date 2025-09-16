#!/usr/bin/env python3
"""
Fixed Visual Music Player - Resolves threading and pygame issues
"""

import pygame
import os
import subprocess
import time
import threading
import math
import json
import openai
from pathlib import Path
from urllib.parse import quote_plus
from utils.logger import setup_logger

# YT-DLP integration
try:
    from yt_dlp import YoutubeDL
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False

class MusicPlayer:
    def __init__(self, width=500, height=350):
        self.logger = setup_logger()
        
        # Music state - initialize BEFORE pygame
        self.current_song = None
        self.current_artist = None
        self.is_playing = False
        self.is_paused = False
        self.current_stream_file = None
        self.loading = False
        self.status_message = "Ready to rock!"
        self.progress = 0.0
        
        # Window settings
        self.width = width
        self.height = height
        self.screen = None
        self.window_open = False
        self.running = False
        self.minimized = False
        
        # Colors - Enhanced Dark futuristic theme
        self.colors = {
            'bg': (8, 8, 15),
            'panel': (20, 25, 35),
            'accent': (0, 200, 255),
            'accent_dim': (0, 120, 180),
            'accent_glow': (100, 220, 255),
            'text': (240, 240, 240),
            'text_dim': (160, 160, 160),
            'success': (0, 255, 150),
            'warning': (255, 200, 0),
            'error': (255, 100, 100),
            'particle': (0, 255, 200),
        }
        
        # Animation variables
        self.pulse_time = 0
        self.wave_offset = 0
        self.particle_systems = []
        self.glow_intensity = 0
        
        # Create temp music folder
        self.temp_music_dir = Path("temp_music")
        self.temp_music_dir.mkdir(exist_ok=True)
        
        # Initialize Groq BEFORE pygame
        self.setup_groq()
        
        # Initialize pygame mixer ONLY (no display yet)
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            print("Audio system initialized!")
        except Exception as e:
            print(f"Audio init error: {e}")
        
        # UI Elements (will be created when window opens)
        self.buttons = {}
        
        print(" Music Player initialized!")
        if YTDLP_AVAILABLE:
            print("YT-DLP streaming enabled!")
        if hasattr(self, 'groq_client') and self.groq_client:
            print("Groq AI music processing enabled!")
    
    def setup_groq(self):
        """Setup Groq AI for intelligent music request processing"""
        groq_api_key = os.getenv('GROQ_API_KEY')
        
        if groq_api_key:
            try:
                self.groq_client = openai.OpenAI(
                    api_key=groq_api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                self.groq_model = "llama-3.1-8b-instant"
                print("Groq AI connected!")
            except Exception as e:
                self.logger.error(f"Groq setup error: {e}")
                self.groq_client = None
        else:
            self.groq_client = None
            print("GROQ_API_KEY not found. Using basic parsing.")
    
    def create_window(self):
        """Create the pygame window - MUST be called from main thread"""
        if self.window_open:
            return True
            
        try:
            # Initialize pygame display
            pygame.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Specter Music Player")
            
            # Initialize fonts
            self.font_large = pygame.font.Font(None, 36)
            self.font_medium = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 18)
            
            # Create UI elements
            self.buttons = self.create_buttons()
            
            self.window_open = True
            self.running = True
            
            print("Music player window created!")
            return True
            
        except Exception as e:
            print(f"Window creation error: {e}")
            self.logger.error(f"Window creation error: {e}")
            return False
    
    def create_buttons(self):
        """Create UI buttons"""
        button_width = 80
        button_height = 35
        spacing = 15
        start_y = self.height - 50
        
        total_width = (button_width * 3) + (spacing * 2)
        start_x = (self.width - total_width) // 2
        
        return {
            'play_pause': pygame.Rect(start_x, start_y, button_width, button_height),
            'stop': pygame.Rect(start_x + button_width + spacing, start_y, button_width, button_height),
            'minimize': pygame.Rect(start_x + (button_width + spacing) * 2, start_y, button_width, button_height)
        }
    
    def process_music_request_with_ai(self, user_input):
        """Use Groq AI to process music requests"""
        if not hasattr(self, 'groq_client') or not self.groq_client:
            return self.extract_song_name(user_input)
        
        try:
            system_prompt = """Extract song and artist from music requests. Return JSON only:
            {"song": "song_name", "artist": "artist_name", "action": "play/pause/stop/resume", "search_query": "optimized_search"}
            
            Examples:
            "play metallica" -> {"song": "", "artist": "metallica", "action": "play", "search_query": "metallica best songs"}
            "play bohemian rhapsody" -> {"song": "bohemian rhapsody", "artist": "", "action": "play", "search_query": "bohemian rhapsody queen"}
            "pause music" -> {"song": "", "artist": "", "action": "pause", "search_query": ""}"""
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                model=self.groq_model,
                max_tokens=200,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            try:
                parsed = json.loads(ai_response)
                return parsed
            except json.JSONDecodeError:
                return {"action": "play", "search_query": self.extract_song_name(user_input)}
                
        except Exception as e:
            self.logger.error(f"Groq processing error: {e}")
            return {"action": "play", "search_query": self.extract_song_name(user_input)}
    
    def extract_song_name(self, command):
        """Basic song name extraction"""
        words_to_remove = ["play", "music", "song", "some", "the", "a", "open", "start"]
        words = command.lower().split()
        song_words = [word for word in words if word not in words_to_remove]
        return " ".join(song_words) if song_words else "popular music"
    
    def handle_music_request(self, command):
        """Handle music request - safe for any thread"""
        if not command:
            return "Please provide a music request!"
        
        print(f"🎵 Processing: {command}")
        
        # Process with AI or fallback
        if hasattr(self, 'groq_client') and self.groq_client:
            request_data = self.process_music_request_with_ai(command)
            action = request_data.get("action", "play")
            search_query = request_data.get("search_query", command)
            print(f"AI processed: {request_data}")
        else:
            command_lower = command.lower()
            if "stop" in command_lower:
                action = "stop"
                search_query = ""
            elif "pause" in command_lower:
                action = "pause"
                search_query = ""
            elif "resume" in command_lower:
                action = "resume" 
                search_query = ""
            else:
                action = "play"
                search_query = self.extract_song_name(command)
        
        # Execute action
        if action == "stop":
            return self.stop_music()
        elif action == "pause":
            return self.pause_music()
        elif action == "resume":
            return self.resume_music()
        elif action == "play":
            if search_query:
                return self.play_music_smart(search_query)
            else:
                return "What would you like me to play?"
        
        return f"Processed: {action}"
    
    def play_music_smart(self, song_name):
        """Start music download and playback"""
        if not YTDLP_AVAILABLE:
            return "YT-DLP not installed. Run: pip install yt-dlp"
        
        self.loading = True
        self.status_message = f"Searching: {song_name}"
        
        # Start download in background thread
        download_thread = threading.Thread(target=self._download_and_play_thread, args=(song_name,))
        download_thread.daemon = True
        download_thread.start()
        
        return f"Searching for '{song_name}'..."
    
    def _download_and_play_thread(self, song_name):
        """Background download thread - does NOT touch pygame"""
        try:
            print("Searching YouTube...")
            self.status_message = "Searching YouTube..."
            
            search_result = self.search_youtube(song_name)
            if not search_result:
                self.status_message = "No results found"
                self.loading = False
                return
            
            print(f"Downloading: {search_result['title']}")
            self.status_message = f"Downloading: {search_result['title'][:40]}..."
            
            success = self.download_audio(search_result['url'], search_result['title'])
            
            if success:
                self.current_song = search_result['title']
                self.current_artist = search_result.get('uploader', 'Unknown')
                self.status_message = f"♪ Playing: {self.current_song[:40]}"
                self.is_playing = True
                self.is_paused = False
                self.glow_intensity = 1.0
                
                print(f"Now playing: {self.current_song}")
            else:
                self.status_message = "Download failed"
                
        except Exception as e:
            print(f"Download error: {e}")
            self.status_message = f"Error: {str(e)[:30]}"
            self.logger.error(f"Download error: {e}")
        finally:
            self.loading = False
    
    def search_youtube(self, query):
        """Search YouTube"""
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "default_search": "ytsearch1:",
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
    
    def download_audio(self, youtube_url, title):
        """Download and play audio"""
        try:
            self.cleanup_stream_file()
            
            # Create safe filename
            import hashlib
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:50]
            file_hash = hashlib.md5(youtube_url.encode()).hexdigest()[:8]
            temp_filename = f"{safe_title}_{file_hash}"
            temp_filepath = self.temp_music_dir / temp_filename
            
            # Download
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(temp_filepath.with_suffix('.%(ext)s')),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',
                }],
                'quiet': True,
                'no_warnings': True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            
            # Find and play file
            for ext in ['.mp3', '.m4a', '.webm', '.opus']:
                potential_file = temp_filepath.with_suffix(ext)
                if potential_file.exists():
                    if ext != '.mp3':
                        final_file = temp_filepath.with_suffix('.mp3')
                        potential_file.rename(final_file)
                        self.current_stream_file = final_file
                    else:
                        self.current_stream_file = potential_file
                    
                    # Play music
                    pygame.mixer.music.load(str(self.current_stream_file))
                    pygame.mixer.music.play()
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Download error: {e}")
            return False
    
    def stop_music(self):
        """Stop music"""
        pygame.mixer.music.stop()
        self.cleanup_stream_file()
        self.is_playing = False
        self.is_paused = False
        self.current_song = None
        self.current_artist = None
        self.status_message = "Stopped"
        self.glow_intensity = 0
        return "Music stopped"
    
    def pause_music(self):
        """Pause music"""
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.status_message = "Paused"
            return "Music paused"
        return "Nothing to pause"
    
    def resume_music(self):
        """Resume music"""
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.status_message = f"♪ Playing: {self.current_song}" if self.current_song else "♪ Playing"
            return "Music resumed"
        return "Nothing to resume"
    
    def cleanup_stream_file(self):
        """Clean up temp files"""
        if self.current_stream_file and Path(self.current_stream_file).exists():
            try:
                Path(self.current_stream_file).unlink()
                self.current_stream_file = None
            except:
                pass
    
    def handle_events(self):
        """Handle pygame events - ONLY call from main thread"""
        if not self.window_open:
            return True
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                if self.buttons['play_pause'].collidepoint(mouse_pos):
                    if self.is_paused:
                        self.resume_music()
                    elif self.is_playing:
                        self.pause_music()
                
                elif self.buttons['stop'].collidepoint(mouse_pos):
                    self.stop_music()
                
                elif self.buttons['minimize'].collidepoint(mouse_pos):
                    self.minimized = not self.minimized
        
        return True
    
    def update_animations(self):
        """Update animations"""
        self.pulse_time += 0.08
        self.wave_offset += 0.03
        
        if self.is_playing and not self.is_paused:
            self.glow_intensity = min(1.0, self.glow_intensity + 0.02)
            self.add_particles()
        else:
            self.glow_intensity = max(0.0, self.glow_intensity - 0.05)
        
        # Update particles
        self.particle_systems = [p for p in self.particle_systems if p['life'] > 0]
        for particle in self.particle_systems:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['vy'] += 0.05
            particle['vx'] *= 0.99
    
    def add_particles(self):
        """Add particle effects"""
        if len(self.particle_systems) < 50:
            import random
            
            for _ in range(2):
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(50, 150)
                
                self.particle_systems.append({
                    'x': self.width // 2 + math.cos(angle) * radius,
                    'y': self.height // 2 + math.sin(angle) * radius,
                    'vx': random.uniform(-1, 1),
                    'vy': random.uniform(-2, 0),
                    'life': random.randint(60, 120),
                    'max_life': 120,
                    'size': random.uniform(1, 3),
                    'color': random.choice([self.colors['accent'], self.colors['success'], self.colors['particle']])
                })
    
    def draw_background(self):
        """Draw background"""
        # Gradient
        for y in range(self.height):
            color_factor = y / self.height
            r = int(self.colors['bg'][0] * (1 + color_factor * 0.3))
            g = int(self.colors['bg'][1] * (1 + color_factor * 0.3))
            b = int(self.colors['bg'][2] * (1 + color_factor * 0.5))
            pygame.draw.line(self.screen, (min(r, 30), min(g, 30), min(b, 50)), (0, y), (self.width, y))
        
        # Wave lines
        for i in range(8):
            points = []
            for x in range(0, self.width, 10):
                y = self.height // 2 + math.sin((x * 0.01) + self.wave_offset + i * 0.3) * (20 + i * 5)
                points.append((x, int(y)))
            
            if len(points) > 1:
                pygame.draw.lines(self.screen, self.colors['accent_dim'], False, points, 2)
    
    def draw_main_panel(self):
        """Draw main panel"""
        if self.minimized:
            return
            
        # Panel
        panel_rect = pygame.Rect(20, 20, self.width - 40, self.height - 80)
        pygame.draw.rect(self.screen, self.colors['panel'], panel_rect, border_radius=15)
        
        # Glow effect when playing
        if self.is_playing and not self.is_paused and self.glow_intensity > 0:
            for i in range(3):
                glow_rect = panel_rect.inflate(i * 2, i * 2)
                pygame.draw.rect(self.screen, self.colors['accent_dim'], glow_rect, 1, border_radius=15)
        
        pygame.draw.rect(self.screen, self.colors['accent_dim'], panel_rect, 2, border_radius=15)
        
        # Title
        title_surface = self.font_medium.render("SPECTER MUSIC PLAYER", True, self.colors['accent'])
        title_rect = title_surface.get_rect(center=(self.width // 2, 45))
        self.screen.blit(title_surface, title_rect)
        
        # Song info
        if self.current_song:
            song_title = self.current_song[:50] + "..." if len(self.current_song) > 50 else self.current_song
            song_surface = self.font_large.render(song_title, True, self.colors['text'])
            song_rect = song_surface.get_rect(center=(self.width // 2, 120))
            self.screen.blit(song_surface, song_rect)
            
            if self.current_artist:
                artist_surface = self.font_medium.render(f"by {self.current_artist}", True, self.colors['text_dim'])
                artist_rect = artist_surface.get_rect(center=(self.width // 2, 150))
                self.screen.blit(artist_surface, artist_rect)
        else:
            no_song_surface = self.font_large.render("No Song Playing", True, self.colors['text_dim'])
            no_song_rect = no_song_surface.get_rect(center=(self.width // 2, 120))
            self.screen.blit(no_song_surface, no_song_rect)
        
        # Status
        status_color = self.colors['success'] if self.is_playing else self.colors['text_dim']
        status_surface = self.font_small.render(self.status_message, True, status_color)
        status_rect = status_surface.get_rect(center=(self.width // 2, 200))
        self.screen.blit(status_surface, status_rect)
        
        # Loading animation
        if self.loading:
            loading_text = "Loading" + "." * ((int(self.pulse_time * 5) % 4))
            loading_surface = self.font_medium.render(loading_text, True, self.colors['warning'])
            loading_rect = loading_surface.get_rect(center=(self.width // 2, 230))
            self.screen.blit(loading_surface, loading_rect)
    
    def draw_visualizer(self):
        """Draw audio visualizer"""
        if not (self.is_playing and not self.is_paused):
            return
        
        import random
        
        center_x, center_y = self.width // 2, 270
        radius = 60
        num_bars = 24
        
        for i in range(num_bars):
            angle = (i / num_bars) * 2 * math.pi
            height = random.randint(5, 20) + int(8 * math.sin(self.pulse_time + i * 0.2))
            
            inner_x = center_x + math.cos(angle) * radius
            inner_y = center_y + math.sin(angle) * radius
            outer_x = center_x + math.cos(angle) * (radius + height)
            outer_y = center_y + math.sin(angle) * (radius + height)
            
            intensity = height / 28.0
            color = (
                int(self.colors['accent'][0] * intensity),
                int(self.colors['accent'][1] * intensity), 
                int(255 * intensity)
            )
            
            pygame.draw.line(self.screen, color, (int(inner_x), int(inner_y)), 
                           (int(outer_x), int(outer_y)), 3)
    
    def draw_particles(self):
        """Draw particles"""
        for particle in self.particle_systems:
            if particle['life'] > 0:
                age_factor = particle['life'] / particle.get('max_life', 120)
                size = max(1, int(particle.get('size', 2) * age_factor))
                
                pygame.draw.circle(self.screen, particle['color'], 
                                 (int(particle['x']), int(particle['y'])), size)
    
    def draw_buttons(self):
        """Draw control buttons"""
        if self.minimized:
            return
            
        button_texts = {
            'play_pause': 'PAUSE' if (self.is_playing and not self.is_paused) else '▶️ PLAY',
            'stop': 'STOP',
            'minimize': 'MIN'
        }
        
        for button_name, rect in self.buttons.items():
            if button_name == 'play_pause' and self.is_playing:
                button_color = self.colors['accent']
            elif button_name == 'stop':
                button_color = self.colors['error']
            else:
                button_color = self.colors['panel']
            
            pygame.draw.rect(self.screen, button_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, self.colors['accent_dim'], rect, 2, border_radius=8)
            
            text_surface = self.font_small.render(button_texts[button_name], True, self.colors['text'])
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def draw_frame(self):
        """Draw complete frame - ONLY call from main thread"""
        if not self.window_open:
            return
            
        if self.minimized:
            self.screen.fill(self.colors['bg'])
            minimized_text = self.font_medium.render("🎵 Minimized - Click to restore", True, self.colors['text'])
            text_rect = minimized_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(minimized_text, text_rect)
        else:
            self.draw_background()
            self.draw_particles()
            self.draw_main_panel()
            self.draw_visualizer()
            self.draw_buttons()
        
        pygame.display.flip()
    
    def run(self):
        """Main loop - MUST run from main thread"""
        # Create window
        if not self.create_window():
            return
        
        clock = pygame.time.Clock()
        
        print("Music player is running!")
        print("Try: player.handle_music_request('play your favorite song')")
        
        try:
            while self.running:
                if not self.handle_events():
                    break
                
                self.update_animations()
                self.draw_frame()
                clock.tick(60)
                
        except Exception as e:
            print(f"Runtime error: {e}")
            self.logger.error(f"Runtime error: {e}")
        finally:
            # Cleanup
            self.cleanup_stream_file()
            if self.window_open:
                pygame.quit()
                self.window_open = False
            print("Music player closed!")

# Simple test function
def test_music_player():
    """Test the music player"""
    print("🎵 Starting Music Player Test...")
    
    # Create player
    player = MusicPlayer()
    
    # Test music request in background
    def test_request():
        time.sleep(2)  # Wait for window to open
        print("Testing music request...")
        player.handle_music_request("play the summoning by sleep token")
    
    # Start test in background
    test_thread = threading.Thread(target=test_request)
    test_thread.daemon = True
    test_thread.start()
    
    # Run main loop
    player.run()

if __name__ == "__main__":
    test_music_player()
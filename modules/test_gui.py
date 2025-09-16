#!/usr/bin/env python3
"""
Specter AI Agent - GUI Version
Modern graphical interface for your AI assistant
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import sys
import os
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))
sys.path.append(str(Path(__file__).parent / "utils"))

class SpecterGUI:
    def __init__(self):
        self.current_mode = "friend"
        self.root = tk.Tk()
        self.root.title("Specter AI Assistant")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Modern color scheme
        self.bg_color = "#1e1e2e"
        self.chat_bg = "#2d2d44"
        self.input_bg = "#3d3d5c"
        self.text_color = "#ffffff"
        self.accent_color = "#6c7ce0"
        self.success_color = "#42a5f5"
        
        self.setup_styles()
        self.setup_gui()
        self.load_modules()
        
        # Current mode
       
        
    def setup_styles(self):
        """Setup modern GUI styles"""
        self.root.configure(bg=self.bg_color)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure modern styles
        style.configure('Chat.TFrame', background=self.chat_bg)
        style.configure('Input.TFrame', background=self.input_bg)
        style.configure('Modern.TButton', 
                       background=self.accent_color,
                       foreground='white',
                       relief='flat',
                       padding=(10, 5))
        style.map('Modern.TButton',
                 background=[('active', self.success_color)])
        
    def setup_gui(self):
        """Setup the main GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="🤖 Specter AI Assistant",
                              font=("Segoe UI", 18, "bold"),
                              bg=self.bg_color,
                              fg=self.text_color)
        title_label.pack(pady=(0, 10))
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill='x', pady=(0, 10))
        
        self.status_label = tk.Label(status_frame,
                                   text="🔄 Loading modules...",
                                   font=("Segoe UI", 10),
                                   bg=self.bg_color,
                                   fg=self.success_color)
        self.status_label.pack(side='left')
        
        self.mode_label = tk.Label(status_frame,
                                 text=f"Mode: {self.current_mode}",
                                 font=("Segoe UI", 10, "bold"),
                                 bg=self.bg_color,
                                 fg=self.accent_color)
        self.mode_label.pack(side='right')
        
        # Chat area
        chat_frame = ttk.Frame(main_frame, style='Chat.TFrame')
        chat_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.chat_area = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            state='disabled',
            font=("Consolas", 11),
            bg=self.chat_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            selectbackground=self.accent_color,
            relief='flat',
            borderwidth=0,
            padx=10,
            pady=10
        )
        self.chat_area.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Input area
        input_frame = ttk.Frame(main_frame, style='Input.TFrame')
        input_frame.pack(fill='x', pady=(0, 10))
        
        self.user_input = tk.Entry(
            input_frame,
            font=("Segoe UI", 12),
            bg=self.input_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            relief='flat',
            borderwidth=0
        )
        self.user_input.pack(side='left', fill='x', expand=True, padx=(5, 10), pady=5)
        self.user_input.bind('<Return>', self.on_enter_pressed)
        self.user_input.bind('<Control-Return>', lambda e: self.user_input.insert('insert', '\n'))
        
        # Send button
        send_button = ttk.Button(
            input_frame,
            text="Send",
            style='Modern.TButton',
            command=self.send_message
        )
        send_button.pack(side='right', padx=(0, 5), pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        # Mode buttons
        ttk.Button(button_frame, text="Friend Mode", 
                  command=lambda: self.change_mode("friend"),
                  style='Modern.TButton').pack(side='left', padx=2)
        
        ttk.Button(button_frame, text="Therapist Mode", 
                  command=lambda: self.change_mode("therapist"),
                  style='Modern.TButton').pack(side='left', padx=2)
        
        ttk.Button(button_frame, text="Work Mode", 
                  command=lambda: self.change_mode("workmate"),
                  style='Modern.TButton').pack(side='left', padx=2)
        
        # Feature buttons
        ttk.Button(button_frame, text="📰 News", 
                  command=self.get_news,
                  style='Modern.TButton').pack(side='right', padx=2)
        
        ttk.Button(button_frame, text="🌤️ Weather", 
                  command=self.get_weather,
                  style='Modern.TButton').pack(side='right', padx=2)
        
        ttk.Button(button_frame, text="🎵 Music", 
                  command=self.play_music,
                  style='Modern.TButton').pack(side='right', padx=2)
        
        ttk.Button(button_frame, text="📁 Files", 
                  command=self.find_files,
                  style='Modern.TButton').pack(side='right', padx=2)
        
        # Clear button
        ttk.Button(button_frame, text="Clear Chat", 
                  command=self.clear_chat,
                  style='Modern.TButton').pack(side='right', padx=2)
        
        # Welcome message
        self.add_message("System", "🤖 Welcome to Specter AI Assistant!\nI'm loading all modules for you...")
        
    def load_modules(self):
        """Load all AI modules"""
        def load_in_background():
            self.modules = {}
            
            try:
                # Import modules
                from conversation import ConversationEngine
                self.modules['conversation'] = ConversationEngine()
                self.update_status("✅ Conversation Engine loaded")
            except Exception as e:
                self.update_status("❌ Conversation Engine failed to load")
            
            try:
                from news_fetcher import NewsFetcher
                self.modules['news'] = NewsFetcher()
                self.update_status("✅ News Engine loaded")
            except Exception as e:
                self.update_status("❌ News Engine failed to load")
            
            try:
                from weather_engine import WeatherEngine
                self.modules['weather'] = WeatherEngine()
                self.update_status("✅ Weather Engine loaded")
            except Exception as e:
                self.update_status("❌ Weather Engine failed to load")
            
            try:
                from music_engine import MusicEngine
                self.modules['music'] = MusicEngine()
                self.update_status("✅ Music Engine loaded")
            except Exception as e:
                self.update_status("❌ Music Engine failed to load")
                
            try:
                from file_manager import FileManager
                self.modules['files'] = FileManager()
                self.update_status("✅ File Manager loaded")
            except Exception as e:
                self.update_status("❌ File Manager failed to load")
            
            # Final status
            loaded_count = len(self.modules)
            self.update_status(f"🚀 Ready! {loaded_count} modules loaded")
            self.add_message("Specter", f"🎉 All systems online! {loaded_count} modules ready.\n\nYou can:\n• Chat with me normally\n• Ask for news, weather, or music\n• Find files on your system\n• Switch between different conversation modes\n\nHow can I help you today?")
        
        # Load modules in background thread
        threading.Thread(target=load_in_background, daemon=True).start()
    
    def add_message(self, sender, message):
        """Add message to chat area"""
        self.chat_area.configure(state='normal')
        
        # Color coding for different senders
        if sender == "You":
            color = "#4fc3f7"
        elif sender == "Specter":
            color = "#66bb6a"
        elif sender == "System":
            color = "#ffa726"
        else:
            color = self.text_color
        
        # Add timestamp
        timestamp = tk.datetime.now().strftime("%H:%M")
        
        self.chat_area.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        self.chat_area.insert(tk.END, f"{sender}: ", ('sender', sender.lower()))
        self.chat_area.insert(tk.END, f"{message}\n\n", 'message')
        
        # Configure tags for styling
        self.chat_area.tag_configure('timestamp', foreground='#9e9e9e', font=("Consolas", 9))
        self.chat_area.tag_configure('sender', foreground=color, font=("Consolas", 11, "bold"))
        self.chat_area.tag_configure('message', foreground=self.text_color, font=("Consolas", 11))
        
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)
    
    def update_status(self, status):
        """Update status label"""
        def update():
            self.status_label.config(text=status)
        
        self.root.after(0, update)
    
    def on_enter_pressed(self, event):
        """Handle Enter key press"""
        if event.state & 0x4:  # Ctrl+Enter
            return
        else:
            self.send_message()
            return 'break'
    
    def send_message(self):
        """Send user message"""
        message = self.user_input.get().strip()
        if not message:
            return
        
        self.user_input.delete(0, tk.END)
        self.add_message("You", message)
        
        # Process message in background
        threading.Thread(target=self.process_message, args=(message,), daemon=True).start()
    
    def process_message(self, message):
        """Process user message"""
        try:
            response = ""
            message_lower = message.lower()
            
            # Route to appropriate module
            if any(word in message_lower for word in ["news", "headlines", "article"]):
                if 'news' in self.modules:
                    response = self.modules['news'].get_news(message)
                else:
                    response = "News module not available."
                    
            elif any(word in message_lower for word in ["weather", "temperature", "forecast"]):
                if 'weather' in self.modules:
                    response = self.modules['weather'].get_weather(message)
                else:
                    response = "Weather module not available."
                    
            elif any(word in message_lower for word in ["play", "music", "song"]):
                if 'music' in self.modules:
                    response = self.modules['music'].play_music(message)
                else:
                    response = "Music module not available."
                    
            elif any(word in message_lower for word in ["find", "file", "search"]):
                if 'files' in self.modules:
                    response = self.modules['files'].find_files(message)
                else:
                    response = "File manager not available."
            else:
                # Regular conversation
                if 'conversation' in self.modules:
                    response = self.modules['conversation'].chat(message, self.current_mode)
                else:
                    response = "I'm here, but my conversation module isn't loaded yet. Try asking for news, weather, or other specific features!"
            
            # Add response to chat
            self.root.after(0, lambda: self.add_message("Specter", response))
            
        except Exception as e:
            self.root.after(0, lambda: self.add_message("System", f"Error processing message: {str(e)}"))
    
    def change_mode(self, mode):
        """Change conversation mode"""
        self.current_mode = mode
        self.mode_label.config(text=f"Mode: {mode}")
        self.add_message("System", f"🔄 Switched to {mode} mode")
    
    def get_news(self):
        """Get latest news"""
        self.user_input.delete(0, tk.END)
        self.user_input.insert(0, "Get me the latest headlines")
        self.send_message()
    
    def get_weather(self):
        """Get weather information"""
        self.user_input.delete(0, tk.END)
        self.user_input.insert(0, "What's the weather like?")
        self.send_message()
    
    def play_music(self):
        """Play music"""
        self.user_input.delete(0, tk.END)
        self.user_input.insert(0, "Play some music")
        self.send_message()
    
    def find_files(self):
        """Find files"""
        self.user_input.delete(0, tk.END)
        self.user_input.insert(0, "Help me find files")
        self.send_message()
    
    def clear_chat(self):
        """Clear chat area"""
        self.chat_area.configure(state='normal')
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.configure(state='disabled')
        self.add_message("System", "Chat cleared! How can I help you?")
    
    def run(self):
        """Start the GUI"""
        self.user_input.focus()
        self.root.mainloop()

# Import datetime for timestamps
import datetime as dt
tk.datetime = dt.datetime

if __name__ == "__main__":
    print("🚀 Starting Specter AI GUI...")
    app = SpecterGUI()
    app.run()

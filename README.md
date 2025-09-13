# Jarvis AI Agent - Hackathon Version

A desktop AI agent for Windows with voice interaction, file management, and intelligent conversation.

## Quick Start

1. **Install Dependencies:**
   ```
   pip install -r requirements.txt
   ```

2. **Configure API Keys:**
   - Edit `.env` file with your API keys
   - Get keys from: OpenAI, NewsAPI, OpenWeatherMap

3. **Run Jarvis:**
   ```
   python main.py
   ```

## Features

- Speech-to-Text & Text-to-Speech
- Music Playback (Local + Online)
- File Management & Organization
- Intelligent Conversation (LLM)
- Calendar & Reminders
- News Fetching
- Application Launcher
- Weather Information
- System Monitoring

## Project Structure

```
jarvis_hackathon/
├── main.py              # Entry point
├── modules/             # Core functionality modules
├── utils/               # Helper functions
├── data/                # Configuration files
├── tests/               # Test files
└── assets/              # Audio and resources
```

## Development

Each module in `modules/` contains a template ready for implementation.
Start with the modules you need most for your demo!

## Hackathon Tips

1. Implement modules incrementally
2. Test each feature before moving to next
3. Focus on demo-worthy features first
4. Use the JSON config files for quick customization

Good luck!

# AI-Desktop-Agent

A desktop AI agent for Windows that provides voice interaction, file management, system monitoring, reminders, weather & news fetching, application launching, and intelligent conversation via large language models.

---

## Table of Contents

- [Features](#features)  
- [Architecture & Project Structure](#architecture--project-structure)  
- [Getting Started](#getting-started)  
  - [Requirements](#requirements)  
  - [Installation](#installation)  
  - [Configuration](#configuration)  
- [Usage](#usage)  
- [Supported Modules](#supported-modules)  
- [Extending the Agent](#extending-the-agent)  
- [Testing](#testing)  
- [Known Issues / Limitations](#known-issues--limitations)  
- [Roadmap](#roadmap)  
- [Contributing](#contributing)  
- [License](#license)  
- [Acknowledgments](#acknowledgments)

---

## Features

The AI-Desktop-Agent includes (or is intended to include) the following capabilities:

- **Speech-to-Text & Text-to-Speech** — voice interaction for user commands and responses.  
- **Intelligent Conversation (LLM)** — chat with the agent; answer general knowledge / question & answer.  
- **File Management & Organization** — search, open, move, delete files, organize directories.  
- **Application Launcher** — start programs on your desktop via voice or typed commands.  
- **Weather Information** — fetch current weather, forecasts, etc.  
- **News Fetching** — get latest news via an API.  
- **System Monitoring** — CPU, memory usage, perhaps disk / network stats.  
- **Calendar & Reminders** — set reminders, manage calendar events.  
- **Music Playback (Local + Online)**  

---

## Architecture & Project Structure

Here’s the layout of the repository and what the components do (or are expected to do):

```
AI-Desktop-Agent/
├── main.py                # Entry point to start the agent
├── modules/               # Different feature modules (weather, news, file-mgmt, etc.)
├── utils/                 # Helper functions/utilities (speech, formatting, API wrappers)
├── data/                  # Configuration / data files
├── tests/                 # Unit / integration tests
└── requirements.txt       # Python dependencies
```

- **main.py** initializes the agent, sets up required services (speech, LLMs, etc.), handles the loop or event-driven interaction.  
- **modules/** implements specific features (e.g. weather, news, calendar).  
- **utils/** contains shared code — audio I/O, converting speech <-> text, logging, config reading.  
- **data/** holds configuration templates or examples (e.g. `.env` file).  
- **tests/** includes test scripts.  

---

## Getting Started

### Requirements

- Python 3.7+  
- OS: Windows (tested)  
- Internet access (for LLMs, weather/news APIs, etc.)  
- API keys for services:  
  - OpenAI (or other LLM provider)  
  - NewsAPI (or equivalent news feed)  
  - OpenWeatherMap (or other weather provider)  
  - Speech-to-Text / Text-to-Speech service keys if required  

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ItzHaniel/AI-Desktop-Agent.git
   cd AI-Desktop-Agent
   ```

2. Create & activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate    # Mac/Linux/WSL
   .\venv\Scripts\activate     # Windows PowerShell or CMD
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

- Create a `.env` file in the root folder with your API keys:

  ```
  OPENAI_API_KEY=your_openai_key_here or GROK_API_KEY
  NEWSAPI_KEY=your_newsapi_key_here
  WEATHER_API_KEY=your_openweathermap_key_here
  ```

- Adjust additional settings (voice parameters, file paths, etc.) in config files or constants.

---

## Usage

Start the agent:

```bash
python main.py
```

Once running, you can:

- Speak commands (if microphone access enabled)  
- Type commands (if CLI mode supported)  
- Get responses via speech or text  

**Example interaction:**

```
User: "Hey agent, what's the weather in New Delhi today?"
Agent: "The weather in New Delhi is 35°C, partly cloudy."
User: "Open Spotify"
Agent: [launches the app]
```

---

## Supported Modules

| Module | Purpose |
|--------|---------|
| **Speech** | Capture voice input and convert to text; convert responses into speech. |
| **LLM / Conversation** | Use OpenAI (or another LLM) to generate responses and hold conversations. We're using Groq. |
| **Weather** | Query weather APIs for current conditions and forecasts. |
| **News** | Fetch and summarize latest headlines. |
| **File Manager** | Search, open, move, delete, and organize files. |
| **Application Launcher** | Open installed applications. |
| **System Monitor** | Provide CPU, RAM, disk usage, and possibly network stats. |
| **Calendar / Reminders** | Set reminders and manage events. |
| **Music Playback** | Play local audio files or stream music. |

---

## Extending the Agent

You can add new features by creating modules under `modules/`. Be creative!
Tips for extending:

- Implement a standard interface (so modules can register themselves).  
- Add offline speech/LLM options for better privacy.  
- Create plugin-like support for drop-in features.  
- Improve error handling for failed API calls.  
- Add user-friendly configuration files.  

---

## Testing

Run tests with:

```bash
pytest
```

Mock audio or network modules as needed to test without hardware/API keys.

---

## Known Issues / Limitations

- High latency possible due to speech or LLM API calls.  
- Some modules may be incomplete or placeholder.  
- Offline support is limited.  
- Continuous listening mode may consume CPU/RAM significantly.  

---

## Roadmap

Planned enhancements:

- Offline speech recognition & TTS  
- Richer conversation memory  
- GUI dashboard interface  
- Plugin store for modules  
- Google/Outlook calendar integrations  
- Error recovery & fallback mechanisms  

---

## Contributing

Contributions welcome!  

1. Fork the repository  
2. Create a new branch (`git checkout -b feature/your-feature`)  
3. Commit changes with clear messages  
4. Submit a Pull Request  

---

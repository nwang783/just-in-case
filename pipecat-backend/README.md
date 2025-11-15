# Case Interview Coach - Voice Agent

A voice-powered case interview practice coach built with Pipecat for real-time conversational AI. Practice consulting case interviews through natural voice conversations.

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
```

Required API keys:
- **Daily.co API Key**: Get from [daily.co](https://www.daily.co/)
- **OpenAI API Key**: Get from [platform.openai.com](https://platform.openai.com/)
- **Deepgram API Key**: Get from [deepgram.com](https://www.deepgram.com/)

Optional API keys (for alternative TTS providers):
- **Cartesia API Key**: Get from [play.cartesia.ai](https://play.cartesia.ai/sign-up)
- **ElevenLabs API Key**: Get from [elevenlabs.io](https://elevenlabs.io/)

### 3. Create a Daily Room

You have two options:

**Option A: Auto-create a room at startup (recommended for demos)**
1. Set `DAILY_AUTO_CREATE_ROOM=true` in `.env`
2. (Optional) Customize `DAILY_ROOM_PREFIX` and `DAILY_ROOM_EXP_MINUTES`
3. When you run `python main.py`, the bot logs a unique room URL—share it with participants

**Option B: Use a static room**
1. Go to [daily.co](https://www.daily.co/) and create a room manually
2. Set `DAILY_ROOM_URL` to the room link in `.env`
3. Keep `DAILY_AUTO_CREATE_ROOM=false` to reuse the same room each run

### 4. Run the Bot

```bash
python main.py
```

The bot will:
1. Connect to the Daily room
2. Wait for you to join
3. Start the case interview practice session

## How to Use

1. **Start the bot**: `python main.py`
2. **Join the Daily room**: Open the Daily room URL in your browser
3. **Allow microphone access** when prompted
4. **Start practicing**: The bot will greet you and you can begin your case interview practice

## Project Structure

```
pipecat-backend/
├── src/
│   ├── bot/
│   │   ├── voice_agent.py     # Main pipeline orchestration
│   │   └── handlers.py         # Event handlers & logging
│   ├── services/
│   │   ├── llm_service.py      # LLM integration (OpenAI, Anthropic)
│   │   ├── tts_service.py      # Text-to-Speech (OpenAI, ElevenLabs, Cartesia)
│   │   └── stt_service.py      # Speech-to-Text (Deepgram)
│   ├── transport/
│   │   └── daily_transport.py  # Daily.co WebRTC transport
│   ├── config/
│   │   └── settings.py         # Configuration management
│   ├── system_prompts/
│   │   └── case_interviewer.txt # Case interviewer personality
│   └── utils/
│       └── logger.py           # Logging utilities
├── main.py                     # Application entry point
├── requirements.txt
└── .env
```

## Configuration

All configuration is done via environment variables in `.env`:

### Required Variables

```bash
# Daily.co (Transport)
DAILY_API_KEY=your_key_here
DAILY_ROOM_URL=https://your-domain.daily.co/your-room
DAILY_AUTO_CREATE_ROOM=false         # Enable true to create a room at startup
DAILY_ROOM_PREFIX=case-coach         # Used when auto-creating rooms
DAILY_ROOM_EXP_MINUTES=120           # Set how long auto-created rooms remain active

# OpenAI (LLM & TTS)
OPENAI_API_KEY=your_key_here

# Deepgram (STT)
DEEPGRAM_API_KEY=your_key_here
```

### Optional Variables

```bash
# Bot Configuration
BOT_NAME="Case Interview Coach"
BOT_GREETING="Hi! I'm ready to practice a case interview with you. Should we get started?"

# LLM Configuration
OPENAI_MODEL=gpt-4o  # or gpt-4o-mini, gpt-3.5-turbo

# Alternative: Anthropic Claude
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Alternative TTS: Cartesia (recommended for low latency)
CARTESIA_API_KEY=your_key_here
CARTESIA_VOICE_ID=79a125e8-cd45-4c13-8a67-188112f4dd22  # British Lady (default)
CARTESIA_MODEL=sonic-english

# Alternative TTS: ElevenLabs
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=your_voice_id_here

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=development

# Avatar Settings
AVATAR_ENABLED=false
AVATAR_ASSETS_DIR=assets
AVATAR_FRAME_GLOB=robot0*.png
AVATAR_FRAME_REPEAT=1

# Transcript Archiving
TRANSCRIPTS_ENABLED=true
TRANSCRIPTS_OUTPUT_DIR=output

# Transcript Analysis
TRANSCRIPT_ANALYSIS_ENABLED=true
TRANSCRIPT_ANALYSIS_MODEL=gpt-5-nano
TRANSCRIPT_ANALYSIS_OUTPUT_DIR=output/analysis
```

### Avatar Video Tile

To show an avatar when users join the Daily room:
1. Drop sequential PNG frames (e.g., `robot001.png` …) into `pipecat-backend/assets/`.
2. Set `AVATAR_ENABLED=true` in `.env`. Adjust `AVATAR_ASSETS_DIR` or `AVATAR_FRAME_GLOB` if you use a different folder or naming pattern.
3. (Optional) Slow down the animation by increasing `AVATAR_FRAME_REPEAT` (each frame is held for N transport frames).
4. Start the bot normally (`python main.py`). The agent now publishes a video track so the browser displays the animated avatar tile while the bot speaks.

### Transcript Archiving

Each conversation run is automatically written to the directory defined by
`TRANSCRIPTS_OUTPUT_DIR` (defaults to `/output` under the project root).
Transcripts are stored as JSONL with metadata, user turns, and bot turns so they
can be processed programmatically or tailed while the session is running. Set
`TRANSCRIPTS_ENABLED=false` to opt out.

### Transcript Analysis

When `TRANSCRIPT_ANALYSIS_ENABLED=true`, the bot calls OpenAI’s Responses API
after each session. It reads the saved transcript, generates structured
coaching insights (summary, key events, sentiment, next steps), and writes them
to `TRANSCRIPT_ANALYSIS_OUTPUT_DIR` as JSON files (matching the transcript
filename with an `-analysis` suffix). Use `TRANSCRIPT_ANALYSIS_MODEL` to pick
any JSON-schema-compatible OpenAI model.

## Customization

### Changing LLM Provider

Edit `main.py`:
```python
agent = VoiceAgent(
    settings=settings,
    llm_provider="anthropic",  # Changed from "openai"
    tts_provider="cartesia",
    stt_provider="deepgram",
)
```

### Changing TTS Provider

You can easily switch between different TTS providers:

```python
agent = VoiceAgent(
    settings=settings,
    llm_provider="openai",
    tts_provider="cartesia",  # Options: "openai", "cartesia", "elevenlabs"
    stt_provider="deepgram",
)
```

#### TTS Provider Options:

- **OpenAI TTS**: Fast and reliable, good for most use cases
- **Cartesia TTS** (Recommended): WebSocket-based streaming with excellent low latency
- **ElevenLabs TTS**: Premium voice quality, best for production

### Custom System Prompt

Edit `src/system_prompts/case_interviewer.txt` to customize the interviewer's personality, case types, or coaching style.

## Testing

### Test Daily Room Connection

```bash
# The bot will log connection status when started
python main.py
```

### Test with Browser Client

1. Start the bot: `python main.py`
2. Join the Daily room URL in your browser
3. Allow microphone access
4. Start speaking!

## Troubleshooting

### "DAILY_ROOM_URL not configured"
- Make sure you have a `.env` file with `DAILY_ROOM_URL` set
- Check that the room URL is valid (format: `https://your-domain.daily.co/room-name`)

### "API key not configured"
- Verify all required API keys are in `.env`
- Check for typos in variable names
- Ensure no extra spaces around the `=` sign

### Audio Quality Issues
- Check your internet connection
- Verify microphone permissions
- Try adjusting Daily room quality settings

### Import Errors
- Make sure you've installed all requirements: `pip install -r requirements.txt`
- Try reinstalling in a fresh virtual environment

## Development

### VAD (Voice Activity Detection)

VAD is enabled by default for better speech detection. You can adjust settings in `.env`:

```bash
VAD_ENABLED=true
VAD_CONFIDENCE=0.7      # Higher = more conservative
VAD_START_SECS=0.2      # Lower = more responsive
VAD_STOP_SECS=0.8       # Lower = faster cutoff
VAD_MIN_VOLUME=0.6      # Minimum volume threshold
```

### Enabling Metrics

Metrics are enabled by default in `src/bot/voice_agent.py`:
```python
params = PipelineParams(
    enable_metrics=True,
    enable_usage_metrics=True,
)
```

## Resources

- [Pipecat Documentation](https://docs.pipecat.ai/)
- [Daily.co Docs](https://docs.daily.co/)
- [OpenAI API](https://platform.openai.com/docs)
- [Deepgram Docs](https://developers.deepgram.com/)
- [Cartesia TTS](https://docs.cartesia.ai/)
- [ElevenLabs Docs](https://elevenlabs.io/docs)

## License

MIT

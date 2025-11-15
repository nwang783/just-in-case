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

### 4. Run the Session API (for frontend control)

Start the FastAPI app so the Next.js frontend can request Daily rooms and
trigger the Pipecat agent on demand:

```bash
uvicorn src.server.app:app --reload --port 8000
```

This exposes endpoints such as `POST /api/sessions` and `POST /api/sessions/{id}/start`.
See [FastAPI Session API](#fastapi-session-api) for the full contract.

### 5. Run the Bot Directly (optional)

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
│   ├── server/
│   │   ├── app.py              # FastAPI application
│   │   └── session_manager.py  # Session lifecycle + Daily rooms
│   ├── config/
│   │   └── interview_prompts.py  # Company/interview specific prompt snippets
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

# FastAPI / Frontend Integration
# Comma-separated list of additional origins allowed to call the API
FRONTEND_ALLOWED_ORIGINS=http://localhost:3000
```

### Avatar Video Tile

To show an avatar when users join the Daily room:
1. Drop sequential PNG frames (e.g., `robot001.png` …) into `pipecat-backend/assets/`.
2. Set `AVATAR_ENABLED=true` in `.env`. Adjust `AVATAR_ASSETS_DIR` or `AVATAR_FRAME_GLOB` if you use a different folder or naming pattern.
3. (Optional) Slow down the animation by increasing `AVATAR_FRAME_REPEAT` (each frame is held for N transport frames).
4. Start the bot normally (`python main.py`). The agent now publishes a video track so the browser displays the animated avatar tile while the bot speaks.

### Vision Analytics (User Engagement)

Set `VISION_ANALYTICS_ENABLED=true` in `.env` to subscribe to each participant's camera feed and run light-weight vision analytics (OpenCV Haar cascades). The processor samples a few frames per second, tracks attention (eye contact / looking away) and smiles, and logs state changes to the console and transcript file. Tunable knobs:

```bash
VISION_TARGET_FPS=6             # higher = more responsive, higher CPU usage
VISION_MAX_FRAME_WIDTH=640      # resize width before running the model
VISION_EYE_AR_THRESHOLD=0.18    # eye-aspect ratio, tweak for your lighting
VISION_LOOK_AWAY_THRESHOLD=0.12 # nose offset threshold for attention
VISION_SMILE_THRESHOLD=1.8      # larger ratios make “smile” harder to trigger
VISION_MIN_EVENT_GAP_SECS=2.5   # debounce for repeated events
```

After enabling:
1. `pip install -r requirements.txt` (installs `opencv-python` for the analyzer).
2. Start the bot (`python main.py`) and join the Daily room with your camera on.
3. Move your gaze off-screen or smile—the logs should emit entries such as `👀 Vision: User disengaged ...` and the transcript JSONL gains `"event": "vision"` entries. These engagement events are also kept in-memory on `VoiceAgent.last_engagement_event` for future LLM prompt conditioning.
4. When transcript analysis is enabled, those vision events are summarized and fed into the OpenAI post-run analysis so coaching feedback reflects non-verbal engagement cues.

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

## FastAPI Session API

The FastAPI app allows the web frontend (or other clients) to control when rooms
are created and when the Pipecat coach joins:

| Endpoint | Description |
| --- | --- |
| `POST /api/sessions` | Creates a new Daily room for a company/interview selection and returns `{sessionId, roomUrl, status}`. |
| `GET /api/sessions/{sessionId}` | Returns current status, room metadata, and any errors. |
| `POST /api/sessions/{sessionId}/start` | Launches the Pipecat `VoiceAgent` for the given room once the user is ready. |
| `POST /api/sessions/{sessionId}/stop` | Gracefully stops the running agent. |
| `GET /api/sessions` | Lists active sessions (useful for debugging). |
| `GET /healthz` | Basic readiness probe. |

The API enforces CORS for `http://localhost:3000` (and `127.0.0.1`) by default.
Add more domains using the optional `FRONTEND_ALLOWED_ORIGINS` environment
variable (comma-separated list).

## Company-specific Prompt Injection

When a session is created via `POST /api/sessions`, the backend looks up a
company/interview specific snippet in `src/config/interview_prompts.py`. That
snippet is appended to the base system prompt before the `VoiceAgent` starts,
so each session adopts the correct persona (e.g., McKinsey PSI vs. Bain fit).
Case-style entries also include scenario scripts plus “held-back” data blocks so
the AI only reveals detailed exhibits when the candidate earns them.

To extend or tweak behavior:
1. Edit `interview_prompts.py` and adjust the entries keyed by `companySlug`
   plus the exact `interviewType` strings used by the frontend.
2. Restart the FastAPI server to pick up the changes.
### Interview Analysis API

The same FastAPI server (`uvicorn src.server.app:app --reload --port 8000`) also
exposes structured transcript analyses so the frontend's `interview/analysis`
page can render the OpenAI-generated coaching report.

Endpoints:

- `GET /api/interviews/analysis?limit=20&include_pending=true` — returns the newest analyses and (optionally) transcripts that are still processing so you can show a “pending” badge.
- `GET /api/interviews/{conversation_id}/analysis` — returns the detailed payload (case summary, key events, strengths, areas, next steps, action items, sentiment, engagement summary, and `source_transcript`). When the analysis file doesn’t exist yet you’ll receive `{ "status": "pending" }`.

Sample response:

```json
[
  {
    "conversation_id": "conversation-20251115-210044-75bdda98",
    "status": "ready",
    "updated_at": "2025-11-15T21:02:00.000000+00:00",
    "analysis": {
      "case_summary": { "...": "..." },
      "key_events": [ { "timestamp": "...", "speaker": "User", "message": "..." } ],
      "coaching_feedback": { "...": "..." },
      "action_items": [ "..." ],
      "sentiment": { "user": "neutral", "assistant": "supportive" },
      "engagement_summary": { "summary": "..." },
      "source_transcript": "/absolute/path/to/output/conversation-....jsonl"
    }
  },
  {
    "conversation_id": "conversation-20251116-173015-5a2c91c9",
    "status": "pending",
    "updated_at": "2025-11-16T17:30:30.000000+00:00",
    "analysis": null
  }
]
```

The `TranscriptWriter` logs `Transcripts will be saved to: ...conversation-<slug>.jsonl`
as soon as a run starts. After a session finishes, `GET /api/sessions/{id}` now
includes `conversationId` so the frontend can redirect to
`/interview/analysis?conversationId=...` and poll the analysis endpoint until it
returns `status: "ready"`.

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

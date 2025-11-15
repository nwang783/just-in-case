# just-in-case

Case interview practice experience with a Next.js frontend and a Pipecat voice
agent backend.

## Development Workflow

### 1. Backend (Pipecat)

```bash
cd pipecat-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # configure API keys + Daily credentials

# Run the FastAPI control plane so the frontend can create rooms
uvicorn src.server.app:app --reload --port 8000
```

You can still run the bot directly via `python main.py`, but the FastAPI server
exposes `/api/sessions` endpoints that let the frontend spin up rooms on demand.

### 2. Frontend (Next.js)

```bash
cd frontend
cp .env.example .env.local   # BACKEND_BASE_URL defaults to http://localhost:8000
npm install
npm run start
```

Navigate to `http://localhost:3000` and open a company page to kick off an
interview session.

### 3. Running an Interview

1. Visit a company page (e.g. `/company/mckinsey-company`).
2. Click **Start Interview** to request a unique Daily room from the backend.
3. Join the Daily room using the generated link.
4. Click **I’m in the room – bring the AI** to tell the backend to launch the
   Pipecat `VoiceAgent` for that room.

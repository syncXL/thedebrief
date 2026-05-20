# TheDebrief

AI-powered news podcast generator. Given a natural-language request, it discovers relevant RSS sources, extracts and researches articles, analyzes them through a roundtable of AI personas, and produces a fully narrated audio episode with headline highlights and deep-dive segments.

## Architecture

The system is a pipeline of five [LangGraph](https://langchain-ai.github.io/langgraph/) agents orchestrated by a root graph:

```
START → Inquisitor → Herald → Researcher (parallel) → Director → END
```

| Agent | Role |
|---|---|
| **Inquisitor** | Discovers relevant RSS feeds from a global catalog based on your request |
| **Herald** | Fetches today's articles, selects the top 10 stories, downloads full text |
| **Researcher** | Per-article: web research for context + multi-persona roundtable analysis (runs in parallel across all stories) |
| **Director** | Writes anchor scripts, generates multi-voice TTS audio, normalizes and merges into a final MP3 episode |

## Personas

Each article is analyzed by 2–4 AI personas selected by an LLM router based on relevance. Nine personas are available:

`critic` `economist` `geopolitician` `historian` `lawyer` `politician` `scientist` `socialite` `tech_analyst`

The **historian** always runs last, synthesizing all persona insights into a closing perspective.

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph (StateGraph, Send API, sub-graphs) |
| LLM | Gemma 4 26B / 31B via OpenRouter |
| TTS | Gemini 2.5 Flash Preview (multi-speaker) |
| Web Research | Tavily |
| Article Parsing | newspaper4k |
| Audio Processing | pydub + pyloudnorm (LUFS normalization) |
| Storage | Cloudinary CDN |
| Backend | FastAPI + uvicorn |
| Frontend | React (Lovable) |

## Setup

### Prerequisites
- Python ≥ 3.12
- [uv](https://docs.astral.sh/uv/)
- Docker (recommended)
- ffmpeg (only required outside Docker)

### Environment

```bash
cp .env.example .env
```

| Variable | Source |
|---|---|
| `OPENROUTER_API_KEY` | [openrouter.ai](https://openrouter.ai) |
| `GOOGLE_API_KEY` | [aistudio.google.com](https://aistudio.google.com) — for TTS |
| `SEARCH_API_KEY` | [tavily.com](https://tavily.com) |
| `CLOUDINARY_CLOUD_NAME` | [cloudinary.com](https://cloudinary.com) |
| `CLOUDINARY_API_KEY` | — |
| `CLOUDINARY_API_SECRET` | — |

### Docker (recommended)

```bash
docker compose up --build
```

### Local

```bash
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

## API

| Endpoint | Description |
|---|---|
| `POST /generate-episode` | Full pipeline — returns `audio_url` and `headline_transcript` |
| `POST /librarian` | Feed discovery only |
| `POST /herald` | Article extraction only |
| `POST /correspondent` | Research only |
| `POST /persona` | Persona roundtable only |
| `POST /director` | Audio production only |

All endpoints accept `{"request": "..."}`.
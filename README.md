# TheDebrief

AI-powered news podcast generator. Given a natural-language request, it discovers relevant RSS sources, extracts and researches articles, analyzes them through a roundtable of AI personas, and produces a fully narrated audio episode with headline highlights and deep-dive segments.

## Architecture

The system is a pipeline of five [LangGraph](https://langchain-ai.github.io/langgraph/) agents orchestrated by a root graph:

```
START → Inquisitor → Herald → Researcher (parallel) → Director → END
```

| Agent | Role |
|---|---|
| **Inquisitor** (librarian) | LLM discovers relevant RSS feeds from a global catalog |
| **Herald** | Fetches recent articles, selects top stories, downloads full text |
| **Researcher** (correspondent + persona) | Web research + multi-persona analysis per article |
| **Director** | Writes scripts, generates TTS audio, merges into final MP3 |

## Setup

### Prerequisites

- Python >=3.12
- [uv](https://docs.astral.sh/uv/)
- ffmpeg

### Environment

```bash
cp .env.example .env
```

Required variables:

| Variable | Source |
|---|---|
| `OPENROUTER_API_KEY` | [openrouter.ai](https://openrouter.ai) |
| `GOOGLE_API_KEY` | [aistudio.google.com](https://aistudio.google.com) |
| `SEARCH_API_KEY` | [tavily.com](https://tavily.com) |
| `CLOUDINARY_CLOUD_NAME` | [cloudinary.com](https://cloudinary.com) |
| `CLOUDINARY_API_KEY` | — |
| `CLOUDINARY_API_SECRET` | — |

### Run

```bash
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

### Docker

```bash
docker compose up --build
```

## API

| Endpoint | Body | Runs |
|---|---|---|
| `POST /generate-episode` | `{"request": "..."}` | Full pipeline |
| `POST /librarian` | `{"request": "..."}` | Feed discovery only |
| `POST /herald` | `{"request": {...}}` | Article extraction only |
| `POST /correspondent` | `{"request": {...}}` | Research only |
| `POST /persona` | `{"request": {...}}` | Persona roundtable only |
| `POST /director` | `{"request": {...}}` | Audio production only |

## Personas

Nine expert personas analyze each article: critic, economist, geopolitician, historian, lawyer, politician, scientist, socialite, tech_analyst. The LLM router selects 2–4 relevant personas per article, then the historian compiles a synthesis.

## Tech Stack

- **Orchestration:** LangGraph (StateGraph, Send, sub-graphs)
- **LLM:** OpenRouter → Gemini, with direct Google API fallback
- **TTS:** Gemini 2.5 Flash Preview (multi-speaker)
- **Audio:** pydub, pyloudnorm (LUFS normalization), MP3 export
- **Storage:** Cloudinary CDN
- **Parser:** newspaper4k
- **Search:** Tavily
- **Server:** FastAPI + uvicorn

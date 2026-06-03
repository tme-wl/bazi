# Bazi Mingyi — Web Shell

A bilingual (English/中文) Ba Zi (Four Pillar) astrology web application. Enter your birth date and get a detailed fate analysis.

```
                   ┌──────────────────┐
                   │   Web Shell      │  React SPA + FastAPI
                   │  (web/frontend)  │
                   └────────┬─────────┘
                            │
                   ┌────────▼─────────┐
                   │   API Server     │  web/server.py
                   └────────┬─────────┘
                            │
                   ┌────────▼─────────┐
                   │   Core Engine    │  Private — skill/
                   │   (skill/)       │
                   └──────────────────┘
```

## Architecture

This repo contains the **web shell only**. The core analysis engine (`skill/`) is a private dependency not included here.

```
bazi/
├── web/                # Public — web shell
│   ├── server.py       # FastAPI backend
│   ├── requirements.txt
│   ├── start_server.sh
│   └── frontend/       # React + Vite + Tailwind SPA
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Quick Start (with skill/ present locally)

```bash
cd /path/to/bazi/project
python3 -m venv .venv
source .venv/bin/activate
pip install -r web/requirements.txt

# Set API key for LLM-enhanced readings (optional)
export BAZI_API_KEY=***

# Start server
uvicorn web.server:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000

## Deploy to Server

```bash
# 1. Clone this repo on your server
git clone git@github.com:tme-wl/bazi.git /opt/bazi

# 2. Deploy core engine separately (scp from local or private repo)
scp -r skill/ user@server:/opt/bazi/skill/

# 3. Install & start
cd /opt/bazi
python3 -m venv .venv
source .venv/bin/activate
pip install -r web/requirements.txt
cat > .env << 'EOF'
BAZI_API_KEY=***
EOF

# Start
set -a; source .env; set +a
uvicorn web.server:app --host 0.0.0.0 --port 8000
```

## API

### POST /api/analyze

```json
{
  "year": 1991,
  "month": 7,
  "day": 6,
  "hour": 2,
  "minute": 0,
  "gender": "male",
  "language": "en"
}
```

Returns structured analysis with sections for personality, career, wealth, relationships, health, and life advice.

### GET /api/health

```json
{
  "status": "ok",
  "version": "0.2.0",
  "llm_enabled": true
}
```

## Development

```bash
# Backend (hot reload)
cd /path/to/bazi/project
uvicorn web.server:app --reload --port 8000

# Frontend (hot reload)
cd /path/to/bazi/project/web/frontend
npm run dev
```

## Design

- Dark modern UI, English-first targeting Western audiences
- Bilingual (English/Chinese) via react-i18next
- LLM-enhanced readings when BAZI_API_KEY is set; pure rule-based fallback otherwise

## Disclaimer

Traditional cultural tool for entertainment and self-reflection. Not medical, legal, or financial advice.

# Bazi Mingyi — Ba Zi Chinese Astrology

A bilingual (English/中文) Ba Zi (Four Pillar) astrology web application, targeting Western audiences. Enter your birth date and get a detailed fate analysis.

```
                   ┌──────────────────┐
                   │   Web Shell      │  React SPA + FastAPI
                   │  (web/frontend)  │
                   └────────┬─────────┘
                            │
                   ┌────────▼─────────┐
                   │   API Server     │  web/server.py
                   │  (web/server.py) │
                   └────────┬─────────┘
                            │
                   ┌────────▼─────────┐
                   │   Core Engine    │  Pure Python, no web deps
                   │   (skill/)       │
                   │                  │
                   │  ┌─ calendar.py  │  Four Pillar calculation
                   │  ├─ analyzer.py  │  Element scores, patterns
                   │  ├─ parser.py    │  Birth info parser (CN/EN)
                   │  ├─ renderer.py  │  HTML report generator
                   │  └─ llm_provider │  OpenAI-compatible LLM
                   └──────────────────┘
```

## Quick Start

```bash
cd /Users/aron/code/bazi

# 1. Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r web/requirements.txt

# 2. Configure API key (optional, for LLM-enhanced readings)
#    Edit .env and set BAZI_API_KEY
#    Without it, the system uses rule-based analysis (still works great)

# 3. Start the server
./web/start_server.sh

# 4. Open in browser
open http://localhost:8000
```

## CLI Usage (Core Engine Only)

The core engine works independently, no web server needed:

```bash
# English analysis
python3 -m skill "1991-07-06 02:00 male" --lang en

# Chinese analysis
python3 -m skill "1991年7月6日 凌晨2点 男" --lang zh

# Save HTML report
python3 -m skill "1991-07-06 02:00 male" --lang en -o my-report.html

# Try LLM enhancement (if BAZI_API_KEY is set)
python3 -m skill "1991-07-06 02:00 male" --lang en --llm
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
  "timezone": "Asia/Shanghai",
  "language": "en"
}
```

Returns structured analysis with sections for personality, career, wealth, relationships, health, and life advice.

### GET /api/health

```json
{
  "status": "ok",
  "version": "0.2.0",
  "llm_enabled": true,
  "timestamp": "2026-06-03T04:13:24Z"
}
```

## Project Structure

```
bazi/
├── skill/                  # Core analysis engine (standalone)
│   ├── __init__.py
│   ├── __main__.py         # CLI entry point
│   ├── models.py           # Data models
│   ├── constants.py        # Astrological constants + English mappings
│   ├── calendar.py         # Four Pillar calculation
│   ├── parser.py           # Birth info parser (CN/EN formats)
│   ├── analyzer.py         # Rule-based analysis + English text generation
│   ├── llm_provider.py     # LLM integration (OpenAI-compatible)
│   ├── prompt_builder.py   # LLM prompt construction
│   ├── renderer.py         # HTML report renderer
│   └── prompts/
│       ├── bazi_mingyi.md      # Chinese analysis rules
│       └── bazi_mingyi_en.md   # English analysis rules
├── web/                    # Web shell
│   ├── server.py           # FastAPI server
│   ├── requirements.txt
│   ├── start_server.sh
│   └── frontend/           # React + Vite + Tailwind CSS
│       ├── dist/           # Production build
│       └── src/
│           ├── pages/Home.tsx, Reading.tsx
│           ├── components/
│           ├── i18n/       # en.json, zh.json
│           └── api/client.ts
├── .env                    # API key configuration (gitignored)
├── .gitignore
└── README.md
```

## LLM Enhancement

For richer, more nuanced readings, set an OpenAI-compatible API key:

```bash
# Edit .env
BAZI_API_KEY=sk-your-key-here
BAZI_API_BASE=https://api.deepseek.com/v1    # default: https://api.openai.com/v1
BAZI_API_MODEL=deepseek-v4-flash             # default: gpt-4o-mini
```

When `BAZI_API_KEY` is set, the server automatically enhances all sections with LLM-generated text. Without it, the built-in rule engine generates thorough English analysis — the site works fully either way.

## Development

```bash
# Backend (hot reload)
cd /Users/aron/code/bazi
uvicorn web.server:app --reload --port 8000

# Frontend (hot reload)
cd /Users/aron/code/bazi/web/frontend
npm run dev
```

The Vite dev server proxies `/api/*` requests to the backend on port 8000.

## Design Principles

- **Core separated from web shell** — `skill/` is a pure Python package with no web dependencies
- **Bilingual by default** — English primary, Chinese secondary
- **Modern dark UI** — Clean minimal aesthetic with subtle Eastern touches
- **Graceful degradation** — Pure rule analysis when no LLM available
- **No login required** — MVP is fully open (rate limiting can be added later)

## Disclaimer

This project is a traditional cultural tool for entertainment and self-reflection. It is not a substitute for medical, legal, or financial advice. Health-related content is based on folk astrology correspondences and should not replace professional medical diagnosis.

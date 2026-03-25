# TrendNexAI Python Backend

FastAPI backend for TrendNexAI. It fetches news from remote APIs, rewrites with AI, and stores in MongoDB.

## Setup

1. Copy environment from root .env.local (should contain `MONGODB_URI`, `OPENAI_API_KEY`, `GNEWS_API_KEY`).

2. Install dependencies:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Run in development:

```bash
uvicorn app.main:app --reload --port 8001
```

4. Check health:

`http://localhost:8001/health`

## API

- `GET /api/fetch-news?limit_per_cat=5`
- `GET /api/articles?category=technology&company=times&skip=0&limit=20`
- `GET /api/article/{slug}`
- `GET /api/categories`
- `GET /api/companies`

## Cron

`app.main` starts APScheduler at startup to run every hour on the hour.

## Next.js integration

In frontend, point data requests to Python backend:

`NEXT_PUBLIC_API_BASE_URL=http://localhost:8001`

Example:

`fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/articles?category=technology`)`

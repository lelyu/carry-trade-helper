# Carry Trade Helper

A comprehensive platform for carry trade analysis.

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Docker

```bash
docker-compose up -d
```

## API Keys Required

- RESEND_API_KEY - For sending emails
- GOOGLE_API_KEY - For Gemini AI
- TAVILY_API_KEY - For web search
- DATABASE_URL - PostgreSQL connection string
- REDIS_URL - Redis connection string

## Documentation

See [AGENTS.md](AGENTS.md) for detailed development guidelines.

## License

MIT
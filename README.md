# Carry Trade Helper

A comprehensive platform for carry trade analysis featuring real-time exchange rates, interest rate data, AI-powered recommendations, daily email reports, and an interactive chat interface.

## Features

- **Real-time Data**: Exchange rates from Frankfurter API and interest rates from DBnomics
- **AI-Powered Analysis**: LangChain deep-agents with Google Gemini for trading recommendations
- **Interactive Chat**: Ask questions about carry trade opportunities
- **Email Reports**: Daily/hourly email reports with Resend API
- **Interactive Charts**: D3.js visualizations for rate trends
- **User Preferences**: Customize currency pairs, email frequency, and alert thresholds
- **Magic Link Auth**: Passwordless authentication for enhanced security

## Technology Stack

### Backend
- **Framework**: FastAPI (async Python 3.11+)
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0 (async)
- **Task Queue**: Celery + Redis (6-hour scheduling)
- **AI/Chat**: LangChain deep-agents + Google Gemini
- **Web Search**: Tavily API
- **Email**: Resend API
- **Authentication**: Magic Link (passwordless)

### Frontend
- **Framework**: Vue 3 Composition API + TypeScript
- **Styling**: Tailwind CSS
- **Charts**: D3.js
- **State**: Pinia stores
- **Build**: Vite

### External APIs
- **Frankfurter**: https://api.frankfurter.dev/v2 (exchange rates, no key)
- **DBnomics**: https://api.db.nomics.world/v22 (interest rates)
- **Tavily**: https://tavily.com (web search for agents)
- **Resend**: https://resend.com/docs/send-with-python (email delivery)
- **Gemini**: Google Generative AI (chat agent)

## Project Structure

```
carry-trade-helper/
├── backend/              # FastAPI Python backend
│   ├── app/
│   │   ├── api/          # API route handlers
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic & API clients
│   │   ├── agents/       # LangChain deep-agent
│   │   ├── tasks/        # Celery background tasks
│   │   └── core/         # Config, security, database
│   ├── tests/
│   └── requirements.txt
├── frontend/            # Vue.js TypeScript frontend
│   ├── src/
│   │   ├── components/   # Vue components
│   │   ├── views/        # Page views
│   │   ├── composables/  # Composition functions
│   │   ├── stores/       # Pinia stores
│   │   ├── services/     # API clients
│   │   └── types/        # TypeScript types
│   └── package.json
├── docker-compose.yml
├── AGENTS.md
└── README.md
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd carry-trade-helper
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys:
# - RESEND_API_KEY
# - GOOGLE_API_KEY
# - TAVILY_API_KEY
# - DATABASE_URL
# - REDIS_URL
# - SECRET_KEY
# - FRONTEND_URL

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env
# Edit .env with your API URL

# Start development server
npm run dev
```

### 4. Docker Setup (Optional)

```bash
# Start all services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 5. Celery Setup (Background Tasks)

```bash
# In backend directory, activate virtual environment
source venv/bin/activate

# Start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# In another terminal, start Celery beat scheduler
celery -A app.tasks.celery_app beat --loglevel=info
```

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/carrytrade
REDIS_URL=redis://localhost:6379/0
RESEND_API_KEY=re_xxxxx
GOOGLE_API_KEY=AIza_xxxxx
TAVILY_API_KEY=tvly_xxxxx
SECRET_KEY=your-secret-key-change-in-production
FRONTEND_URL=http://localhost:3000
EMAIL_DOMAIN=yourdomain.com
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

## API Endpoints

### Authentication
- `POST /auth/request-magic-link` - Request magic link email
- `POST /auth/verify-magic-link` - Verify token and get JWT
- `GET /auth/me` - Get current user info

### Rates
- `GET /api/exchange-rates/latest` - Latest exchange rates
- `GET /api/exchange-rates/historical` - Historical time series
- `GET /api/exchange-rates/currencies` - List supported currencies
- `GET /api/interest-rates/latest` - Latest interest rates
- `GET /api/interest-rates/historical` - Historical interest rates

### Subscriptions
- `GET /api/preferences` - Get user preferences
- `POST /api/preferences` - Create preferences
- `PUT /api/preferences` - Update preferences

### Chat
- `POST /api/chat/message` - Send message to AI agent
- `GET /api/chat/history` - Get chat history

## Development

### Backend Commands

```bash
# Run development server
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black .

# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "message"
```

### Frontend Commands

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Run type checking
npm run type-check

# Run linting
npm run lint
```

## Deployment

### Railway Deployment

1. Connect GitHub repository
2. Add environment variables in Railway dashboard
3. Deploy backend service (auto-detected)
4. Deploy frontend service
5. Deploy Celery worker and beat services
6. Add PostgreSQL and Redis add-ons

### Production Checklist

- [ ] Set `SECRET_KEY` to secure random value
- [ ] Configure custom domain for email sending
- [ ] Verify domain with Resend
- [ ] Set up PostgreSQL backups
- [ ] Configure Redis persistence
- [ ] Enable SSL/TLS
- [ ] Set up monitoring
- [ ] Configure rate limiting

## Testing

### Backend Tests

```bash
cd backend
pytest
pytest --cov=app tests/
```

### Frontend Tests

```bash
cd frontend
npm run test
```

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For questions or issues, please open a GitHub issue.

## Acknowledgments

- Frankfurter API for exchange rate data
- DBnomics for interest rate data
- LangChain for deep-agent framework
- Google Gemini for AI capabilities
- Resend for email delivery
- Vue.js and FastAPI communities
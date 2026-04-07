# Carry Trade Helper - Agent Guidelines

## Project Overview
A comprehensive platform for carry trade analysis featuring:
- Real-time exchange rate and interest rate data
- AI-powered trading recommendations via LangChain deep-agents
- Daily/hourly email reports
- Interactive chat interface
- D3.js visualizations

## Technology Stack

### Backend
- **Framework**: FastAPI (async Python3.11+)
- **Database**: PostgreSQL 15+with SQLAlchemy 2.0 (async)
- **Task Queue**: Celery + Redis (6-hour scheduling)
- **AI/Chat**: LangChain deep-agents + Google Gemini
- **Web Search**: Tavily API
- **Email**: Resend API

### Frontend
- **Framework**: Vue 3 Composition API + TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Charts**: D3.js
- **State**: Pinia stores
- **Build**: Vite

### External APIs
- **Frankfurter**: https://api.fankfurter.dev/v2 (exchange rates, no key)
- **DBnomics**: https://api.db.nomics.world/v22 (interest rates)
- **Tavily**: https://tavily.com (web search for agents)
- **Resend**: https://resend.com/docs/send-with-python (email delivery)
- **Gemini**: Google Generative AI (chat agent)

## Code Style Guidelines

### Backend (Python)
- Follow PEP8 with Black formatting
- Use type hints for all functions
- Async/await patterns throughout
- Repository pattern for data access
- Pydantic v2 schemas for validation
- Dependency injection via FastAPI's Depends()

### Frontend (TypeScript/Vue)
- Use `<script setup lang="ts">` syntax
- Strict TypeScript mode enabled
- Composition API only (no Options API)
- D3.js integration in dedicated chart components
- Pinia for state management
- Tailwind CSS utility-first approach

## Project Structure

```
backend/app/
├── api/           # FastAPI route handlers
├── models/        # SQLAlchemy ORM models
├── schemas/       # Pydantic request/response schemas
├── services/      # Business logic & external API clients
├── agents/        # LangChain deep-agent implementations
├── tasks/         # Celery background tasks
└── core/          # Config, security, database

frontend/src/
├── components/    # Vue components
├── views/         # Page-level components
├── composables/   # Reusable composition functions
├── stores/        # Pinia state stores
├── services/      # API client functions
└── types/         # TypeScript type definitions
```

## Key Patterns

### Authentication Flow
1. User submits email to `/auth/request-magic-link`
2. Backend creates magic link token (expires in 15 min)
3. Resend sends email with magic link
4. User clicks link → `/auth/verify-magic-link`
5. Backend validates token → returns JWT
6. Frontend stores JWT in localStorage

### Rate Fetching (Every 6 Hours)
1. Celery Beat triggers `fetch_and_cache_rates` task
2. Query Frankfurter API for exchange rates
3. Query DBnomics for interest rates
4. Store results in PostgreSQL
5. Check user-defined alert thresholds
6. Send notifications if thresholds exceeded

### Chat with Deep Agent
1. User sends message to `/api/chat/message`
2. Backend loads user's chat history
3. Agent invokes with Gemini + tools (Tavily search, rate queries)
4. Agent performs multi-step reasoning and research
5. Response saved to database
6. Stream response to frontend

## Development Commands

### Backend
```bash
# Install dependencies
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Run database migrations
alembic upgrade head

# Run Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# Run Celery beat scheduler
celery -A app.tasks.celery_app beat --loglevel=info

# Run tests
pytest
```

### Frontend
```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run type checking
npm run type-check

# Run linting
npm run lint
```

### Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/carrytrade
REDIS_URL=redis://localhost:6379/0
RESEND_API_KEY=re_xxxxx
GOOGLE_API_KEY=AIza_xxxxx
TAVILY_API_KEY=tvly_xxxxx
SECRET_KEY=your-secret-key
FRONTEND_URL=http://localhost:3000
EMAIL_DOMAIN=yourdomain.com
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## Testing Requirements

- Backend: pytest with >80% coverage
- Frontend: Vitest with component tests
- Integration tests for API endpoints
- Unit tests for business logic services

## Deployment

### Railway Deployment
1. Connect GitHub repository
2. Add environment variables in Railway dashboard
3. Deploy backend service (auto-detected)
4. Deploy frontend service (build command auto-detected)
5. Deploy Celery worker and beat services
6. Add PostgreSQL and Redis add-ons

### Production Checklist
- [ ] Set `SECRET_KEY` to secure random value
- [ ] Configure custom domain for email sending
- [ ] Verify domain with Resend
- [ ] Set up PostgreSQL backups
- [ ] Configure Redis persistence
- [ ] Enable SSL/TLS
- [ ] Set up monitoring (Railway metrics)
- [ ] Configure rate limiting

## API Endpoints

### Authentication
- `POST /auth/request-magic-link` - Request magic link email
- `POST /auth/verify-magic-link` - Verify token and get JWT
- `GET /auth/me` - Get current user info

### Rates
- `GET /api/exchange-rates/latest` - Latest exchange rates
- `GET /api/exchange-rates/historical` - Historical time series
- `GET /api/interest-rates/latest` - Latest interest rates

### Subscriptions
- `POST /api/preferences` - Update user preferences
- `GET /api/preferences` - Get current preferences

### Chat
- `POST /api/chat/message` - Send message to AI agent
- `GET /api/chat/history` - Get chat history

### Reports
- `GET /api/reports/summary` - Daily summary
- `GET /api/reports/signals` - Trading signals

## Security Considerations

- JWT tokens expire after 30 minutes
- Magic links expire after 15 minutes
- CORS configured for production domain only
- Rate limiting on all endpoints
- SQL injection prevention via SQLAlchemy
- Input validation via Pydantic schemas
- Environment variables never committed
- `.env` files in `.gitignore`

## Supported Currency Pairs
- Major pairs: EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, NZD/USD
- Additional: USD/CNY, USD/HKD

## Contact & Support

For questions about the architecture or implementation:
1. Check this AGENTS.md file
2. Review inline code comments
3. Check API documentation at `/docs` (FastAPI Swagger)

## Updates and Maintenance

When updating this project:
1. Run all tests before committing
2. Update database migrations if models change
3. Run linters: `black .` (Python), `npm run lint` (Frontend)
4. Update AGENTS.md if architecture changes
5. Check for dependency updates monthly

---
*Last updated: 2025-04-07*
*Project version: 0.1.0*
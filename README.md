# Carry Trade Helper

A mobile-first platform for carry trade analysis featuring real-time exchange rates and interest rate data with interactive D3.js charts.

## Features

- **Exchange Rates**: Real-time rates from Frankfurter API with base currency switcher, 7d/30d/90d/1y historical charts, and trend indicators
- **Interest Rates**: Central bank policy rates from FRED with step-function charts showing rate changes over time
- **Mobile-First UI**: Bottom tab bar navigation on mobile, side-by-side panels on desktop
- **Interactive Charts**: D3.js line charts with hover tooltips, step-function mode for interest rates
- **Trend Indicators**: Contextual trend arrows (7d change) on every rate row
- **In-Memory Caching**: 1-hour TTL with request deduplication for fast, efficient API calls
- **Stale Cache Fallback**: Serves cached data with warning when external APIs are down

## Technology Stack

### Backend
- **Framework**: FastAPI (async Python 3.13+)
- **Caching**: In-memory TTL cache with asyncio Lock deduplication
- **External APIs**: Frankfurter (exchange rates), FRED (interest rates)
- **No database, no Celery, no Redis** — stateless single-process server

### Frontend
- **Framework**: Vue 3 Composition API + TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Charts**: D3.js with step-function support
- **State**: Pinia stores
- **Build**: Vite

## Project Structure

```
backend/app/
├── api/                  # FastAPI route handlers
│   ├── exchange_rates.py # Exchange rate endpoints
│   └── interest_rates.py # Interest rate endpoints
├── core/
│   ├── cache.py          # In-memory TTL cache with deduplication
│   └── config.py         # Pydantic settings
├── schemas/              # Pydantic request/response schemas
└── services/             # External API clients
    ├── frankfurter_client.py
    └── fred_client.py

frontend/src/
├── components/           # Vue components
│   ├── LineChart.vue     # D3.js chart with step mode
│   ├── TabBar.vue        # Mobile bottom tab bar
│   └── TrendIndicator.vue
├── views/                # Page views
│   ├── Home.vue          # Desktop side-by-side layout
│   ├── ExchangeRates.vue # Exchange rate list with search
│   ├── ExchangeDetail.vue# Currency detail with chart
│   ├── InterestRates.vue # Interest rate list with search
│   └── InterestDetail.vue# Country detail with chart
├── stores/               # Pinia state stores
└── services/             # API client
```

## Getting Started

### Prerequisites

- Python 3.13+
- Node.js 18+

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env — only FRED_API_KEY is required
# Get a free FRED API key at: https://fred.stlouisfed.org/docs/api/api_key.html

# Start development server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

Open http://localhost:3000

## Environment Variables

### Backend (.env)

```env
FRED_API_KEY=your_fred_api_key      # Required — get one at https://fred.stlouisfed.org
FRONTEND_URL=http://localhost:3000   # Optional, defaults to localhost:3000
CACHE_TTL_SECONDS=3600              # Optional, defaults to 3600 (1 hour)
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

## API Endpoints

- `GET /health` — Health check
- `GET /api/exchange-rates/latest?base=USD` — Latest rates + 7d history + trends
- `GET /api/exchange-rates/historical?base=USD&target=JPY&from=2025-01-01&to=2025-05-01` — Historical time series
- `GET /api/exchange-rates/currencies` — Supported currency list
- `GET /api/interest-rates/latest` — Latest interest rates + 1y change history + trends
- `GET /api/interest-rates/historical?country=JPN&from=2025-01-01&to=2025-05-01` — Historical interest rates

## Routes

| Path | Description |
|------|-------------|
| `/` | Home — side-by-side panels on desktop, cards on mobile |
| `/exchange` | Exchange rate list with search and base currency switcher |
| `/exchange/:target` | Currency detail with D3 chart and period selector |
| `/interest` | Interest rate list with search |
| `/interest/:code` | Country detail with step-function chart |

## Deployment

### Free-tier hosting (recommended for getting started)

- **Frontend**: Vercel or Netlify (free tier, auto-deploy from git)
- **Backend**: Render (free tier, single FastAPI process)

No PostgreSQL, Redis, or Celery needed — the backend is fully stateless.

## Development

### Backend Commands

```bash
uvicorn app.main:app --reload    # Dev server
```

### Frontend Commands

```bash
npm run dev          # Dev server
npm run build        # Production build
npm run type-check   # TypeScript checking
```

## License

MIT
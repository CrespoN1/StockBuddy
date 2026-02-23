# StockBuddy Product Roadmap

## Current State Assessment

StockBuddy is an AI-powered stock portfolio and earnings call analyzer. The codebase
has **three layers** in varying states of completion:

| Layer | Tech | Status |
|---|---|---|
| **Desktop app** (root `main.py`) | Tkinter + Selenium + yfinance | Prototype / proof of concept |
| **Backend API** (`apps/api/`) | FastAPI + PostgreSQL + Redis + arq workers | ~70% built, well-structured |
| **Web frontend** (`apps/web/`) | Next.js 16 + React 19 + Clerk + TailwindCSS + shadcn/ui | ~60% built, pages and components exist |

The API layer is the most production-ready part. It has proper async database access,
Alembic migrations (6 so far), Clerk JWT auth, Stripe billing scaffolding, structured
logging via structlog, Sentry integration, rate limiting, and CI (lint + test) via
GitHub Actions. The web frontend has routing, Clerk auth, dashboard pages, and React
Query hooks wired to the API.

### What Currently Works (API)
- Portfolio CRUD (create, list, update, delete)
- Holdings CRUD with market data enrichment
- Earnings call analysis (scrape + AI summary via DeepSeek)
- Portfolio-level AI analysis
- Multi-stock comparison analysis
- Stock search, fundamentals, candlestick data, technicals
- Watchlist management
- Price alerts
- Subscription/billing scaffolding (Stripe checkout, portal, webhooks)
- Background job queue (arq + Redis)
- News aggregation, Reddit sentiment, price forecasting services

### What Currently Works (Web)
- Auth flows (sign-in / sign-up via Clerk)
- Dashboard shell with sidebar navigation
- Portfolio list, detail view, holdings table
- Stock search, detail pages with candlestick charts
- Earnings analysis form and results display
- Comparison tool with multi-select
- Watchlist and alerts pages
- Billing/upgrade page
- CSV export utility

---

## What's Needed for a Fully Functioning Product

### Phase 1: Fix Critical Gaps (Must-Have Before Launch)

#### 1.1 Security: Remove Hardcoded Secrets
**Priority: CRITICAL**

`config.py` at the repo root contains hardcoded API keys in plaintext:
```
MASSIVE_API_KEY = "zg6LoRvK7kW53hpf5B05ft78DE8z7TSQ"
DEEPSEEK_API_KEY = "sk-13795f0f8029452ea0be459ad6db1383"
ALPHA_VANTAGE_API_KEY = "X5184RQAARQKZG8O"
```

**Actions:**
- Rotate all exposed API keys immediately (they are in git history)
- Remove the root `config.py` hardcoded defaults, require `.env` exclusively
- Audit `apps/api/.env.example` to ensure no real keys are committed
- Add a pre-commit hook or CI check that scans for secrets (e.g., `trufflehog`, `gitleaks`)
- Consider using a secrets manager (AWS Secrets Manager, Doppler, etc.) for production

#### 1.2 Decide on Architecture: Desktop vs Web
**Priority: CRITICAL**

The codebase contains two complete UI approaches: a Tkinter desktop app and a
Next.js web app. Shipping both is impractical for a small team.

**Recommendation:** Commit fully to the web stack (`apps/api` + `apps/web`).
The desktop app was a useful prototype but the web architecture is significantly
more mature, supports multi-user auth, and is deployable to users without
installation. The root-level files (`main.py`, `ai_explainer.py`,
`portfolio_analyzer.py`, `stock_chart.py`, `market_data.py`, `models.py`,
`config.py`) should be archived or removed.

#### 1.3 Database Migrations & Schema Completeness
**Priority: HIGH**

The API has 6 Alembic migrations, which is a good start. Review for:
- Ensure all model fields match the latest migration state
- Add indexes on frequently queried columns (user_id + ticker combinations)
- Add database-level constraints (e.g., unique constraint on user_id + ticker
  per portfolio to prevent duplicate holdings)
- Plan for data migration strategy when schema changes in production

#### 1.4 Earnings Transcript Sourcing
**Priority: HIGH**

The desktop app scrapes `earningscall.biz` via Selenium with brittle XPath
selectors. The API has a `transcript.py` service. Key issues:
- Selenium-based scraping breaks when the target site changes layout
- No fallback if scraping fails
- Legal/TOS risk with scraping third-party sites

**Actions:**
- Integrate a proper earnings transcript API (e.g., Financial Modeling Prep,
  Alpha Vantage earnings endpoint, Seeking Alpha API, or EarningsCall.biz's
  official API if available)
- Build a caching layer so transcripts are fetched once and stored in the database
- Add retry logic with graceful degradation (show analysis based on fundamentals
  + news if transcript unavailable -- the `analyze_stock_overview` function
  already exists for this)

#### 1.5 Error Handling & Resilience
**Priority: HIGH**

- The API has bare `except:` or `except Exception` blocks in several places that
  silently swallow errors
- External API calls (Alpha Vantage, DeepSeek, yfinance) lack circuit breaker
  patterns -- if one service is down, the entire request fails slowly
- Background workers need dead-letter queues for failed jobs

**Actions:**
- Add structured error responses for all API endpoints
- Implement circuit breakers (e.g., via `tenacity` which is already a dependency)
  for all external service calls
- Add health check endpoints for each external dependency
- Ensure the arq worker retries failed tasks and has alerting on repeated failures

---

### Phase 2: Production Infrastructure

#### 2.1 Deployment Pipeline
**Status:** Partially configured (Railway for API, Vercel implied for frontend)

**Actions:**
- Set up proper staging and production environments
- Configure environment-specific settings (the `Settings.validate_production`
  method is a good start)
- Set up database backups (automated daily for PostgreSQL)
- Configure Redis persistence or use a managed Redis service
- Add deployment health checks and rollback procedures
- Set up a CI/CD pipeline that runs tests, builds, and deploys on merge to main

#### 2.2 Monitoring & Observability
**Status:** Sentry is configured, structlog is in place

**Actions:**
- Add application performance monitoring (Sentry APM is already partially set up)
- Set up alerting rules (error rate spikes, latency p99, failed background jobs)
- Add request/response logging for debugging (structlog with request context
  middleware is already built)
- Dashboard for API usage metrics (requests per user, AI analysis counts)
- Monitor external API usage and costs (DeepSeek tokens, Alpha Vantage calls)

#### 2.3 Rate Limiting & Abuse Prevention
**Status:** slowapi is integrated with configurable limits

**Actions:**
- Tune rate limits based on actual usage patterns:
  - `100/minute` general, `10/minute` AI, `30/minute` search (current defaults)
- Add per-user rate limiting (currently appears to be per-IP)
- Implement cost-based limiting for AI endpoints (token usage tracking)
- Add CAPTCHA or proof-of-work for unauthenticated endpoints if needed

---

### Phase 3: Feature Completeness

#### 3.1 Subscription & Billing (Stripe)
**Status:** Scaffolded but untested with real payments

The subscription service has `FREE_LIMITS` and `PRO_LIMITS` both set to unlimited
(`None`) with the comment "MVP: Free tier unlocked (same as Pro). Tighten these
when ready to monetize."

**Actions:**
- Define actual free-tier limits (e.g., 3 portfolios, 5 holdings each, 10
  earnings analyses/month)
- Create the Stripe product and price in the Stripe dashboard
- Test the full checkout flow: upgrade, manage subscription, cancel, webhook
  processing
- Handle edge cases: failed payments, subscription lapses, grace periods
- Build the billing page UI to show current plan, usage meters, and upgrade CTA
  (the web page exists but needs real data)

#### 3.2 Background Job Processing
**Status:** arq worker configured, task infrastructure exists

**Actions:**
- Wire up actual background tasks:
  - Periodic market data refresh for all holdings
  - Earnings calendar monitoring (alert users before earnings dates)
  - Price alert checking (poll prices and trigger notifications)
  - Portfolio snapshot generation (daily/weekly summaries)
- Add job status tracking so the frontend can poll for completion (the
  `use-job-polling.ts` hook exists)
- Implement notification delivery (email via SendGrid/Resend, or push
  notifications)

#### 3.3 Price Alerts
**Status:** API router and model exist, service partially implemented

**Actions:**
- Complete the price alert checking loop (run via arq worker on a schedule)
- Add notification delivery when alerts trigger
- Support alert types: price above/below threshold, percentage change, volume spike
- Allow users to set alerts from the stock detail page
- Auto-expire or auto-disable alerts after triggering

#### 3.4 Portfolio History & Performance Tracking
**Status:** Model exists (`PortfolioSnapshot`), chart component exists

**Actions:**
- Implement daily snapshot creation (background job that records portfolio value)
- Build time-series storage for historical portfolio performance
- Calculate returns: daily, weekly, monthly, YTD, all-time
- Compare portfolio performance against benchmarks (S&P 500, NASDAQ)
- Wire up the `portfolio-history-chart.tsx` component to real data

#### 3.5 Export & Reporting
**Status:** CSV export utility exists in frontend, export button is a placeholder
in desktop app

**Actions:**
- Implement CSV export for holdings, portfolio analysis, and earnings reports
- Add PDF report generation for portfolio summaries
- Consider scheduled email reports (weekly portfolio digest)

#### 3.6 Peer Comparison
**Status:** The desktop app has a `compare_with_peers` placeholder function

**Actions:**
- Auto-detect sector peers based on a stock's sector/industry
- Pre-populate comparison tool with relevant peers
- Show relative valuation metrics (P/E, P/S, EV/EBITDA) across peers

---

### Phase 4: Quality & Reliability

#### 4.1 Test Coverage
**Status:** Test files exist for most API routers, CI runs pytest

**Actions:**
- Verify existing tests pass and add coverage measurement
- Add integration tests for critical flows:
  - User signs up -> creates portfolio -> adds holdings -> runs analysis
  - Stripe webhook -> subscription upgrade -> usage limits change
- Add frontend tests (React Testing Library, or Playwright for E2E)
- Set a coverage target (e.g., 80% for API, 60% for frontend) and enforce in CI
- Add load testing for AI analysis endpoints (they call external APIs and can be
  slow)

#### 4.2 Code Quality
**Status:** Ruff linting configured, TypeScript strict mode in frontend

**Actions:**
- Fix the duplicate `get_earnings_insights` method in `portfolio_analyzer.py`
  (defined twice in the root file)
- Fix the `disable_buttons_during_operation` and `_disable_buttons_in_frame`
  functions defined outside the class at the bottom of `main.py`
- Remove unused root-level files if committing to web architecture
- Add type annotations to all API service functions
- Set up pre-commit hooks (ruff, mypy, eslint, prettier)

#### 4.3 API Documentation
**Status:** FastAPI auto-generates OpenAPI docs at `/docs`

**Actions:**
- Add request/response examples to all endpoints
- Document rate limits and authentication requirements
- Add API versioning strategy (currently `/api/v1`)
- Create a developer guide if the API will be public

---

### Phase 5: Growth & Polish

#### 5.1 User Experience
- Add onboarding flow for new users (guided portfolio creation)
- Implement search autocomplete with debouncing (stock search bar exists)
- Add loading skeletons (skeleton components exist but verify coverage)
- Mobile-responsive design audit (Tailwind helps but needs testing)
- Dark mode support (next-themes is a dependency)
- Toast notifications for async operations (sonner is configured)

#### 5.2 AI Quality
- Evaluate DeepSeek output quality vs. alternatives (GPT-4, Claude)
- Add prompt versioning so you can A/B test analysis quality
- Implement feedback mechanism (thumbs up/down on AI analyses)
- Cache AI responses to avoid redundant API calls for the same data
- Add streaming support for AI responses (better UX for long analyses)

#### 5.3 Data Quality
- Validate market data from Alpha Vantage against yfinance for accuracy
- Handle market hours correctly (show "market closed" indicators)
- Cache stock data with appropriate TTLs (intraday vs. daily data)
- Add data freshness indicators ("Price as of 3:45 PM EST")

#### 5.4 Legal & Compliance
- Add financial disclaimer ("Not financial advice, for educational purposes only")
- Terms of Service and Privacy Policy
- GDPR compliance if serving EU users (data export, deletion)
- Cookie consent if using analytics
- Review API provider terms of service for commercial use

---

## Suggested Launch Order

| Step | What | Why |
|------|-------|-----|
| 1 | Rotate secrets, remove hardcoded keys | Security emergency |
| 2 | Remove/archive desktop app files | Reduce confusion, single architecture |
| 3 | Get API + Web running end-to-end locally | Verify the full stack works |
| 4 | Deploy staging environment | Test with real external APIs |
| 5 | Test auth flow (Clerk) end-to-end | Users need to sign in |
| 6 | Test core loop: create portfolio -> add holdings -> run analysis | Core value proposition |
| 7 | Fix earnings transcript sourcing | Key feature must be reliable |
| 8 | Add financial disclaimers, ToS, privacy policy | Legal requirement |
| 9 | Set up monitoring and alerting | Know when things break |
| 10 | Soft launch (invite-only beta) | Get real user feedback |
| 11 | Implement Stripe billing with real limits | Monetization |
| 12 | Public launch | After beta feedback is addressed |

---

## Tech Stack Summary

| Component | Technology | Notes |
|---|---|---|
| Frontend | Next.js 16, React 19, TailwindCSS 4, shadcn/ui | Deployed to Vercel |
| Auth | Clerk | JWT-based, handles sign-up/sign-in/session |
| API | FastAPI, Python 3.12 | Async, deployed to Railway |
| Database | PostgreSQL 16 | Managed via Alembic migrations |
| Cache/Queue | Redis 7 | Used by arq for background jobs |
| AI | DeepSeek API | OpenAI-compatible, used for all analysis |
| Market Data | Alpha Vantage, yfinance, Massive API | Fundamentals, prices, search |
| Billing | Stripe | Checkout, billing portal, webhooks |
| Monitoring | Sentry | Error tracking + APM |
| CI/CD | GitHub Actions | Lint + test for both frontend and backend |
| Logging | structlog | Structured JSON logging with request context |

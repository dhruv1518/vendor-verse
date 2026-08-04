# VendorVerse — Deployment Guide

> **Document Version:** 1.0  
> **Last Updated:** 2026-07-22  
> **Status:** Approved  
> **Related Documents:** [System Architecture](./03-system-architecture.md) · [Project Structure](./11-project-structure.md) · [Security & Performance](./10-security-performance.md)

---

## 1. Environment Overview

```mermaid
graph LR
    DEV["Development<br/>(Local Docker)"]
    STG["Staging<br/>(Cloud/VPS)"]
    PROD["Production<br/>(Cloud/VPS)"]

    DEV -->|PR merge to develop| STG
    STG -->|Manual promote to main| PROD

    style DEV fill:#3b82f6,stroke:#1d4ed8,color:#fff
    style STG fill:#f59e0b,stroke:#d97706,color:#fff
    style PROD fill:#10b981,stroke:#059669,color:#fff
```

| Environment | Purpose | Database | Debug | SSL | Email |
|---|---|---|---|---|---|
| **Development** | Local coding & testing | PostgreSQL (Docker) | On | Off | Mailpit (local) |
| **Staging** | Pre-production validation | PostgreSQL (managed) | Off | On | SendGrid (sandbox) |
| **Production** | Live platform | PostgreSQL (managed) | Off | On | SendGrid (live) |

---

## 2. Docker Configuration

### 2.1 Dockerfile

```dockerfile
# Multi-stage build for optimized image
# Stage 1: Python dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

# System dependencies for psycopg2 and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt requirements/production.txt ./requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

# Stage 2: Application
FROM python:3.12-slim AS runtime

WORKDIR /app

# Runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system app && adduser --system --group app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=config.settings.production

# Switch to non-root user
USER app

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

EXPOSE 8000

ENTRYPOINT ["scripts/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
```

### 2.2 Docker Compose — Development

```yaml
# docker-compose.yml (development)
services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
      - media_data:/app/media
    ports:
      - "8000:8000"
    env_file: .env
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.development
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: vendorverse
      POSTGRES_USER: vendorverse
      POSTGRES_PASSWORD: vendorverse_dev
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U vendorverse"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  celery:
    build: .
    command: celery -A config worker --loglevel=info --concurrency=2
    volumes:
      - .:/app
    env_file: .env
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.development
    depends_on:
      - db
      - redis

  celery-beat:
    build: .
    command: celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    volumes:
      - .:/app
    env_file: .env
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.development
    depends_on:
      - db
      - redis

  mailpit:
    image: axllent/mailpit:latest
    ports:
      - "8025:8025"  # Web UI
      - "1025:1025"  # SMTP

volumes:
  postgres_data:
  media_data:
```

### 2.3 Docker Compose — Production Overrides

```yaml
# docker-compose.prod.yml
services:
  web:
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120 --access-logfile -
    volumes: []  # No code mount in production
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production

  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - static_files:/app/staticfiles
    depends_on:
      - web

  celery:
    command: celery -A config worker --loglevel=warning --concurrency=4
    volumes: []
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production

volumes:
  static_files:
```

---

## 3. Environment Variables

### 3.1 `.env.example`

```bash
# Django Core
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://vendorverse:vendorverse_dev@db:5432/vendorverse

# Redis
REDIS_URL=redis://redis:6379/0

# Email (Development: Mailpit)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=mailpit
EMAIL_PORT=1025
EMAIL_USE_TLS=False
DEFAULT_FROM_EMAIL=noreply@vendorverse.local

# Stripe (Test keys)
STRIPE_PUBLIC_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here

# Storage (Development: local filesystem)
USE_S3=False

# Social Auth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Sentry (optional in development)
SENTRY_DSN=
```

---

## 4. CI/CD Pipeline

### 4.1 GitHub Actions — CI

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff
      - run: ruff check .
      - run: ruff format --check .

  test:
    runs-on: ubuntu-latest
    needs: lint
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: vendorverse_test
          POSTGRES_USER: vendorverse
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements/test.txt
      - run: python manage.py makemigrations --check --dry-run
        env:
          DJANGO_SETTINGS_MODULE: config.settings.test
          DATABASE_URL: postgres://vendorverse:test_password@localhost:5432/vendorverse_test
      - run: pytest --cov=apps --cov-report=xml --cov-fail-under=80
        env:
          DJANGO_SETTINGS_MODULE: config.settings.test
          DATABASE_URL: postgres://vendorverse:test_password@localhost:5432/vendorverse_test
          REDIS_URL: redis://localhost:6379/1
      - uses: codecov/codecov-action@v4
        with:
          file: coverage.xml

  security:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pip-audit
      - run: pip-audit -r requirements/base.txt
```

### 4.2 GitHub Actions — CD

```yaml
# .github/workflows/cd.yml
name: CD

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: [lint, test, security]
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t vendorverse:${{ github.sha }} .
      - name: Push to registry
        run: |
          docker tag vendorverse:${{ github.sha }} registry/vendorverse:latest
          docker push registry/vendorverse:latest
      - name: Deploy to production
        run: |
          # SSH to production server and pull new image
          # Run migrations
          # Restart services
          echo "Deploy steps configured per hosting provider"
```

---

## 5. Deployment Procedures

### 5.1 First-Time Setup

```bash
# 1. Clone repository
git clone https://github.com/your-org/vendorverse.git
cd vendorverse

# 2. Copy environment file
cp .env.example .env
# Edit .env with your configuration

# 3. Build and start services
docker compose up --build -d

# 4. Run migrations
docker compose exec web python manage.py migrate

# 5. Create admin user
docker compose exec web python manage.py create_superadmin

# 6. Seed initial data (categories, subscription tiers)
docker compose exec web python manage.py seed_data

# 7. Build Tailwind CSS
npm install
npm run build:css

# 8. Collect static files
docker compose exec web python manage.py collectstatic --noinput

# 9. Verify
open http://localhost:8000
```

### 5.2 Routine Deployment

```bash
# 1. Pull latest code
git pull origin main

# 2. Build new image
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# 3. Run migrations (with dry run first)
docker compose exec web python manage.py migrate --plan
docker compose exec web python manage.py migrate

# 4. Collect static files
docker compose exec web python manage.py collectstatic --noinput

# 5. Restart services (zero-downtime with rolling restart)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps web

# 6. Verify health
curl -f https://vendorverse.com/health/

# 7. Monitor logs
docker compose logs -f web --tail=100
```

### 5.3 Rollback Procedure

```bash
# 1. Identify the previous working image tag
docker images vendorverse --format "{{.Tag}}"

# 2. Roll back to previous image
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps web

# 3. If migration needs reversal
docker compose exec web python manage.py migrate <app_name> <previous_migration_number>

# 4. Verify
curl -f https://vendorverse.com/health/
```

---

## 6. Database Management

### 6.1 Migration Workflow

| Environment | Procedure |
|---|---|
| **Development** | `makemigrations` → `migrate` → commit migration files |
| **Staging** | Migrations auto-applied by CI after test pass |
| **Production** | `migrate --plan` (dry run) → `migrate` (during maintenance window) |

### 6.2 Backup Strategy

| Schedule | Method | Retention | Storage |
|---|---|---|---|
| Daily | `pg_dump` via cron | 30 days | S3 / offsite storage |
| Pre-deployment | Manual `pg_dump` | Until deployment verified | Local + S3 |
| Weekly | Full WAL archive | 90 days | S3 |

```bash
# Automated backup script (scripts/backup_db.sh)
# pg_dump $DATABASE_URL | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
# Upload to S3 with retention policy
```

---

## 7. Monitoring & Observability

### 7.1 Health Check Endpoint

```
GET /health/
Response: { "status": "ok", "database": "ok", "redis": "ok", "celery": "ok" }
```

Checks database connectivity, Redis ping, and Celery worker responsiveness.

### 7.2 Monitoring Stack

| Concern | Tool | Setup |
|---|---|---|
| **Error tracking** | Sentry | `sentry-sdk[django]` configured in production settings |
| **Performance** | Sentry Performance | APM traces on views and tasks |
| **Uptime** | UptimeRobot (free) | Monitor `/health/` endpoint every 5 min |
| **Logs** | Docker logs → aggregator | `docker compose logs` or Loki/CloudWatch |
| **Task queue** | Flower | `celery -A config flower --port=5555` |
| **Database** | `pg_stat_statements` | Monitor slow queries, connection count |

### 7.3 Alert Configuration

| Alert | Condition | Channel |
|---|---|---|
| Site down | Health check fails 3x | Email + Slack |
| Error spike | > 50 errors in 5 minutes | Sentry notification |
| Slow response | p95 > 2 seconds | Sentry Performance |
| Database connection | > 80% of pool used | Email |
| Disk space | > 85% used | Email |
| Celery queue depth | > 500 tasks pending | Email |
| Failed payment | Payment error rate > 5% | Email + Slack (immediate) |

---

## 8. Makefile for Developer Experience

```makefile
# Common developer commands
.PHONY: help run test lint migrate shell

help:            ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

run:             ## Start all services
	docker compose up -d

stop:            ## Stop all services
	docker compose down

build:           ## Rebuild containers
	docker compose up --build -d

test:            ## Run tests with coverage
	docker compose exec web pytest --cov=apps --cov-report=term-missing

lint:            ## Run linter
	docker compose exec web ruff check .

format:          ## Format code
	docker compose exec web ruff format .

migrate:         ## Run database migrations
	docker compose exec web python manage.py migrate

makemigrations:  ## Create new migrations
	docker compose exec web python manage.py makemigrations

shell:           ## Django shell
	docker compose exec web python manage.py shell_plus

dbshell:         ## Database shell
	docker compose exec db psql -U vendorverse vendorverse

logs:            ## View logs
	docker compose logs -f --tail=100

seed:            ## Seed database with initial data
	docker compose exec web python manage.py seed_data

css:             ## Build Tailwind CSS
	npm run build:css

css-watch:       ## Watch Tailwind CSS (development)
	npm run watch:css
```

---

*← [Testing Strategy](./13-testing-strategy.md) · Next: [Development Roadmap →](./15-development-roadmap.md)*

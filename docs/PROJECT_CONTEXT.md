# VendorVerse — Project Context

> **Master Reference Document for AI Development Sessions**  
> **Last Updated:** 2026-07-22  
> **Version:** 1.0

---

## Purpose

This document is the **single entry point** for any developer or AI beginning work on VendorVerse. Read this document first before writing any code. It provides a complete project overview with references to detailed documentation.

---

## 1. Project Summary

**VendorVerse** is an enterprise-grade multi-vendor marketplace web application built with Django. It enables vendors to create storefronts, list products, and manage orders, while customers enjoy a unified shopping experience with cross-vendor cart, secure checkout, and order tracking. The platform generates revenue through vendor commissions and subscription tiers.

| Attribute | Value |
|---|---|
| **Type** | Multi-Vendor E-Commerce Marketplace |
| **Framework** | Django 5.x (mandatory) |
| **Architecture** | Modular Monolith |
| **Database** | PostgreSQL 16 |
| **Frontend** | Django Templates + HTMX + Alpine.js + Tailwind CSS 3 |
| **API** | Django REST Framework (REST, JWT auth) |
| **Cache/Broker** | Redis 7 |
| **Task Queue** | Celery 5.4+ |
| **Payments** | Stripe Connect |
| **Auth** | Django Allauth (session) + SimpleJWT (API) |
| **Deployment** | Docker + Docker Compose + GitHub Actions CI/CD |

---

## 2. Business Objective

Build a marketplace platform where:
- **Vendors** can register, get approved, set up storefronts, list products, fulfill orders, and track earnings
- **Customers** can browse, search, add to a multi-vendor cart, checkout with Stripe, track orders, and leave reviews
- **Admins** can approve vendors, moderate content, configure commissions, and monitor platform health
- **The Platform** earns revenue through tiered commissions (1.5%–5%) and vendor subscriptions

---

## 3. User Roles

| Role | Key Capabilities |
|---|---|
| **Customer** | Browse, search, cart, checkout, orders, reviews, wishlist, profile/addresses |
| **Vendor** | Storefront management, product CRUD, order fulfillment, earnings/payouts, analytics |
| **Admin** | Vendor approval, content moderation, commission config, platform analytics, site settings |

Vendors retain all customer capabilities. Role transition: Customer → Vendor (via admin-approved application).

---

## 4. Technology Stack

### Backend
- **Python 3.12+**, **Django 5.x**, **Django REST Framework 3.15+**
- **PostgreSQL 16** (primary DB, full-text search via `pg_trgm` + `SearchVector`)
- **Redis 7** (cache, sessions, Celery broker)
- **Celery 5.4+** (async tasks: emails, image processing, reports, payouts)
- **Gunicorn** (WSGI server) + **Nginx** (reverse proxy)

### Frontend
- **Django Templates** (server-rendered pages)
- **HTMX** (dynamic interactions without page reloads)
- **Alpine.js** (client-side reactivity: dropdowns, modals, galleries)
- **Tailwind CSS 3** (utility-first styling)

### Infrastructure
- **Docker + Docker Compose** (containerized development and deployment)
- **GitHub Actions** (CI: lint, test, security scan; CD: build, deploy)
- **Sentry** (error tracking + APM)
- **Stripe Connect** (multi-vendor payment processing with commission splitting)
- **django-storages + S3** (media storage in production)

### Key Packages
| Package | Purpose |
|---|---|
| `django-allauth` | Registration, email verification, social auth (Google/GitHub) |
| `djangorestframework-simplejwt` | JWT authentication for API |
| `django-htmx` | HTMX middleware and utilities |
| `django-filter` | Queryset filtering for views and API |
| `drf-spectacular` | OpenAPI schema generation |
| `django-environ` | Environment variable management |
| `django-redis` | Redis cache backend |
| `django-celery-beat` | Periodic task scheduling |
| `Pillow` | Image processing |
| `stripe` | Stripe API client |
| `whitenoise` | Static file serving |

---

## 5. Architecture Summary

### Architectural Pattern
**Modular Monolith** — single Django project with well-bounded apps communicating through a service layer. Chosen over microservices for development speed, transactional consistency, and team-size fit. Modules can be extracted to services later if needed.

### Layered Architecture
```
Presentation (Templates + DRF Views)
    → Business Logic (Service Layer)
        → Data Access (Django ORM + Custom Managers)
            → Infrastructure (PostgreSQL, Redis, S3, Stripe)
```

### Key Architectural Decisions
1. **Service Layer Pattern** — Business logic lives in `services.py`, not views or models. Views are thin.
2. **Selectors Pattern** — Read-only queries in `selectors.py`, separate from write operations in `services.py`.
3. **HTMX over SPA** — Server-rendered with progressive enhancement; no JavaScript build pipeline.
4. **Session + JWT dual auth** — Sessions for browser security, JWT for API/mobile.
5. **PostgreSQL FTS** — Built-in full-text search with trigram similarity; no Elasticsearch dependency.
6. **Shared schema multi-tenancy** — Vendor isolation via foreign keys, not separate schemas.

---

## 6. Database Summary

### Core Entities

| App | Models | Key Relationships |
|---|---|---|
| **accounts** | User, UserProfile, Address, AuditLog | User → Profile (1:1), User → Addresses (1:N) |
| **vendors** | Vendor, VendorApplication, Storefront, SubscriptionTier | User → Vendor (1:1), Vendor → Storefront (1:1) |
| **products** | Product, Category, ProductImage, ProductVariant, ProductTag | Vendor → Products (1:N), Category → Products (1:N) |
| **cart** | Cart, CartItem | User → Cart (1:1), Cart → CartItems (1:N) |
| **orders** | Order, OrderItem, OrderStatusLog, ReturnRequest | User → Orders (1:N), Order → OrderItems (1:N) |
| **payments** | Payment, Transaction | Order → Payment (1:1), Payment → Transactions (1:N) |
| **reviews** | Review, ReviewImage, ReviewResponse | Product → Reviews (1:N), Review → VendorResponse (1:1) |
| **notifications** | Notification, NotificationPreference | User → Notifications (1:N) |
| **administration** | SiteConfiguration, Coupon, CouponUsage | Singleton config; Coupon → Usages (1:N) |

### Key Design Decisions
- **Integer PKs** for performance; **UUID `public_id`** for URLs (prevents enumeration)
- **Soft deletes** via `is_active` flag on critical entities
- **Denormalized fields** for read performance: `Product.average_rating`, `Vendor.product_count`
- **Immutable order snapshots**: shipping address and product price stored at order time
- **Order status state machine** with valid transitions enforced in service layer

---

## 7. Core Modules

### 7.1 Module Communication Flow
```
accounts → vendors → products → cart → orders → payments
                                              → reviews
                                              → analytics
All modules → notifications (via signals)
core → (shared by all modules)
administration → (configures vendors, products, platform)
```

### 7.2 Module Responsibilities

| Module | Owns | Delegates To |
|---|---|---|
| **core** | Base models, exceptions, mixins, utilities | — |
| **accounts** | User lifecycle, authentication, profiles | Allauth, SimpleJWT |
| **vendors** | Vendor application, storefront, subscriptions, earnings | Stripe Connect (for onboarding) |
| **products** | Product CRUD, categories, search, image management | Celery (image processing) |
| **cart** | Cart state, item validation | Products (stock check) |
| **orders** | Order creation, lifecycle, returns, invoices | Payments (charge/refund), Notifications (events) |
| **payments** | Stripe integration, commission splitting, payouts | Stripe API |
| **reviews** | Review CRUD, moderation, rating aggregation | Products (update denormalized rating) |
| **notifications** | Email + in-app notifications, preferences | Celery (async delivery) |
| **analytics** | Dashboard aggregations, reports | Orders, Products (read-only queries) |
| **administration** | Site config, commission tiers, moderation queues | Vendors, Products, Reviews |

---

## 8. Key Workflows

| Workflow | Document | Section |
|---|---|---|
| Customer registration & login | [Auth & Authorization](./09-authentication-authorization.md) | §1 |
| Vendor application & onboarding | [User Flows](./08-user-flows.md) | §3.1 |
| Product listing & search | [User Flows](./08-user-flows.md) | §2.2 |
| Cart to checkout to payment | [User Flows](./08-user-flows.md) | §2.3 |
| Order fulfillment (vendor) | [User Flows](./08-user-flows.md) | §3.3 |
| Multi-vendor commission split | [User Flows](./08-user-flows.md) | §5.1 |
| Review submission | [User Flows](./08-user-flows.md) | §5.2 |
| Vendor payout | [User Flows](./08-user-flows.md) | §5.3 |
| Admin vendor review | [User Flows](./08-user-flows.md) | §4.1 |
| Content moderation | [User Flows](./08-user-flows.md) | §4.2 |

---

## 9. Folder Structure (Top-Level)

```
vendorverse/
├── config/                  # Django settings, URLs, WSGI/ASGI, Celery
│   └── settings/            # base.py, development.py, production.py, test.py
├── apps/                    # All Django apps
│   ├── core/                # Shared base models, mixins, utilities
│   ├── accounts/            # User auth, profiles, addresses
│   ├── vendors/             # Vendor management, storefronts
│   ├── products/            # Product catalog, categories, search
│   ├── cart/                # Shopping cart
│   ├── orders/              # Order lifecycle, returns
│   ├── payments/            # Stripe integration, payouts
│   ├── reviews/             # Reviews, ratings, moderation
│   ├── notifications/       # Email + in-app notifications
│   ├── analytics/           # Dashboard data (no models)
│   └── administration/      # Site config, coupons, moderation
├── templates/               # Global templates (base, layouts, includes, components)
├── static/                  # CSS, JS (HTMX, Alpine.js), images
├── media/                   # User uploads (dev only; S3 in prod)
├── docs/                    # This documentation suite
├── scripts/                 # Utility scripts (entrypoint, backup)
├── requirements/            # base.txt, development.txt, production.txt, test.txt
├── docker-compose.yml       # Development services
├── Dockerfile               # Application container
├── Makefile                 # Developer commands
└── README.md
```

Each app follows a consistent internal structure:
`models/ → services.py → selectors.py → serializers.py → views/(web.py, api.py) → urls/ → forms.py → tests/`

Full structure: [Project Structure Document](./11-project-structure.md)

---

## 10. Development Principles

### Code Architecture
- **Service layer is the source of truth** — views call services; services call models
- **Selectors for reads, services for writes** — clear separation of query and mutation
- **Keyword-only arguments** on service functions — prevents positional errors
- **Domain exceptions** — services raise domain-specific errors, not HTTP errors
- **Signals for side effects** — notifications, cache invalidation, analytics (not for core logic)

### Coding Standards
- **PEP 8 + Ruff** — line length 99, double quotes, trailing commas
- **Absolute imports only** — `from apps.products.models import Product`
- **Google-style docstrings** — on all public functions
- **No business logic in views, serializers, or models** — services only
- **No N+1 queries** — `select_related`/`prefetch_related` mandatory on list views

### Git Workflow
- **Branches:** `main` (production) → `develop` (integration) → `feature/*`, `bugfix/*`
- **Commits:** `type(scope): description` (e.g., `feat(products): add search`)
- **PRs:** Required for `develop` and `main`; CI must pass; 1 review minimum

Full details: [Coding Standards](./12-coding-standards.md)

---

## 11. Security Principles

- **OWASP Top 10** mitigated for all categories — detailed in [Security Document](./10-security-performance.md)
- **Django ORM exclusively** — no raw SQL; prevents SQL injection
- **CSRF protection** on all state-changing requests
- **XSS prevention** — template auto-escaping + CSP header
- **Argon2id** password hashing
- **Rate limiting** on auth endpoints (10/min) and API (100/min)
- **File uploads** validated, re-encoded, and served from CDN (never Django process)
- **Secrets in environment variables** — never committed to source
- **UUID public IDs** — prevent resource enumeration

---

## 12. Performance Principles

- **Redis caching** at view, fragment, and queryset levels — [details](./10-security-performance.md)
- **N+1 prevention** — enforced via django-debug-toolbar + code review
- **Lazy loading** images; WebP format; responsive `srcset`
- **HTMX partial updates** — avoid full page reloads for dynamic content
- **Celery offloading** — emails, image processing, reports never block requests
- **Database indexing** — composite indexes on all filtered/sorted columns
- **Connection pooling** — PgBouncer or django-db-connection-pool
- **Target:** <2s page load (p95), <500ms API response (p95), ≥1000 concurrent users

---

## 13. Documentation Index

| # | Document | Purpose |
|---|---|---|
| 01 | [Project Overview](./01-project-overview.md) | Business analysis, personas, assumptions, constraints |
| 02 | [Software Requirements](./02-software-requirements.md) | Functional/non-functional requirements, acceptance criteria |
| 03 | [System Architecture](./03-system-architecture.md) | HLD, LLD, component diagrams, ADRs, caching, logging |
| 04 | [Database Design](./04-database-design.md) | ER diagram, all schemas, indexing, state machine |
| 05 | [API Design](./05-api-design.md) | REST endpoints, request/response schemas, rate limiting |
| 06 | [Django Architecture](./06-django-architecture.md) | App structure, service layer, settings, middleware, signals |
| 07 | [UI/UX Design](./07-ui-ux-design.md) | Design system, components, pages, HTMX patterns |
| 08 | [User Flows](./08-user-flows.md) | Use cases, flow diagrams, sequence diagrams, edge cases |
| 09 | [Authentication & Authorization](./09-authentication-authorization.md) | Auth flows, RBAC, JWT, session management |
| 10 | [Security & Performance](./10-security-performance.md) | OWASP mitigations, caching, query optimization |
| 11 | [Project Structure](./11-project-structure.md) | Complete folder tree with annotations |
| 12 | [Coding Standards](./12-coding-standards.md) | Python/Django conventions, Git workflow, PR process |
| 13 | [Testing Strategy](./13-testing-strategy.md) | Testing pyramid, factories, CI integration |
| 14 | [Deployment Guide](./14-deployment-guide.md) | Docker, CI/CD, environments, monitoring |
| 15 | [Development Roadmap](./15-development-roadmap.md) | Phased plan, milestones, MVP scope |
| — | **PROJECT_CONTEXT.md** (this file) | Master reference for AI sessions |

---

## 14. Quick Start for AI Sessions

When starting a new development session on VendorVerse:

1. **Read this file** for project context
2. **Check the [Development Roadmap](./15-development-roadmap.md)** to identify the current phase
3. **Read the relevant detailed documents** for the module you're working on
4. **Follow the [Coding Standards](./12-coding-standards.md)** and **[Django Architecture](./06-django-architecture.md)** patterns
5. **Write tests** per the [Testing Strategy](./13-testing-strategy.md)
6. **Never skip:**
   - Service layer pattern (services.py, not logic in views)
   - `select_related` / `prefetch_related` on querysets
   - Permission checks on every view
   - Domain exceptions (not HTTP exceptions in services)
   - Keyword-only arguments on service functions

---

*This document is the permanent blueprint for VendorVerse. All development decisions should align with the architecture documented here.*

# VendorVerse — Enterprise Multi-Vendor Marketplace

[![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7.0-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![HTMX](https://img.shields.io/badge/HTMX-1.9+-336699?style=for-the-badge&logo=htmx&logoColor=white)](https://htmx.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)

**VendorVerse** is an enterprise-grade multi-vendor marketplace web application built with Django, PostgreSQL, Redis, Celery, HTMX, and Tailwind CSS. It is architected as a production-ready, modular monolith featuring multi-tenant storefronts, multi-vendor cart and checkout processing, Stripe Connect payment splitting, role-based access control, and complete platform administration.

---

## 📚 Documentation Suite

The project includes complete Sprint 0 planning, architectural blueprints, and operational documentation in the [`/docs`](./docs) directory:

| Document                                                                 | Description                                                                  |
| ------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| 📄 [**PROJECT_CONTEXT.md**](./docs/PROJECT_CONTEXT.md)                   | **Master reference for AI development sessions** — read this first!          |
| 📊 [01. Project Overview](./docs/01-project-overview.md)                 | Business problem, goals, user personas, scope, and risk assessment           |
| 📋 [02. Software Requirements](./docs/02-software-requirements.md)       | Comprehensive SRS with 80+ functional & non-functional requirements          |
| 🏗️ [03. System Architecture](./docs/03-system-architecture.md)           | High & low-level architecture, C4 diagrams, request lifecycles, and ADRs     |
| 🗄️ [04. Database Design](./docs/04-database-design.md)                   | ER diagrams, table schemas, indexing strategy, and state machines            |
| 🔌 [05. API Design](./docs/05-api-design.md)                             | REST API endpoints, schemas, rate limits, and OpenAPI specs                  |
| 🐍 [06. Django Architecture](./docs/06-django-architecture.md)           | App decomposition, service layer pattern, middleware, and signals            |
| 🎨 [07. UI/UX Design](./docs/07-ui-ux-design.md)                         | Design system, component library, page inventory, and HTMX patterns          |
| 🔄 [08. User Flows](./docs/08-user-flows.md)                             | End-to-end user workflows, sequence diagrams, and edge cases                 |
| 🔐 [09. Auth & Authorization](./docs/09-authentication-authorization.md) | Dual authentication (Session + JWT), RBAC matrix, and security audit logging |
| 🛡️ [10. Security & Performance](./docs/10-security-performance.md)       | OWASP mitigations, security headers, caching, and scalability strategies     |
| 📁 [11. Project Structure](./docs/11-project-structure.md)               | Fully annotated codebase tree and directory guidelines                       |
| 📏 [12. Coding Standards](./docs/12-coding-standards.md)                 | Code conventions, linting configuration, and Git workflow                    |
| 🧪 [13. Testing Strategy](./docs/13-testing-strategy.md)                 | Testing pyramid, Factory Boy setup, mocking, and CI pipeline                 |
| 🚀 [14. Deployment Guide](./docs/14-deployment-guide.md)                 | Docker, Compose setup, environment variables, CI/CD, and Makefiles           |
| 🗺️ [15. Development Roadmap](./docs/15-development-roadmap.md)           | 6-phase Gantt roadmap, milestones, and MVP scope definition                  |

---

## 🛠️ Technology Stack

- **Core Framework:** Django 5.x
- **Language:** Python 3.12+
- **Primary Database:** PostgreSQL 16 (Full-text search, trigram matching, JSONB)
- **Caching & Broker:** Redis 7
- **Task Processing:** Celery 5.4+ with Django Celery Beat
- **Frontend:** Server-Rendered Django Templates, HTMX, Alpine.js, Tailwind CSS 3
- **API Framework:** Django REST Framework (DRF) with SimpleJWT & drf-spectacular
- **Payments:** Stripe Connect
- **Authentication:** Django Allauth + SimpleJWT
- **Containerization:** Docker & Docker Compose
- **Code Quality:** Ruff, Pytest, Coverage.py

---

## 🚀 Quick Start (Development)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [Make](https://www.gnu.org/software/make/) (optional, for developer convenience)

### Local Environment Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-org/VendorVerse.git
   cd VendorVerse
   ```

2. **Set up environment variables:**

   ```bash
   cp .env.example .env
   ```

3. **Start services with Docker Compose:**

   ```bash
   docker compose up --build -d
   ```

4. **Apply database migrations:**

   ```bash
   docker compose exec web python manage.py migrate
   ```

5. **Create platform superadmin:**

   ```bash
   docker compose exec web python manage.py create_superadmin
   ```

6. **Seed initial demo data:**

   ```bash
   docker compose exec web python manage.py seed_data
   ```

7. **Access the application:**
   - **Storefront:** [http://localhost:8000](http://localhost:8000)
   - **Django Admin:** [http://localhost:8000/admin/](http://localhost:8000/admin/)
   - **API Documentation:** [http://localhost:8000/api/v1/docs/](http://localhost:8000/api/v1/docs/)
   - **Mailpit (Local Emails):** [http://localhost:8025](http://localhost:8025)

---

## 🛠️ Common Developer Commands

Using `make` (or run equivalent `docker compose` commands directly):

```bash
make run          # Start containers in background
make stop         # Stop containers
make test         # Run pytest suite with coverage
make lint         # Run Ruff linter checks
make format       # Format code with Ruff
make migrate      # Apply database migrations
make makemigrations # Create new migrations
make shell        # Open Django shell_plus
make logs         # Tail container logs
```

---

## 🤝 Contribution & Workflow

1. All development must follow the standards specified in [`12-coding-standards.md`](./docs/12-coding-standards.md).
2. Create topic branches off `develop` (`feature/*`, `bugfix/*`).
3. Ensure all tests pass (`make test`) and linting succeeds (`make lint`) before opening a PR.
4. Reference requirement IDs in commit messages and PR descriptions.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

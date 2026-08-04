# VendorVerse — Coding Standards

> **Document Version:** 1.0  
> **Last Updated:** 2026-07-22  
> **Status:** Approved  
> **Related Documents:** [Django Architecture](./06-django-architecture.md) · [Project Structure](./11-project-structure.md) · [Testing Strategy](./13-testing-strategy.md)

---

## 1. Python Coding Standards

### 1.1 Style Guide

VendorVerse follows **PEP 8** with enhancements enforced by **Ruff** (linter + formatter).

| Rule | Standard |
|---|---|
| Line length | 99 characters maximum |
| Indentation | 4 spaces (never tabs) |
| String quotes | Double quotes for strings (`"hello"`); single quotes for dict keys only when mixed (`'key'`) |
| Trailing commas | Always on multi-line collections, function arguments, and imports |
| Import ordering | stdlib → third-party → Django → project (enforced by Ruff isort) |
| Type hints | Encouraged on service layer functions and complex utilities; not required on views |

### 1.2 Import Organization

```python
# Standard library
import uuid
from datetime import timedelta
from decimal import Decimal

# Third-party
import stripe
from celery import shared_task

# Django
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

# Django REST Framework
from rest_framework import serializers, status
from rest_framework.response import Response

# Project apps (absolute imports only)
from apps.core.exceptions import InsufficientStockError
from apps.core.models import TimeStampedModel
from apps.products.services import ProductService
```

**Rules:**
- Always use absolute imports (`from apps.products.models import Product`)
- Never use wildcard imports (`from module import *`)
- Never use relative imports (`from .models import Product`) — absolute imports are clearer in a Django project

### 1.3 Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Classes | PascalCase | `ProductService`, `OrderStatusLog` |
| Functions / Methods | snake_case | `get_products_by_category()`, `place_order()` |
| Variables | snake_case | `order_total`, `is_active` |
| Constants | UPPER_SNAKE_CASE | `MAX_CART_ITEMS`, `ORDER_STATUS_PLACED` |
| Private methods | `_prefix` | `_calculate_commission()` |
| Module-level "constants" | UPPER_SNAKE_CASE | `DEFAULT_PAGE_SIZE = 20` |
| URL pattern names | `kebab-case` | `product-list`, `vendor-dashboard` |
| Template variables | snake_case | `{{ product.title }}`, `{{ order_items }}` |
| CSS classes | kebab-case (Tailwind utilities) | `product-card`, `btn-primary` |

### 1.4 Docstring Standard

All public functions, classes, and modules use Google-style docstrings:

```python
def place_order(*, customer, cart, shipping_address_id, coupon_code=None):
    """
    Creates an order from the customer's cart.

    Validates stock availability, calculates totals with commission splits,
    creates the order with pending payment status, and initiates the
    Stripe PaymentIntent.

    Args:
        customer: The User placing the order.
        cart: The Cart instance to convert to an order.
        shipping_address_id: UUID of the selected shipping address.
        coupon_code: Optional coupon code to apply.

    Returns:
        Tuple of (Order, stripe_client_secret) for payment processing.

    Raises:
        InsufficientStockError: If any cart item exceeds available stock.
        InvalidCouponError: If coupon_code is invalid or expired.
        AddressNotFoundError: If shipping_address_id doesn't exist.
    """
```

---

## 2. Django-Specific Standards

### 2.1 Model Standards

| Rule | Rationale |
|---|---|
| All models inherit from `TimeStampedModel` | Consistent audit timestamps |
| Define `__str__()` on every model | Readable admin and debugging |
| Define `class Meta` with `ordering`, `verbose_name`, `verbose_name_plural` | Consistent behavior and admin display |
| ForeignKey fields always specify `on_delete` and `related_name` | Explicit is better than implicit |
| Choices defined as class-level constants or TextChoices | Centralized, reusable, IDE-friendly |
| No business logic in models | Service layer handles business rules; models are data containers |
| `get_absolute_url()` on models with detail pages | Template `{{ object.get_absolute_url }}` works consistently |

### 2.2 View Standards

| Rule | Rationale |
|---|---|
| Views are thin — delegate to services | Reusable logic between web and API views |
| Template views use class-based views (CBVs) | Consistent patterns; mixins for permissions |
| API views use DRF `APIView` or `ViewSet` | DRF serialization and permission framework |
| Every view has explicit `permission_classes` (API) or mixin (web) | No accidentally public endpoints |
| HTMX detection via `request.htmx` (from `django-htmx`) | Clean partial vs. full template rendering |
| No database queries in templates | Queries in views/selectors; context passed to templates |

### 2.3 Service Layer Standards

| Rule | Rationale |
|---|---|
| Functions use keyword-only arguments (`*` separator) | Prevents positional argument errors |
| Functions are stateless (module-level functions, not classes) | Simple, testable, no hidden state |
| Raise domain exceptions, not HTTP exceptions | Decoupled from HTTP; views translate to responses |
| `@transaction.atomic` on write operations | Data consistency on multi-step mutations |
| Return model instances or simple dicts, not Response objects | Views handle serialization |

### 2.4 Serializer Standards

| Rule | Rationale |
|---|---|
| Separate `Read` and `Write` serializers when shapes differ | `ProductListSerializer` vs `ProductCreateSerializer` |
| Never put business logic in serializers | Serializers validate shape; services validate rules |
| Use `source` parameter for renamed fields | Clean API field names vs. model field names |
| Nested serializers for read; PKs/UUIDs for write | Avoid deep nesting on write operations |

---

## 3. Git Workflow

### 3.1 Branch Strategy

```mermaid
gitgraph
    commit id: "Initial commit"
    branch develop
    checkout develop
    commit id: "Setup project"
    branch feature/user-auth
    checkout feature/user-auth
    commit id: "Add user model"
    commit id: "Add auth views"
    checkout develop
    merge feature/user-auth
    branch feature/products
    checkout feature/products
    commit id: "Add product models"
    commit id: "Add product views"
    checkout develop
    merge feature/products
    checkout main
    merge develop tag: "v0.1.0"
```

| Branch | Purpose | Naming |
|---|---|---|
| `main` | Production-ready code; only merged from `develop` | Protected; no direct push |
| `develop` | Integration branch; all features merge here | Protected; PRs required |
| `feature/*` | New features | `feature/user-authentication`, `feature/product-catalog` |
| `bugfix/*` | Bug fixes | `bugfix/cart-quantity-validation` |
| `hotfix/*` | Critical production fixes | `hotfix/payment-processing-error` |
| `docs/*` | Documentation changes | `docs/api-documentation-update` |

### 3.2 Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

| Type | Usage |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Code style (formatting, no logic change) |
| `refactor` | Code restructuring (no behavior change) |
| `test` | Adding or modifying tests |
| `chore` | Build, config, tooling changes |
| `perf` | Performance improvements |

**Examples:**
```
feat(products): add product search with PostgreSQL FTS

Implements full-text search using SearchVector and SearchRank
with trigram similarity for typo tolerance.

Refs: FR-SRC-001
```

```
fix(cart): prevent negative quantity on cart item update

Added min=1 validation to CartItem quantity field.
Closes #45
```

### 3.3 Pull Request Process

| Step | Requirement |
|---|---|
| 1. Create branch | From `develop`; follow naming convention |
| 2. Implement | Follow coding standards; include tests |
| 3. Self-review | Run lint, tests, check migrations before PR |
| 4. Create PR | Use PR template; describe what and why |
| 5. CI passes | Lint + tests + migration check must pass |
| 6. Code review | Minimum 1 approval required |
| 7. Merge | Squash and merge into `develop` |

### 3.4 PR Checklist Template

```markdown
## Description
Brief description of changes.

## Type
- [ ] Feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Documentation

## Checklist
- [ ] Code follows project coding standards
- [ ] Tests added/updated for changes
- [ ] All tests pass locally
- [ ] No new linting warnings
- [ ] Migrations generated (if model changes)
- [ ] Documentation updated (if API/architecture changes)
- [ ] No secrets or credentials committed
- [ ] N+1 queries checked (if adding queries)
```

---

## 4. Linting & Formatting Configuration

### 4.1 Ruff Configuration (`.ruff.toml`)

```toml
line-length = 99
target-version = "py312"

[lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "S",    # flake8-bandit (security)
    "C4",   # flake8-comprehensions
    "DJ",   # flake8-django
    "T20",  # flake8-print
]
ignore = [
    "S101",  # allow assert in tests
    "S308",  # allow mark_safe in templates
]

[lint.per-file-ignores]
"*/tests/*" = ["S101"]
"*/migrations/*" = ["E501"]

[lint.isort]
known-first-party = ["apps", "config"]
known-django = ["django", "rest_framework"]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "DJANGO", "FIRSTPARTY", "LOCALFOLDER"]
```

### 4.2 Pre-commit Hooks (`.pre-commit-config.yaml`)

| Hook | Purpose |
|---|---|
| `ruff` | Lint Python code |
| `ruff-format` | Format Python code |
| `check-yaml` | Validate YAML files |
| `check-merge-conflict` | Detect merge conflict markers |
| `no-commit-to-branch` | Prevent direct commits to `main`/`develop` |
| `django-migration-check` | Ensure no missing migrations |

---

## 5. Documentation Standards

### 5.1 Code Documentation

| What | When | Format |
|---|---|---|
| Module docstring | Every `.py` file | Brief description of module purpose |
| Class docstring | Every class | Purpose, important attributes |
| Public function docstring | Every public function | Google-style with Args, Returns, Raises |
| Inline comments | Complex logic only | Explain "why", not "what" |
| TODO comments | Temporary; tracked in issues | `# TODO(username): description - #issue_number` |

### 5.2 App-Level Documentation

Each Django app has a `README.md` in its directory explaining:
- App purpose and boundaries
- Key models and their relationships
- Service layer functions (public API)
- Dependencies on other apps
- How to run app-specific tests

---

*← [Project Structure](./11-project-structure.md) · Next: [Testing Strategy →](./13-testing-strategy.md)*

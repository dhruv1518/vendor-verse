# VendorVerse — Project Structure

> **Document Version:** 1.0  
> **Last Updated:** 2026-07-22  
> **Status:** Approved  
> **Related Documents:** [Django Architecture](./06-django-architecture.md) · [Coding Standards](./12-coding-standards.md) · [Deployment Guide](./14-deployment-guide.md)

---

## 1. Repository Root Structure

```
vendorverse/                             # Repository root
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                       # CI pipeline (lint, test, build)
│   │   └── cd.yml                       # CD pipeline (deploy to staging/prod)
│   ├── PULL_REQUEST_TEMPLATE.md         # PR template with checklist
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
│
├── config/                              # Django project configuration
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                      # Shared settings
│   │   ├── development.py               # Dev overrides (DEBUG=True, local DB)
│   │   ├── staging.py                   # Staging overrides
│   │   ├── production.py                # Production overrides (security hardened)
│   │   └── test.py                      # Test overrides (in-memory, fast)
│   ├── urls.py                          # Root URL configuration
│   ├── wsgi.py                          # WSGI entry point
│   ├── asgi.py                          # ASGI entry point
│   └── celery.py                        # Celery app configuration
│
├── apps/                                # All Django apps
│   ├── __init__.py
│   ├── core/                            # Shared utilities and base classes
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                    # TimeStampedModel, PublicIDModel
│   │   ├── exceptions.py               # VendorVerseException hierarchy
│   │   ├── mixins.py                    # View mixins (VendorRequiredMixin, etc.)
│   │   ├── utils.py                     # General utilities
│   │   ├── validators.py               # Shared validators
│   │   ├── constants.py                 # Global constants
│   │   ├── pagination.py               # Custom pagination classes
│   │   ├── renderers.py                # Custom API response renderer
│   │   ├── middleware.py               # RequestIDMiddleware, TimezoneMiddleware
│   │   ├── context_processors.py       # Global template context
│   │   ├── templatetags/
│   │   │   ├── __init__.py
│   │   │   └── core_tags.py            # Custom template tags/filters
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── seed_data.py         # Seed initial data
│   │   │       └── create_superadmin.py # Create admin with proper role
│   │   └── tests/
│   │       └── __init__.py
│   │
│   ├── accounts/                        # User management & authentication
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models/
│   │   │   ├── __init__.py              # Exports User, UserProfile, Address, AuditLog
│   │   │   ├── user.py                  # Custom User model
│   │   │   ├── profile.py              # UserProfile model
│   │   │   ├── address.py              # Address model
│   │   │   └── audit.py                # AuditLog model
│   │   ├── managers.py                  # Custom UserManager
│   │   ├── services.py                  # Registration, profile update logic
│   │   ├── selectors.py                 # User queries
│   │   ├── serializers.py               # DRF serializers
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── web.py                   # Template views (profile, addresses)
│   │   │   └── api.py                   # API views (auth, profile)
│   │   ├── urls/
│   │   │   ├── __init__.py
│   │   │   ├── web.py                   # Browser URL patterns
│   │   │   └── api.py                   # API URL patterns
│   │   ├── forms.py                     # Profile, address forms
│   │   ├── permissions.py               # IsCustomer, IsAdmin permissions
│   │   ├── signals.py                   # Signal definitions
│   │   ├── receivers.py                 # Auto-create profile on User save
│   │   ├── tasks.py                     # Async tasks (send emails)
│   │   ├── constants.py                 # Role choices, auth constants
│   │   ├── adapters.py                  # Allauth account adapter
│   │   ├── templates/
│   │   │   └── accounts/
│   │   │       ├── login.html
│   │   │       ├── register.html
│   │   │       ├── profile.html
│   │   │       ├── addresses.html
│   │   │       ├── password_reset.html
│   │   │       ├── password_change.html
│   │   │       └── partials/
│   │   │           ├── _address_form.html
│   │   │           └── _address_list.html
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py
│   │   │   ├── test_services.py
│   │   │   ├── test_views.py
│   │   │   ├── test_api.py
│   │   │   └── factories.py
│   │   └── migrations/
│   │       └── __init__.py
│   │
│   ├── vendors/                         # Vendor management
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── vendor.py                # Vendor model
│   │   │   ├── application.py           # VendorApplication model
│   │   │   ├── storefront.py            # Storefront model
│   │   │   └── subscription.py          # SubscriptionTier model
│   │   ├── managers.py
│   │   ├── services.py
│   │   ├── selectors.py
│   │   ├── serializers.py
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── web.py                   # Dashboard, storefront views
│   │   │   └── api.py
│   │   ├── urls/
│   │   │   ├── __init__.py
│   │   │   ├── web.py
│   │   │   └── api.py
│   │   ├── forms.py
│   │   ├── filters.py
│   │   ├── permissions.py               # IsVendor, IsVendorOwner
│   │   ├── signals.py
│   │   ├── receivers.py
│   │   ├── tasks.py
│   │   ├── constants.py
│   │   ├── templates/
│   │   │   └── vendors/
│   │   │       ├── dashboard.html
│   │   │       ├── application_form.html
│   │   │       ├── storefront_public.html
│   │   │       ├── storefront_edit.html
│   │   │       ├── earnings.html
│   │   │       └── partials/
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py
│   │   │   ├── test_services.py
│   │   │   ├── test_views.py
│   │   │   ├── test_api.py
│   │   │   └── factories.py
│   │   └── migrations/
│   │       └── __init__.py
│   │
│   ├── products/                        # Product catalog
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── category.py
│   │   │   ├── product.py
│   │   │   ├── image.py
│   │   │   ├── variant.py
│   │   │   └── tag.py
│   │   ├── managers.py                  # PublishedProductManager
│   │   ├── services.py
│   │   ├── selectors.py                 # Complex search/filter queries
│   │   ├── serializers.py
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── web.py                   # Listing, detail, vendor product CRUD
│   │   │   └── api.py
│   │   ├── urls/
│   │   │   ├── __init__.py
│   │   │   ├── web.py
│   │   │   └── api.py
│   │   ├── forms.py
│   │   ├── filters.py                   # ProductFilter (django-filter)
│   │   ├── permissions.py
│   │   ├── signals.py
│   │   ├── receivers.py                 # Cache invalidation, search vector update
│   │   ├── tasks.py                     # Image processing
│   │   ├── constants.py                 # Product status choices
│   │   ├── search.py                    # PostgreSQL FTS utilities
│   │   ├── templates/
│   │   │   └── products/
│   │   │       ├── product_list.html
│   │   │       ├── product_detail.html
│   │   │       ├── product_form.html
│   │   │       ├── category_list.html
│   │   │       ├── search_results.html
│   │   │       └── partials/
│   │   │           ├── _product_card.html
│   │   │           ├── _product_grid.html
│   │   │           ├── _filter_sidebar.html
│   │   │           └── _search_suggestions.html
│   │   ├── tests/
│   │   │   └── ...
│   │   └── migrations/
│   │       └── __init__.py
│   │
│   ├── cart/                            # Shopping cart
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                    # Cart, CartItem (small app — single file)
│   │   ├── services.py
│   │   ├── selectors.py
│   │   ├── serializers.py
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── web.py
│   │   │   └── api.py
│   │   ├── urls/
│   │   │   ├── __init__.py
│   │   │   ├── web.py
│   │   │   └── api.py
│   │   ├── forms.py
│   │   ├── constants.py
│   │   ├── templates/
│   │   │   └── cart/
│   │   │       ├── cart_detail.html
│   │   │       └── partials/
│   │   │           ├── _cart_item.html
│   │   │           ├── _cart_totals.html
│   │   │           └── _cart_badge.html
│   │   ├── tests/
│   │   │   └── ...
│   │   └── migrations/
│   │       └── __init__.py
│   │
│   ├── orders/                          # Order management
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── order.py
│   │   │   ├── order_item.py
│   │   │   ├── status_log.py
│   │   │   └── return_request.py
│   │   ├── managers.py
│   │   ├── services.py                  # Order placement, cancellation, status transitions
│   │   ├── selectors.py
│   │   ├── serializers.py
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── web.py                   # Checkout, order history, order detail
│   │   │   └── api.py
│   │   ├── urls/
│   │   │   ├── __init__.py
│   │   │   ├── web.py
│   │   │   └── api.py
│   │   ├── forms.py
│   │   ├── filters.py
│   │   ├── permissions.py               # IsOrderOwner
│   │   ├── signals.py                   # order_placed, order_status_changed
│   │   ├── receivers.py
│   │   ├── tasks.py                     # Invoice generation, auto-delivery
│   │   ├── constants.py                 # OrderStatus, allowed transitions
│   │   ├── state_machine.py             # Order status transition logic
│   │   ├── invoice.py                   # PDF invoice generation
│   │   ├── templates/
│   │   │   └── orders/
│   │   │       ├── checkout.html
│   │   │       ├── checkout_confirm.html
│   │   │       ├── order_confirmation.html
│   │   │       ├── order_list.html
│   │   │       ├── order_detail.html
│   │   │       └── partials/
│   │   ├── tests/
│   │   │   └── ...
│   │   └── migrations/
│   │       └── __init__.py
│   │
│   ├── payments/                        # Payment processing
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── payment.py
│   │   │   └── transaction.py
│   │   ├── services.py                  # Stripe integration, payout logic
│   │   ├── serializers.py
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   └── api.py                   # Webhook endpoint
│   │   ├── urls/
│   │   │   ├── __init__.py
│   │   │   └── api.py
│   │   ├── webhooks.py                  # Stripe webhook handlers
│   │   ├── constants.py
│   │   ├── signals.py                   # payment_completed, payout_processed
│   │   ├── receivers.py
│   │   ├── tasks.py                     # Process payouts, reconciliation
│   │   ├── tests/
│   │   │   └── ...
│   │   └── migrations/
│   │       └── __init__.py
│   │
│   ├── reviews/                         # Reviews & ratings
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── review.py
│   │   │   ├── review_image.py
│   │   │   └── review_response.py
│   │   ├── services.py
│   │   ├── selectors.py
│   │   ├── serializers.py
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── web.py
│   │   │   └── api.py
│   │   ├── urls/
│   │   │   ├── __init__.py
│   │   │   ├── web.py
│   │   │   └── api.py
│   │   ├── forms.py
│   │   ├── permissions.py               # IsReviewAuthor
│   │   ├── moderation.py                # Auto-moderation rules
│   │   ├── signals.py
│   │   ├── receivers.py                 # Update product/vendor ratings
│   │   ├── tasks.py
│   │   ├── constants.py
│   │   ├── templates/
│   │   │   └── reviews/
│   │   │       └── partials/
│   │   │           ├── _review_card.html
│   │   │           ├── _review_form.html
│   │   │           └── _star_rating.html
│   │   ├── tests/
│   │   │   └── ...
│   │   └── migrations/
│   │       └── __init__.py
│   │
│   ├── notifications/                   # Notification system
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                    # Notification, NotificationPreference
│   │   ├── services.py                  # Create notification, send email
│   │   ├── selectors.py
│   │   ├── serializers.py
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── web.py
│   │   │   └── api.py
│   │   ├── urls/
│   │   │   ├── __init__.py
│   │   │   ├── web.py
│   │   │   └── api.py
│   │   ├── signals.py
│   │   ├── receivers.py                 # Listen for order/vendor events
│   │   ├── tasks.py                     # Async email sending
│   │   ├── constants.py                 # Notification type choices
│   │   ├── templates/
│   │   │   └── notifications/
│   │   │       └── partials/
│   │   │           └── _notification_list.html
│   │   ├── tests/
│   │   │   └── ...
│   │   └── migrations/
│   │       └── __init__.py
│   │
│   ├── analytics/                       # Dashboards & analytics
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── services.py                  # Aggregation queries
│   │   ├── selectors.py                 # Dashboard data queries
│   │   ├── serializers.py
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── web.py                   # Dashboard views
│   │   │   └── api.py
│   │   ├── urls/
│   │   │   ├── __init__.py
│   │   │   ├── web.py
│   │   │   └── api.py
│   │   ├── tasks.py                     # Report generation
│   │   ├── constants.py
│   │   ├── tests/
│   │   │   └── ...
│   │   └── migrations/                  # No models — no migrations
│   │       └── __init__.py
│   │
│   └── administration/                  # Platform administration
│       ├── __init__.py
│       ├── apps.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── site_config.py           # SiteConfiguration singleton
│       │   └── coupon.py                # Coupon, CouponUsage
│       ├── services.py
│       ├── selectors.py
│       ├── serializers.py
│       ├── views/
│       │   ├── __init__.py
│       │   ├── web.py                   # Admin panel views
│       │   └── api.py
│       ├── urls/
│       │   ├── __init__.py
│       │   ├── web.py
│       │   └── api.py
│       ├── forms.py
│       ├── permissions.py
│       ├── tasks.py
│       ├── constants.py
│       ├── templates/
│       │   └── administration/
│       │       ├── dashboard.html
│       │       ├── vendor_applications.html
│       │       ├── vendor_management.html
│       │       ├── moderation_products.html
│       │       ├── moderation_reviews.html
│       │       ├── categories.html
│       │       ├── commissions.html
│       │       ├── site_settings.html
│       │       └── partials/
│       ├── tests/
│       │   └── ...
│       └── migrations/
│           └── __init__.py
│
├── templates/                           # Global templates
│   ├── base.html
│   ├── layouts/
│   │   ├── main.html
│   │   ├── vendor_dashboard.html
│   │   ├── admin_panel.html
│   │   └── auth.html
│   ├── includes/
│   │   ├── _navbar.html
│   │   ├── _footer.html
│   │   ├── _messages.html
│   │   ├── _pagination.html
│   │   ├── _breadcrumbs.html
│   │   └── _search_bar.html
│   ├── components/
│   │   ├── _product_card.html
│   │   ├── _vendor_card.html
│   │   ├── _review_card.html
│   │   ├── _star_rating.html
│   │   ├── _price_display.html
│   │   ├── _empty_state.html
│   │   ├── _modal.html
│   │   └── _order_status_badge.html
│   ├── errors/
│   │   ├── 400.html
│   │   ├── 403.html
│   │   ├── 404.html
│   │   └── 500.html
│   └── emails/
│       ├── base_email.html
│       ├── order_confirmation.html
│       ├── vendor_approved.html
│       └── password_reset.html
│
├── static/                              # Static assets
│   ├── css/
│   │   ├── input.css                    # Tailwind source
│   │   ├── output.css                   # Tailwind compiled (gitignored in dev)
│   │   └── custom.css                   # Custom overrides
│   ├── js/
│   │   ├── htmx.min.js
│   │   ├── alpine.min.js
│   │   ├── app.js
│   │   └── components/
│   │       ├── cart.js
│   │       ├── search.js
│   │       └── notifications.js
│   ├── images/
│   │   ├── logo.svg
│   │   ├── favicon.ico
│   │   └── placeholders/
│   └── fonts/
│
├── media/                               # User uploads (dev only; S3 in prod)
│
├── docs/                                # Project documentation
│   ├── 01-project-overview.md
│   ├── 02-software-requirements.md
│   ├── ...
│   └── PROJECT_CONTEXT.md
│
├── scripts/                             # Utility scripts
│   ├── entrypoint.sh                    # Docker entrypoint
│   ├── wait_for_db.py                   # Wait for DB readiness
│   └── backup_db.sh                     # Database backup script
│
├── .env.example                         # Environment variables template
├── .gitignore
├── .pre-commit-config.yaml              # Pre-commit hook config
├── .ruff.toml                           # Ruff linter config
├── docker-compose.yml                   # Development services
├── docker-compose.prod.yml              # Production overrides
├── Dockerfile                           # Application container
├── Makefile                             # Common development commands
├── manage.py                            # Django management entry point
├── pyproject.toml                       # Python project config (black, isort)
├── requirements/
│   ├── base.txt                         # Shared dependencies
│   ├── development.txt                  # Dev-only (debug-toolbar, factory-boy)
│   ├── production.txt                   # Prod-only (gunicorn, sentry)
│   └── test.txt                         # Test-only (pytest, coverage)
├── tailwind.config.js                   # Tailwind configuration
├── package.json                         # Node dependencies (Tailwind)
└── README.md                            # Project README
```

---

## 2. Naming Conventions

### 2.1 Files

| Type | Convention | Example |
|---|---|---|
| Python modules | `snake_case.py` | `order_item.py`, `state_machine.py` |
| Templates | `snake_case.html` | `product_list.html`, `_product_card.html` |
| Partial templates | `_prefixed.html` | `_navbar.html`, `_cart_item.html` |
| CSS files | `kebab-case.css` or `snake_case.css` | `output.css`, `custom.css` |
| JavaScript files | `camelCase.js` or `kebab-case.js` | `notifications.js`, `app.js` |
| Migration files | Auto-generated | `0001_initial.py`, `0002_add_product_slug.py` |

### 2.2 Django Models

| Convention | Example |
|---|---|
| Model class: `PascalCase` singular | `Product`, `OrderItem`, `VendorApplication` |
| Field: `snake_case` | `first_name`, `created_at`, `is_active` |
| ForeignKey field: model name in `snake_case` | `vendor`, `category`, `customer` |
| Boolean field: `is_` or `has_` prefix | `is_active`, `is_featured`, `has_variants` |
| Reverse relation: explicit `related_name` | `products` (from Category), `order_items` (from Order) |

### 2.3 URLs

| Convention | Example |
|---|---|
| URL paths: `kebab-case/` | `/vendor/dashboard/`, `/order-history/` |
| URL names: `app:entity-action` | `products:list`, `orders:detail`, `vendors:dashboard` |
| API paths: `/api/v1/resource/` | `/api/v1/products/`, `/api/v1/cart/items/` |

---

## 3. Configuration Files Explained

| File | Purpose |
|---|---|
| `.env.example` | Template for environment variables; copied to `.env` locally |
| `.gitignore` | Excludes `.env`, `media/`, `__pycache__/`, `node_modules/`, `staticfiles/`, `*.pyc` |
| `.pre-commit-config.yaml` | Runs Ruff lint + format, check migrations, check YAML on commit |
| `.ruff.toml` | Ruff linter/formatter configuration matching project standards |
| `pyproject.toml` | Python tooling config (pytest, coverage, isort settings) |
| `Makefile` | Developer convenience (`make run`, `make test`, `make migrate`, `make lint`) |
| `tailwind.config.js` | Tailwind CSS customization (colors, fonts, extend) |
| `package.json` | Node deps for Tailwind CLI |

---

*← [Security & Performance](./10-security-performance.md) · Next: [Coding Standards →](./12-coding-standards.md)*

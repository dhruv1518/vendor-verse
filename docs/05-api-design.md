# VendorVerse — API Design

> **Document Version:** 1.0  
> **Last Updated:** 2026-07-22  
> **Status:** Approved  
> **Related Documents:** [Software Requirements](./02-software-requirements.md) · [System Architecture](./03-system-architecture.md) · [Authentication & Authorization](./09-authentication-authorization.md)

---

## 1. API Strategy

### 1.1 Dual-Interface Architecture

VendorVerse serves content through two interfaces:

| Interface | Technology | Purpose | Consumers |
|---|---|---|---|
| **Server-Rendered Views** | Django Templates + HTMX | Primary web experience | Browsers |
| **REST API** | Django REST Framework | Programmatic access, future mobile app | API clients, HTMX (partial), mobile (future) |

HTMX requests may hit either Django views (returning HTML fragments) or DRF endpoints (returning JSON that Alpine.js renders). The pattern depends on the interaction:

- **Page loads, navigation, pagination:** Django views → HTML fragments via HTMX
- **Data mutations (cart add, review submit):** DRF API → JSON → HTMX/Alpine.js handles response

### 1.2 API Design Principles

| Principle | Implementation |
|---|---|
| **RESTful** | Resources as nouns; HTTP verbs for actions; HATEOAS links where useful |
| **Versioned** | URL prefix versioning (`/api/v1/`) |
| **Consistent** | Uniform response envelope, error format, pagination |
| **Stateless** | JWT authentication for API; no server-side session required |
| **Documented** | OpenAPI 3.0 schema via drf-spectacular |
| **Secure** | Rate limiting, input validation, permission checks on every endpoint |

---

## 2. API Base Configuration

### 2.1 Base URL

```
Production:  https://vendorverse.com/api/v1/
Development: http://localhost:8000/api/v1/
```

### 2.2 Standard Response Envelope

**Success Response:**
```json
{
  "status": "success",
  "data": { ... },
  "meta": {
    "timestamp": "2026-07-22T12:00:00Z",
    "request_id": "req_abc123"
  }
}
```

**Paginated Response:**
```json
{
  "status": "success",
  "data": [ ... ],
  "meta": {
    "timestamp": "2026-07-22T12:00:00Z",
    "request_id": "req_abc123"
  },
  "pagination": {
    "count": 150,
    "page": 1,
    "page_size": 20,
    "total_pages": 8,
    "next": "/api/v1/products/?page=2",
    "previous": null
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more fields have validation errors.",
    "details": [
      {
        "field": "price",
        "message": "Ensure this value is greater than 0.",
        "code": "min_value"
      }
    ]
  },
  "meta": {
    "timestamp": "2026-07-22T12:00:00Z",
    "request_id": "req_abc123"
  }
}
```

### 2.3 Standard Error Codes

| HTTP Status | Error Code | Description |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Request body failed validation |
| 400 | `BAD_REQUEST` | Malformed request |
| 401 | `AUTHENTICATION_REQUIRED` | Missing or invalid token |
| 401 | `TOKEN_EXPIRED` | JWT access token expired |
| 403 | `PERMISSION_DENIED` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource does not exist |
| 409 | `CONFLICT` | Resource state conflict (e.g., duplicate review) |
| 422 | `BUSINESS_RULE_VIOLATION` | Business logic constraint (e.g., insufficient stock) |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error (details logged, not exposed) |

### 2.4 Pagination Strategy

| Parameter | Default | Max | Description |
|---|---|---|---|
| `page` | 1 | — | Page number (1-indexed) |
| `page_size` | 20 | 100 | Items per page |

Cursor-based pagination for high-throughput endpoints (notifications, audit logs).

### 2.5 Filtering & Sorting

```
GET /api/v1/products/?category=electronics&price_min=10&price_max=100&rating_min=4&sort=-price&page=1&page_size=20
```

| Convention | Format | Example |
|---|---|---|
| Filtering | `field=value` | `status=published` |
| Range filtering | `field_min=X&field_max=Y` | `price_min=10&price_max=100` |
| Sorting | `sort=field` (asc) or `sort=-field` (desc) | `sort=-created_at` |
| Searching | `search=term` | `search=laptop` |
| Multi-value | `field=val1,val2` | `status=published,draft` |

---

## 3. Endpoint Inventory

### 3.1 Authentication Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/auth/register/` | Public | Register new user |
| POST | `/api/v1/auth/login/` | Public | Login (returns JWT) |
| POST | `/api/v1/auth/token/refresh/` | Public | Refresh JWT access token |
| POST | `/api/v1/auth/logout/` | Authenticated | Blacklist refresh token |
| POST | `/api/v1/auth/password/reset/` | Public | Request password reset email |
| POST | `/api/v1/auth/password/reset/confirm/` | Public | Confirm password reset |
| POST | `/api/v1/auth/password/change/` | Authenticated | Change password |
| POST | `/api/v1/auth/email/verify/` | Public | Verify email address |
| GET | `/api/v1/auth/social/{provider}/` | Public | Initiate social auth |
| POST | `/api/v1/auth/social/{provider}/callback/` | Public | Social auth callback |

#### Register — Request/Response

**Request:**
```json
POST /api/v1/auth/register/
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "Priya",
  "last_name": "Sharma"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "uuid-public-id",
      "email": "user@example.com",
      "first_name": "Priya",
      "last_name": "Sharma",
      "role": "customer"
    },
    "message": "Verification email sent. Please verify your email to activate your account."
  }
}
```

#### Login — Request/Response

**Request:**
```json
POST /api/v1/auth/login/
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "refresh": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "id": "uuid-public-id",
      "email": "user@example.com",
      "first_name": "Priya",
      "last_name": "Sharma",
      "role": "customer",
      "avatar_url": "/media/avatars/user_42.webp"
    }
  }
}
```

---

### 3.2 User Endpoints

| Method | Endpoint | Auth | Permission | Description |
|---|---|---|---|---|
| GET | `/api/v1/users/me/` | Required | Self | Get current user profile |
| PATCH | `/api/v1/users/me/` | Required | Self | Update profile |
| GET | `/api/v1/users/me/addresses/` | Required | Self | List addresses |
| POST | `/api/v1/users/me/addresses/` | Required | Self | Create address |
| PATCH | `/api/v1/users/me/addresses/{id}/` | Required | Self | Update address |
| DELETE | `/api/v1/users/me/addresses/{id}/` | Required | Self | Delete address |
| POST | `/api/v1/users/me/addresses/{id}/set-default/` | Required | Self | Set as default |
| GET | `/api/v1/users/me/wishlist/` | Required | Self | List wishlist items |
| POST | `/api/v1/users/me/wishlist/` | Required | Self | Add to wishlist |
| DELETE | `/api/v1/users/me/wishlist/{product_id}/` | Required | Self | Remove from wishlist |

---

### 3.3 Vendor Endpoints

| Method | Endpoint | Auth | Permission | Description |
|---|---|---|---|---|
| POST | `/api/v1/vendors/apply/` | Required | Customer | Submit vendor application |
| GET | `/api/v1/vendors/application/` | Required | Self | Check application status |
| GET | `/api/v1/vendors/{slug}/` | Public | — | View vendor storefront |
| GET | `/api/v1/vendors/{slug}/products/` | Public | — | List vendor's products |
| GET | `/api/v1/vendors/{slug}/reviews/` | Public | — | List vendor reviews |
| PATCH | `/api/v1/vendors/me/` | Required | Vendor | Update vendor profile |
| PATCH | `/api/v1/vendors/me/storefront/` | Required | Vendor | Update storefront |
| GET | `/api/v1/vendors/me/dashboard/` | Required | Vendor | Dashboard summary |
| GET | `/api/v1/vendors/me/earnings/` | Required | Vendor | Earnings breakdown |
| POST | `/api/v1/vendors/me/earnings/withdraw/` | Required | Vendor | Request payout |
| GET | `/api/v1/vendors/me/orders/` | Required | Vendor | Vendor's order items |
| PATCH | `/api/v1/vendors/me/orders/{id}/status/` | Required | Vendor | Update order item status |

---

### 3.4 Product Endpoints

| Method | Endpoint | Auth | Permission | Description |
|---|---|---|---|---|
| GET | `/api/v1/products/` | Public | — | List/search products |
| GET | `/api/v1/products/{slug}/` | Public | — | Product detail |
| POST | `/api/v1/products/` | Required | Vendor | Create product |
| PATCH | `/api/v1/products/{slug}/` | Required | Vendor (owner) | Update product |
| DELETE | `/api/v1/products/{slug}/` | Required | Vendor (owner) | Archive product |
| POST | `/api/v1/products/{slug}/images/` | Required | Vendor (owner) | Upload image |
| DELETE | `/api/v1/products/{slug}/images/{id}/` | Required | Vendor (owner) | Delete image |
| POST | `/api/v1/products/{slug}/variants/` | Required | Vendor (owner) | Add variant |
| PATCH | `/api/v1/products/{slug}/variants/{id}/` | Required | Vendor (owner) | Update variant |
| DELETE | `/api/v1/products/{slug}/variants/{id}/` | Required | Vendor (owner) | Delete variant |
| GET | `/api/v1/products/{slug}/reviews/` | Public | — | List product reviews |

---

### 3.5 Category Endpoints

| Method | Endpoint | Auth | Permission | Description |
|---|---|---|---|---|
| GET | `/api/v1/categories/` | Public | — | List top-level categories |
| GET | `/api/v1/categories/{slug}/` | Public | — | Category detail + children |
| GET | `/api/v1/categories/tree/` | Public | — | Full category tree |

---

### 3.6 Search Endpoints

| Method | Endpoint | Auth | Permission | Description |
|---|---|---|---|---|
| GET | `/api/v1/search/` | Public | — | Full-text product search |
| GET | `/api/v1/search/suggestions/` | Public | — | Autocomplete suggestions |

#### Search — Query Parameters

| Parameter | Type | Description |
|---|---|---|
| `q` | string | Search query (required) |
| `category` | string | Category slug filter |
| `price_min` | decimal | Minimum price |
| `price_max` | decimal | Maximum price |
| `rating_min` | integer | Minimum rating (1-5) |
| `vendor` | string | Vendor slug filter |
| `in_stock` | boolean | Only in-stock products |
| `sort` | string | Sort field: relevance, price, -price, rating, newest |

---

### 3.7 Cart Endpoints

| Method | Endpoint | Auth | Permission | Description |
|---|---|---|---|---|
| GET | `/api/v1/cart/` | Required | Self | Get cart with items |
| POST | `/api/v1/cart/items/` | Required | Self | Add item to cart |
| PATCH | `/api/v1/cart/items/{id}/` | Required | Self | Update quantity |
| DELETE | `/api/v1/cart/items/{id}/` | Required | Self | Remove item |
| DELETE | `/api/v1/cart/` | Required | Self | Clear cart |
| POST | `/api/v1/cart/validate/` | Required | Self | Validate cart for checkout |

#### Add to Cart — Request/Response

**Request:**
```json
POST /api/v1/cart/items/
{
  "product_id": "uuid-public-id",
  "variant_id": "uuid-public-id",
  "quantity": 2
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "cart": {
      "item_count": 3,
      "total": "149.97",
      "vendors": [
        {
          "vendor_name": "TechStore",
          "vendor_slug": "techstore",
          "items": [
            {
              "id": "uuid",
              "product_title": "Wireless Mouse",
              "variant_name": "Black",
              "quantity": 2,
              "unit_price": "29.99",
              "line_total": "59.98",
              "in_stock": true,
              "max_quantity": 10
            }
          ],
          "subtotal": "59.98"
        }
      ]
    }
  }
}
```

---

### 3.8 Order & Checkout Endpoints

| Method | Endpoint | Auth | Permission | Description |
|---|---|---|---|---|
| POST | `/api/v1/checkout/` | Required | Customer | Initiate checkout (create order) |
| POST | `/api/v1/checkout/confirm/` | Required | Customer | Confirm payment |
| GET | `/api/v1/orders/` | Required | Customer | List customer orders |
| GET | `/api/v1/orders/{order_number}/` | Required | Customer/Vendor | Order detail |
| POST | `/api/v1/orders/{order_number}/cancel/` | Required | Customer | Cancel order |
| POST | `/api/v1/orders/{order_number}/items/{id}/return/` | Required | Customer | Request return |
| GET | `/api/v1/orders/{order_number}/invoice/` | Required | Customer/Vendor | Download invoice PDF |

#### Checkout — Request/Response

**Request:**
```json
POST /api/v1/checkout/
{
  "shipping_address_id": "uuid-public-id",
  "notes": "Please leave at the door",
  "coupon_code": "SAVE10"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "order": {
      "order_number": "ORD-20260722-0001",
      "status": "pending_payment",
      "items": [ ... ],
      "subtotal": "149.97",
      "shipping_total": "9.99",
      "discount_total": "14.99",
      "tax_total": "0.00",
      "grand_total": "144.97"
    },
    "payment": {
      "client_secret": "pi_xxx_secret_xxx",
      "publishable_key": "pk_test_xxx"
    }
  }
}
```

---

### 3.9 Review Endpoints

| Method | Endpoint | Auth | Permission | Description |
|---|---|---|---|---|
| POST | `/api/v1/products/{slug}/reviews/` | Required | Customer (purchased) | Create review |
| PATCH | `/api/v1/reviews/{id}/` | Required | Author | Update review |
| DELETE | `/api/v1/reviews/{id}/` | Required | Author/Admin | Delete review |
| POST | `/api/v1/reviews/{id}/helpful/` | Required | Authenticated | Mark as helpful |
| POST | `/api/v1/reviews/{id}/response/` | Required | Vendor (product owner) | Vendor response |

---

### 3.10 Notification Endpoints

| Method | Endpoint | Auth | Permission | Description |
|---|---|---|---|---|
| GET | `/api/v1/notifications/` | Required | Self | List notifications |
| GET | `/api/v1/notifications/unread-count/` | Required | Self | Get unread count |
| POST | `/api/v1/notifications/{id}/read/` | Required | Self | Mark as read |
| POST | `/api/v1/notifications/read-all/` | Required | Self | Mark all as read |
| GET | `/api/v1/notifications/preferences/` | Required | Self | Get preferences |
| PATCH | `/api/v1/notifications/preferences/` | Required | Self | Update preferences |

---

### 3.11 Admin Endpoints

| Method | Endpoint | Auth | Permission | Description |
|---|---|---|---|---|
| GET | `/api/v1/admin/dashboard/` | Required | Admin | Platform dashboard data |
| GET | `/api/v1/admin/vendors/` | Required | Admin | List all vendors |
| PATCH | `/api/v1/admin/vendors/{id}/status/` | Required | Admin | Approve/suspend/ban vendor |
| GET | `/api/v1/admin/applications/` | Required | Admin | Pending vendor applications |
| PATCH | `/api/v1/admin/applications/{id}/` | Required | Admin | Approve/reject application |
| GET | `/api/v1/admin/moderation/products/` | Required | Admin | Products pending moderation |
| PATCH | `/api/v1/admin/moderation/products/{id}/` | Required | Admin | Approve/reject product |
| GET | `/api/v1/admin/moderation/reviews/` | Required | Admin | Reviews pending moderation |
| PATCH | `/api/v1/admin/moderation/reviews/{id}/` | Required | Admin | Approve/reject review |
| GET | `/api/v1/admin/analytics/` | Required | Admin | Platform analytics |
| PATCH | `/api/v1/admin/configuration/` | Required | Admin | Update site configuration |
| GET | `/api/v1/admin/commission-tiers/` | Required | Admin | List commission tiers |
| PATCH | `/api/v1/admin/commission-tiers/{id}/` | Required | Admin | Update commission tier |

---

## 4. Rate Limiting

| Endpoint Group | Limit | Window | Scope |
|---|---|---|---|
| Authentication (login, register) | 10 requests | 1 minute | Per IP |
| Password reset | 3 requests | 15 minutes | Per IP |
| API (authenticated) | 100 requests | 1 minute | Per user |
| API (anonymous) | 30 requests | 1 minute | Per IP |
| Search | 60 requests | 1 minute | Per IP/user |
| File upload | 10 requests | 1 minute | Per user |
| Checkout | 5 requests | 1 minute | Per user |

**Implementation:** DRF's built-in throttling classes + `django-ratelimit` for view-based endpoints.

**Response (429):**
```json
{
  "status": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Request was throttled. Expected available in 45 seconds.",
    "retry_after": 45
  }
}
```

---

## 5. API Documentation

### 5.1 OpenAPI/Swagger

Generated automatically by `drf-spectacular`:

| URL | Purpose |
|---|---|
| `/api/v1/schema/` | OpenAPI 3.0 JSON schema |
| `/api/v1/docs/` | Swagger UI (interactive) |
| `/api/v1/redoc/` | ReDoc (readable documentation) |

### 5.2 Versioning Strategy

| Version | Status | Support |
|---|---|---|
| `v1` | Current | Active development |
| `v2` (future) | Planning | When breaking changes needed |

**Deprecation policy:** Minimum 6-month notice before removing API version. Deprecated endpoints return `Sunset` header.

---

*← [Database Design](./04-database-design.md) · Next: [Django Architecture →](./06-django-architecture.md)*

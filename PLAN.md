# VendorVerse Simplified Implementation Plan (College Project Edition)

This is the implementation plan simplified for a college project. All external services (like Stripe), containerization (Docker), background workers (Celery/Redis), and API tokens (JWT) have been removed. The project focuses purely on standard Django frontend, backend, and local database CRUD operations.

## Removed from the plan:
1. **Stripe Integration**: Removed completely. Replaced with a **Mock Checkout System** that simulates card payments locally.
2. **Docker & Docker Compose**: Removed. Run locally using standard `python manage.py runserver`.
3. **Redis & Celery**: Removed.
4. **JWT API Auth**: Removed.
5. **Amazon S3 Storage**: Removed. File uploads saved locally.
6. **Playwright E2E Testing**: Removed.
7. **Sentry & APM**: Removed.

---

## Phase 0: Foundation

### [x] Task 1 — Django Project Setup
- **Page/Feature Name**: Initial Django Setup
- **Objective**: Initialize the Django project, configure settings, and set up the database (Supabase PostgreSQL).
- **Dependencies**: None
- **Files**: `config/settings.py`, `manage.py`, `requirements.txt`
- **Expected Output**: A running local Django project.
- **Completion Criteria**: `python manage.py runserver` starts successfully and the default Django page is accessible.

### [x] Task 2 — Core App Foundation
- **Page/Feature Name**: Base Models & Utilities
- **Objective**: Create the core app with base models (`TimeStampedModel`, `PublicIDModel`) and shared utility classes.
- **Dependencies**: Task 1
- **Files**: `apps/core/models.py`, `apps/core/exceptions.py`
- **Expected Output**: Base classes for audit fields and UUID public identifiers.
- **Completion Criteria**: Migrations generated and applied without errors.

### [x] Task 3 — Base Template (base.html)
- **Page/Feature Name**: Global HTML Shell & Tailwind Setup
- **Objective**: Set up Tailwind CSS (via CDN or simple static asset) and the global HTML shell (`base.html`).
- **Dependencies**: Task 1
- **Files**: `templates/base.html`, `static/css/tailwind.css`
- **Expected Output**: A styled empty page base.
- **Completion Criteria**: `base.html` renders with Tailwind styles correctly applied.

### [x] Task 4 — Navigation Bar Component
- **Page/Feature Name**: Top Navigation Bar
- **Objective**: Create the top navigation bar with the logo, search bar placeholder, and authentication links.
- **Dependencies**: Task 3
- **Files**: `templates/includes/navbar.html`, `templates/base.html` (include tag)
- **Expected Output**: Responsive navbar on all pages.
- **Completion Criteria**: Navbar is visible, adapts to mobile/desktop, and links correctly.

### [x] Task 5 — Footer Component
- **Page/Feature Name**: Global Footer
- **Objective**: Create the global footer component containing basic site links.
- **Dependencies**: Task 3
- **Files**: `templates/includes/footer.html`, `templates/base.html` (include tag)
- **Expected Output**: Standard footer on all pages.
- **Completion Criteria**: Footer renders consistently at the bottom of the page.

---

## Phase 1: Authentication & User Management

### [x] Task 6 — Custom User Model
- **Page/Feature Name**: User Database Model
- **Objective**: Implement a custom user model using email as the primary identifier (no username) and role fields.
- **Dependencies**: Task 2
- **Files**: `apps/accounts/models.py`, `apps/accounts/admin.py`, `config/settings.py`
- **Expected Output**: `User` model with email login capability.
- **Completion Criteria**: Can create a superuser via CLI and log into Django Admin using an email address.

### [x] Task 7 — Django Allauth Integration
- **Page/Feature Name**: Authentication Backend Setup
- **Objective**: Configure `django-allauth` for registration, login, and session management.
- **Dependencies**: Task 6
- **Files**: `config/settings.py`, `config/urls.py`
- **Expected Output**: Standard backend routing for authentication.
- **Completion Criteria**: Allauth accounts endpoints are wired up correctly.

### [x] Task 8 — Registration Page
- **Page/Feature Name**: Sign Up UI
- **Objective**: Create a custom signup page overriding Allauth defaults.
- **Dependencies**: Task 3, Task 7
- **Files**: `templates/account/signup.html`, `apps/accounts/forms.py`
- **Expected Output**: Functional registration page matching the Design System.
- **Completion Criteria**: User can successfully register and is redirected to log in or home.

### [x] Task 9 — Login Page
- **Page/Feature Name**: Sign In UI
- **Objective**: Create a custom login page.
- **Dependencies**: Task 3, Task 7
- **Files**: `templates/account/login.html`
- **Expected Output**: Working login page.
- **Completion Criteria**: Registered user can log in and is successfully redirected to the home page.

### [x] Task 10 — Password Reset Pages
- **Page/Feature Name**: Password Recovery UI
- **Objective**: Implement simple password reset request and set new password pages.
- **Dependencies**: Task 9
- **Files**: `templates/account/password_reset.html`, `templates/account/password_reset_done.html`, `templates/account/password_reset_from_key.html`
- **Expected Output**: Full password recovery flow.
- **Completion Criteria**: User can request a reset link (sent to console in development) and change their password.

### [x] Task 11 — User Profile & Address Book Models
- **Page/Feature Name**: Profile Database Schema
- **Objective**: Create `UserProfile` and `Address` models along with their database fields.
- **Dependencies**: Task 6
- **Files**: `apps/accounts/models.py`, `apps/accounts/admin.py`
- **Expected Output**: Profile and address data structures.
- **Completion Criteria**: Models migrate successfully.

### [x] Task 12 — Customer Profile Page
- **Page/Feature Name**: Edit Profile UI
- **Objective**: Create the page for users to view/edit their profile details.
- **Dependencies**: Task 11
- **Files**: `templates/account/profile.html`, `apps/accounts/views.py`, `apps/accounts/urls.py`, `apps/accounts/forms.py`
- **Expected Output**: Profile edit form.
- **Completion Criteria**: User can update their details (name, avatar) and save changes.

### [x] Task 13 — Customer Address Book Page
- **Page/Feature Name**: Manage Addresses UI
- **Objective**: Page to add, edit, and delete multiple shipping addresses.
- **Dependencies**: Task 11
- **Files**: `templates/account/addresses.html`, `apps/accounts/views.py`, `apps/accounts/urls.py`
- **Expected Output**: Address management interface.
- **Completion Criteria**: User can successfully add, update, and remove shipping addresses.

---

## Phase 2: Vendor Platform

### [x] Task 14 — Vendor & Storefront Models
- **Page/Feature Name**: Vendor Database Schema
- **Objective**: Implement basic `Vendor` and `Storefront` models.
- **Dependencies**: Task 11
- **Files**: `apps/vendors/models.py`, `apps/vendors/admin.py`
- **Expected Output**: Database schema for vendor accounts.
- **Completion Criteria**: Models migrate successfully; admin can manually link a User to a Vendor in Django Admin.

### [x] Task 15 — Vendor Application Form Page
- **Page/Feature Name**: Become a Vendor UI
- **Objective**: Page where customer accounts can apply to become active vendors.
- **Dependencies**: Task 14
- **Files**: `templates/vendors/apply.html`, `apps/vendors/forms.py`, `apps/vendors/views.py`, `apps/vendors/urls.py`
- **Expected Output**: Vendor application form.
- **Completion Criteria**: Form submission successfully creates a pending application in the database.

### [x] Task 16 — Admin Vendor Management Views
- **Page/Feature Name**: Admin Application Review
- **Objective**: Django Admin workflow to approve or reject vendor applications.
- **Dependencies**: Task 15
- **Files**: `apps/vendors/admin.py`, `apps/vendors/services.py`
- **Expected Output**: Simple approval state mechanism.
- **Completion Criteria**: Approving a vendor updates their status and creates their storefront details automatically.

### [x] Task 17 — Vendor Dashboard Base Layout & Home Page
- **Page/Feature Name**: Vendor Dashboard UI
- **Objective**: Create the dashboard sidebar layout and the dashboard home view showing static stats.
- **Dependencies**: Task 14, Task 3
- **Files**: `templates/vendors/dashboard.html`, `templates/vendors/dashboard_base.html`, `apps/vendors/views.py`
- **Expected Output**: Dashboard layout containing overview cards.
- **Completion Criteria**: Vendor can log in and access `/vendor/dashboard/`.

### [x] Task 18 — Vendor Storefront Settings Page
- **Page/Feature Name**: Storefront Configuration UI
- **Objective**: Page for vendors to update their logo, banner, description, and policies.
- **Dependencies**: Task 17
- **Files**: `templates/vendors/storefront_settings.html`, `apps/vendors/views.py`, `apps/vendors/forms.py`
- **Expected Output**: Storefront settings configuration form.
- **Completion Criteria**: Edits save to the database and update the storefront.

### [x] Task 19 — Public Vendor Directory Page
- **Page/Feature Name**: Vendor List UI
- **Objective**: Public directory page listing all active vendor storefronts.
- **Dependencies**: Task 14
- **Files**: `templates/vendors/directory.html`, `apps/vendors/views.py`, `apps/vendors/urls.py`
- **Expected Output**: Grid of active vendor store cards.
- **Completion Criteria**: Accessible for all visitors to browse store options.

### [x] Task 20 — Public Vendor Storefront Page
- **Page/Feature Name**: Vendor Public Profile UI
- **Objective**: Public storefront page showing a specific vendor's description and their catalog.
- **Dependencies**: Task 14
- **Files**: `templates/vendors/storefront.html`, `apps/vendors/views.py`
- **Expected Output**: Dedicated public page displaying vendor info and their products.
- **Completion Criteria**: Accessible via `/store/{slug}/`.

---

## Phase 3: Product Catalog

### [x] Task 21 — Category Model & Mega Menu
- **Page/Feature Name**: Category Schema & Dropdown
- **Objective**: Implement the category database hierarchy and a simple navbar dropdown categories display.
- **Dependencies**: Task 2
- **Files**: `apps/products/models.py`, `apps/products/admin.py`, `templates/includes/navbar.html`
- **Expected Output**: Multi-level product categories and a navigation list.
- **Completion Criteria**: Categories are queryable and show in the navbar header.

### [x] Task 22 — Product & ProductImage Models
- **Page/Feature Name**: Product Database Schema
- **Objective**: Create `Product` and `ProductImage` database tables.
- **Dependencies**: Task 14, Task 21
- **Files**: `apps/products/models.py`, `apps/products/admin.py`
- **Expected Output**: Product models.
- **Completion Criteria**: Product and image attachments can be created locally via admin interface.

### [x] Task 23 — Product Variant & Tag Models
- **Page/Feature Name**: Product Variations Schema
- **Objective**: Add variant (e.g. Size, Color) and tag fields to Products.
- **Dependencies**: Task 22
- **Files**: `apps/products/models.py`
- **Expected Output**: Support for different product configurations.
- **Completion Criteria**: Varied pricing or attributes can be stored per variant.

### [x] Task 24 — Vendor Product List Page
- **Page/Feature Name**: Vendor Manage Products UI
- **Objective**: List products belonging only to the logged-in vendor.
- **Dependencies**: Task 17, Task 22
- **Files**: `templates/vendors/products/list.html`, `apps/products/views/vendor.py`, `apps/products/urls.py`
- **Expected Output**: Tabular product lists with action links.
- **Completion Criteria**: Vendors can see their own inventory list.

### [x] Task 25 — Vendor Product Create & Edit Page
- **Page/Feature Name**: Vendor Add/Edit Product Form UI
- **Objective**: Simple form page to add or edit products, upload images, and configure variants.
- **Dependencies**: Task 24
- **Files**: `templates/vendors/products/form.html`, `apps/products/forms.py`, `apps/products/views/vendor.py`
- **Expected Output**: Unified creation/editing page.
- **Completion Criteria**: Vendor can publish new products or update details.

### [x] Task 26 — Public Product Listing Page
- **Page/Feature Name**: Catalog UI & Filtering
- **Objective**: Page listing all public products, with basic search and category filters.
- **Dependencies**: Task 22, Task 3
- **Files**: `templates/products/list.html`, `apps/products/views/web.py`, `apps/products/urls.py`
- **Expected Output**: Interactive catalog grid.
- **Completion Criteria**: Filtering by category or typing a search query filters the listed cards.

### [x] Task 27 — Public Product Detail Page
- **Page/Feature Name**: Single Product Detail UI
- **Objective**: Detailed display page of a product containing images, variants, descriptions, and a checkout button.
- **Dependencies**: Task 23
- **Files**: `templates/products/detail.html`, `apps/products/views/web.py`, `apps/products/urls.py`
- **Expected Output**: Dedicated product page with layout.
- **Completion Criteria**: Variant selector updates price and visual details correctly.

---

## Phase 4: Shopping & Checkout (Mock Payments)

### [x] Task 28 — Cart System
- **Page/Feature Name**: Shopping Cart Database Schema & Logic
- **Objective**: Implement a session-based or simple database-based multi-vendor shopping cart.
- **Dependencies**: Task 27
- **Files**: `apps/cart/models.py`, `apps/cart/views.py`, `apps/cart/urls.py`
- **Expected Output**: Backend logic to store and adjust quantities of added products.
- **Completion Criteria**: Cart details are maintained as the user navigates.

### [x] Task 29 — Cart Page
- **Page/Feature Name**: Shopping Cart UI
- **Objective**: Create the page for reviewing items, adjusting counts, and clicking proceed to checkout.
- **Dependencies**: Task 28
- **Files**: `templates/cart/detail.html`, `apps/cart/views.py`
- **Expected Output**: Cart page showing line items and calculations.
- **Completion Criteria**: User can successfully see totals, adjust items, and proceed.

### [x] Task 30 — Checkout Page
- **Page/Feature Name**: Checkout Form UI
- **Objective**: Simple checkout page displaying selected shipping address and final order items.
- **Dependencies**: Task 29, Task 13
- **Files**: `templates/checkout/checkout.html`, `apps/orders/views/checkout.py`, `apps/orders/urls.py`
- **Expected Output**: Combined review and checkout information entry.
- **Completion Criteria**: Address and order summary display ready for checkout.

### [x] Task 31 — Mock Payment Page
- **Page/Feature Name**: Simulated Payment Interface
- **Objective**: Create a simplified payment page that simulates processing a credit card payment locally without Stripe.
- **Dependencies**: Task 30
- **Files**: `templates/checkout/payment.html`, `apps/payments/views.py`, `apps/payments/urls.py`
- **Expected Output**: A form showing mock card inputs (card number, expiry, CVV) with a "Pay" button.
- **Completion Criteria**: Submitting the form simulates a 1-second delay and processes the transaction successfully.

### [x] Task 32 — Order Models & Master Order Creation
- **Page/Feature Name**: Order Database Schema
- **Objective**: Create `Order` and `OrderItem` models to record the transaction.
- **Dependencies**: Task 28
- **Files**: `apps/orders/models.py`, `apps/orders/services.py`, `apps/orders/admin.py`
- **Expected Output**: Database tables for tracking paid orders.
- **Completion Criteria**: Successfully paying converts active cart into a logged order record.

### [x] Task 33 — Order Confirmation / Success Page
- **Page/Feature Name**: Order Success UI
- **Objective**: Branded landing page post-checkout indicating order completion.
- **Dependencies**: Task 32, Task 31
- **Files**: `templates/checkout/success.html`, `apps/orders/views/checkout.py`
- **Expected Output**: Receipt confirmation page.
- **Completion Criteria**: Displays final order ID and thank you message.

### [x] Task 34 — Customer Order History & Detail Pages
- **Page/Feature Name**: Customer Order Management UI
- **Objective**: Pages for customers to list their orders and see single order progress.
- **Dependencies**: Task 33
- **Files**: `templates/account/orders.html`, `templates/account/order_detail.html`, `apps/orders/views/customer.py`
- **Expected Output**: History list and specific receipt views.
- **Completion Criteria**: Customers can verify their order statuses.

### [x] Task 35 — Vendor Order List & Detail Pages
- **Page/Feature Name**: Vendor Order Management UI
- **Objective**: Views in the vendor dashboard to track sales items and mark items as completed/shipped.
- **Dependencies**: Task 33, Task 17
- **Files**: `templates/vendors/orders/list.html`, `templates/vendors/orders/detail.html`, `apps/orders/views/vendor.py`
- **Expected Output**: Order dispatch dashboard pages for vendors.
- **Completion Criteria**: Vendor can update the status of their items.

---

## Phase 5: Ecosystem & Operations

### [ ] Task 36 — Review Model & Product Ratings
- **Page/Feature Name**: Ratings Database Schema
- **Objective**: Create a `Review` model to store customer feedback.
- **Dependencies**: Task 34, Task 22
- **Files**: `apps/reviews/models.py`, `apps/reviews/admin.py`
- **Expected Output**: Database fields for 1-5 star ratings.
- **Completion Criteria**: Review records associate correctly to products.

### [ ] Task 37 — Customer Write Review Form
- **Page/Feature Name**: Product Review UI
- **Objective**: Simple form component on the product page or checkout details for customers to write reviews.
- **Dependencies**: Task 36
- **Files**: `templates/reviews/form.html`, `apps/reviews/views.py`, `templates/products/detail.html`
- **Expected Output**: Interactive review submission.
- **Completion Criteria**: Submissions immediately recalculate product average rating.

### [ ] Task 38 — Simple Email Notifications
- **Page/Feature Name**: Email Alerts
- **Objective**: Dispatch emails synchronously (using standard Django email backends) for account welcome and order placement.
- **Dependencies**: Task 7, Task 32
- **Files**: `apps/notifications/services.py`, `templates/emails/order_confirmation.html`
- **Expected Output**: Simple transactional emails.
- **Completion Criteria**: Placing an order triggers an email sent via Django's SMTP layer.

### [ ] Task 39 — Vendor/Admin Simple Dashboard Updates
- **Page/Feature Name**: Simplified Admin Dashboards UI
- **Objective**: Replace dashboard mocks with actual standard database aggregates (e.g. sums of vendor order values).
- **Dependencies**: Task 35, Task 17
- **Files**: `templates/vendors/dashboard.html`, `apps/vendors/views.py`
- **Expected Output**: Live sales count display.
- **Completion Criteria**: Dashboards load actual revenue counts without requiring complex analytical libraries.

---

## Phase 6: Polish

### [x] Task 40 — Static Pages
- **Page/Feature Name**: Landing & Info Pages
- **Objective**: Build the static public pages: Home (`/`), About, Contact, and Terms.
- **Dependencies**: Task 3
- **Files**: `templates/pages/home.html`, `templates/pages/about.html`, `apps/core/views.py`, `config/urls.py`
- **Expected Output**: Basic information pages.
- **Completion Criteria**: Pages load correctly and look fully designed.

### [ ] Task 41 — Custom Error Pages
- **Page/Feature Name**: 404 & 500 Pages
- **Objective**: Design custom error page layouts.
- **Dependencies**: Task 3
- **Files**: `templates/404.html`, `templates/500.html`
- **Expected Output**: Custom styled templates for 404 and 500 error codes.
- **Completion Criteria**: Navigating to broken links displays custom design.

# VendorVerse — User Flows & Use Cases

> **Document Version:** 1.0  
> **Last Updated:** 2026-07-22  
> **Status:** Approved  
> **Related Documents:** [Software Requirements](./02-software-requirements.md) · [UI/UX Design](./07-ui-ux-design.md) · [Authentication & Authorization](./09-authentication-authorization.md)

---

## 1. Use Case Overview

```mermaid
graph TB
    subgraph CustomerUseCases["Customer Use Cases"]
        UC1[Register / Login]
        UC2[Browse & Search Products]
        UC3[Manage Cart]
        UC4[Checkout & Pay]
        UC5[Track Orders]
        UC6[Write Reviews]
        UC7[Manage Profile & Addresses]
        UC8[Manage Wishlist]
        UC9[Request Return / Refund]
    end

    subgraph VendorUseCases["Vendor Use Cases"]
        UC10[Apply for Vendor Account]
        UC11[Set Up Storefront]
        UC12[Manage Products]
        UC13[Fulfill Orders]
        UC14[Track Earnings & Withdraw]
        UC15[View Analytics]
        UC16[Respond to Reviews]
    end

    subgraph AdminUseCases["Admin Use Cases"]
        UC17[Review Vendor Applications]
        UC18[Moderate Products & Reviews]
        UC19[Manage Vendors]
        UC20[Configure Commission Tiers]
        UC21[View Platform Analytics]
        UC22[Manage Site Settings]
    end

    C((Customer)) --> CustomerUseCases
    V((Vendor)) --> VendorUseCases
    A((Admin)) --> AdminUseCases
```

---

## 2. Customer Flows

### 2.1 Registration Flow

```mermaid
flowchart TD
    A[Visit VendorVerse] --> B{Has account?}
    B -->|No| C[Click 'Register']
    B -->|Yes| D[Click 'Login']

    C --> E{Registration method?}
    E -->|Email| F[Fill registration form]
    E -->|Social| G[Click Google/GitHub]

    F --> H{Form valid?}
    H -->|No| I[Show validation errors]
    I --> F
    H -->|Yes| J[Create inactive account]

    G --> K[OAuth flow with provider]
    K --> L{OAuth success?}
    L -->|No| M[Show error, retry option]
    L -->|Yes| N[Create active account with social profile]

    J --> O[Send verification email]
    O --> P[Show 'Check your email' message]
    P --> Q[User clicks verification link]
    Q --> R{Link valid?}
    R -->|No| S[Show 'Link expired' + resend option]
    R -->|Yes| T[Activate account]

    T --> U[Redirect to homepage with welcome toast]
    N --> U
```

### 2.2 Product Discovery Flow

```mermaid
flowchart TD
    A[Customer on Homepage] --> B{Discovery path?}

    B -->|Search| C[Type query in search bar]
    C --> D[Autocomplete suggestions appear]
    D --> E{Select suggestion?}
    E -->|Yes| F[Navigate to product/category]
    E -->|No| G[Submit search]
    G --> H[Search results page]

    B -->|Browse| I[Click category in mega menu]
    I --> J[Category listing page]

    B -->|Featured| K[Click featured product on homepage]
    K --> F

    H --> L[Apply filters & sorting]
    J --> L
    L --> M[Scroll/paginate through results]
    M --> N{Found product?}
    N -->|Yes| F
    N -->|No| O{Refine?}
    O -->|Yes| L
    O -->|No| P[Try different search/category]

    F --> Q[Product Detail Page]
    Q --> R{Action?}
    R -->|Add to Cart| S[Select variant/quantity → Add]
    R -->|Wishlist| T[Toggle wishlist ❤️]
    R -->|Read Reviews| U[Scroll to reviews section]
    R -->|Visit Vendor| V[Navigate to vendor storefront]
```

### 2.3 Checkout Flow (Critical Path)

```mermaid
sequenceDiagram
    actor C as Customer
    participant Cart as Cart Page
    participant Check as Checkout
    participant Addr as Address Selection
    participant Pay as Payment (Stripe)
    participant Order as Order Service
    participant Notify as Notification Service

    C->>Cart: Review cart items
    Cart->>Cart: Validate stock & prices

    alt Items changed
        Cart-->>C: Show update notice (price/stock changes)
    end

    C->>Cart: Click 'Proceed to Checkout'
    Cart->>Check: Redirect to checkout

    Check->>C: Step 1: Select shipping address
    C->>Addr: Choose saved address or enter new

    alt New address
        C->>Addr: Fill address form
        Addr->>Addr: Validate address
        C->>Addr: Optionally save to profile
    end

    Addr->>Check: Address confirmed

    Check->>C: Step 2: Order review with totals
    Note over Check: Subtotal + Shipping + Tax - Discount = Grand Total

    opt Apply coupon
        C->>Check: Enter coupon code
        Check->>Check: Validate coupon
        Check-->>C: Show updated totals
    end

    C->>Check: Confirm order
    Check->>Order: Create order (status: PENDING_PAYMENT)
    Order->>Order: Reserve stock (select_for_update)
    Order-->>Check: Order created with Stripe client_secret

    Check->>C: Step 3: Payment form (Stripe Elements)
    C->>Pay: Enter card details
    Pay->>Pay: Process payment (client-side tokenization)

    alt Payment succeeds
        Pay-->>Check: PaymentIntent succeeded
        Check->>Order: Update order status → PLACED
        Order->>Order: Decrement stock, clear cart
        Order->>Notify: Trigger order_placed signal
        Notify->>C: Email: Order confirmation
        Notify->>Notify: Email: Notify vendor(s)
        Check-->>C: Order confirmation page
    else Payment fails
        Pay-->>Check: Payment failed
        Check->>Order: Update order status → PAYMENT_FAILED
        Order->>Order: Release reserved stock
        Check-->>C: Show error + retry option
    end
```

### 2.4 Order Tracking Flow

```mermaid
flowchart TD
    A[Customer views Order History] --> B[List of orders with status badges]
    B --> C[Click order to view details]
    C --> D[Order Detail Page]

    D --> E[Status Timeline]
    E --> F{Current status?}

    F -->|Placed| G[Waiting for vendor confirmation]
    F -->|Confirmed| H[Vendor is preparing order]
    F -->|Shipped| I[Show tracking number & carrier]
    F -->|Delivered| J[Show delivery date]

    I --> K{Track shipment?}
    K -->|Yes| L[Open carrier tracking page]

    J --> M{Actions available?}
    M -->|Write Review| N[Navigate to review form]
    M -->|Request Return| O[Submit return request]

    D --> P{Cancel order?}
    P -->|Status allows| Q[Confirm cancellation]
    Q --> R[Order cancelled + refund initiated]
    P -->|Status too late| S[Cancellation not available message]
```

---

## 3. Vendor Flows

### 3.1 Vendor Application & Onboarding

```mermaid
flowchart TD
    A[Registered Customer] --> B[Click 'Become a Vendor']
    B --> C[Vendor Application Form]
    C --> D[Fill: business name, description, type, tax ID]
    D --> E{Form valid?}
    E -->|No| F[Show validation errors]
    F --> C
    E -->|Yes| G[Submit application]

    G --> H[Application status: PENDING]
    H --> I[Admin notified of new application]
    I --> J{Admin decision?}

    J -->|Approve| K[User role updated to VENDOR]
    J -->|Reject| L[Email: rejection with reason]

    K --> M[Email: 'Your vendor application is approved!']
    M --> N[Redirect to Vendor Onboarding]

    N --> O[Step 1: Storefront Setup]
    O --> P[Upload logo, banner, write description]
    P --> Q[Step 2: Policies]
    Q --> R[Set return policy, shipping policy]
    R --> S[Step 3: Stripe Connect Onboarding]
    S --> T[Redirect to Stripe for account setup]
    T --> U{Stripe setup complete?}

    U -->|Yes| V[Vendor status: ACTIVE]
    U -->|No| W[Vendor status: PENDING_SETUP]
    W --> X[Dashboard shows 'Complete Stripe setup' banner]

    V --> Y[Vendor can list products]

    L --> Z[Customer can reapply after addressing feedback]
```

### 3.2 Product Management Flow

```mermaid
flowchart TD
    A[Vendor Dashboard] --> B[Click 'Add Product']
    B --> C[Product Creation Form]

    C --> D[Section 1: Basic Info]
    D --> E[Title, description, category, tags]

    E --> F[Section 2: Pricing & Inventory]
    F --> G[Price, compare price, SKU, stock quantity, low stock threshold]

    G --> H[Section 3: Images]
    H --> I[Upload up to 10 images, set primary, drag to reorder]

    I --> J[Section 4: Variants - optional]
    J --> K[Add size/color/material variants with individual SKU & stock]

    K --> L[Section 5: SEO - optional]
    L --> M[Meta title, meta description]

    M --> N{Save action?}
    N -->|Save as Draft| O[Status: DRAFT]
    N -->|Publish| P{Vendor verified?}

    P -->|Yes| Q[Status: PUBLISHED]
    P -->|No, < 5 products| R[Status: PENDING_REVIEW]
    P -->|No, ≥ 5 approved| Q

    R --> S[Admin moderation queue]
    S --> T{Admin decision?}
    T -->|Approve| Q
    T -->|Reject| U[Status: DRAFT + rejection reason]
    U --> V[Vendor notified to fix issues]

    Q --> W[Product visible to customers]
```

### 3.3 Order Fulfillment Flow

```mermaid
sequenceDiagram
    actor V as Vendor
    participant Dash as Vendor Dashboard
    participant Order as Order Service
    participant Notify as Notification Service
    actor C as Customer

    Note over V, C: Order has been placed by customer

    Notify->>V: Email + in-app: "New order received!"
    V->>Dash: View new order details
    Dash-->>V: Show order items, quantities, shipping address

    V->>Dash: Click 'Confirm Order'
    Dash->>Order: Update item status → CONFIRMED
    Order->>Notify: Trigger status change
    Notify->>C: Email: "Your order has been confirmed"

    V->>V: Prepare and package items

    V->>Dash: Click 'Mark as Shipped'
    Dash-->>V: Form: Enter tracking number + carrier
    V->>Dash: Submit tracking info
    Dash->>Order: Update item status → SHIPPED
    Order->>Notify: Trigger status change
    Notify->>C: Email: "Your order has been shipped" + tracking info

    Note over C: Customer receives package

    alt Customer confirms delivery
        C->>Order: Mark as delivered
    else Auto-delivery (14 days after shipping)
        Order->>Order: Auto-mark DELIVERED
    end

    Order->>Notify: Trigger delivery notification
    Notify->>C: Email: "Your order has been delivered" + review CTA
    
    Note over V: After payout hold period (7 days)
    Order->>Order: Release vendor earnings
```

---

## 4. Admin Flows

### 4.1 Vendor Application Review

```mermaid
flowchart TD
    A[Admin Dashboard] --> B[Notification: N pending applications]
    B --> C[Navigate to Applications Queue]
    C --> D[View application list - sorted by date]
    D --> E[Click application to review]
    E --> F[Review: business name, description, type, website]

    F --> G{Decision?}
    G -->|Approve| H[Click 'Approve']
    H --> I[Confirmation modal]
    I --> J[Vendor account created]
    J --> K[Email sent to applicant]

    G -->|Reject| L[Click 'Reject']
    L --> M[Enter rejection reason - required]
    M --> N[Confirmation modal]
    N --> O[Application marked REJECTED]
    O --> P[Email sent with reason]

    G -->|Need more info| Q[Click 'Request Info']
    Q --> R[Email sent requesting clarification]
```

### 4.2 Content Moderation Flow

```mermaid
flowchart TD
    A[Admin Panel] --> B[Moderation Queue]
    B --> C{Queue type?}

    C -->|Products| D[Pending products list]
    D --> E[View product details, images, description]
    E --> F{Decision?}
    F -->|Approve| G[Status → PUBLISHED]
    F -->|Reject| H[Enter reason → Status → DRAFT]
    F -->|Flag| I[Add note, keep in queue for further review]

    C -->|Reviews| J[Flagged reviews list]
    J --> K[View review content, associated product, reviewer history]
    K --> L{Decision?}
    L -->|Approve| M[Review visible]
    L -->|Edit| N[Modify offensive content, keep review]
    L -->|Remove| O[Review hidden, reviewer notified]
```

---

## 5. Sequence Diagrams — Critical System Interactions

### 5.1 Multi-Vendor Cart to Sub-Orders

```mermaid
sequenceDiagram
    participant C as Customer
    participant CS as Cart Service
    participant OS as Order Service
    participant PS as Payment Service
    participant ST as Stripe

    C->>CS: Checkout cart (3 items, 2 vendors)
    CS->>CS: Validate all items (stock, price, availability)
    CS-->>C: Cart validated

    C->>OS: Place order
    OS->>OS: Create parent Order (ORD-001)
    OS->>OS: Create OrderItem for Vendor A (2 items)
    OS->>OS: Create OrderItem for Vendor B (1 item)
    OS->>OS: Calculate commission per vendor
    Note over OS: Vendor A: $50 × 5% = $2.50 commission<br/>Vendor B: $30 × 3% = $0.90 commission

    OS->>PS: Create payment for $80 total
    PS->>ST: Create PaymentIntent ($80)
    PS->>ST: Create Transfer to Vendor A ($47.50)
    PS->>ST: Create Transfer to Vendor B ($29.10)
    PS->>ST: Platform keeps $3.40 commission
    ST-->>PS: PaymentIntent client_secret

    PS-->>OS: Payment initiated
    OS-->>C: Show Stripe payment form

    C->>ST: Confirm payment (card details)
    ST-->>C: Payment succeeded
    C->>OS: Payment confirmed

    OS->>OS: Order status → PLACED
    OS->>OS: Create sub-order status logs
    Note over OS: Vendor A and Vendor B each see their items independently
```

### 5.2 Review Submission Flow

```mermaid
sequenceDiagram
    participant C as Customer
    participant RS as Review Service
    participant PS as Product Service
    participant NS as Notification Service

    C->>RS: Submit review (product_id, rating=4, body="Great!")
    RS->>RS: Validate: customer purchased this product?
    RS->>RS: Validate: order status = DELIVERED?
    RS->>RS: Validate: no existing review for this product+order?

    alt Validation fails
        RS-->>C: Error: "You can only review purchased & delivered products"
    end

    RS->>RS: Create Review (is_verified_purchase=true)
    RS->>RS: Check for flagged keywords (auto-moderation)

    alt Contains flagged content
        RS->>RS: Set is_approved=false (pending moderation)
        RS->>NS: Notify admin: review pending moderation
    else Clean content
        RS->>RS: Set is_approved=true
    end

    RS->>PS: Signal: update product rating
    PS->>PS: Recalculate average_rating and review_count
    PS->>PS: Update vendor average_rating

    RS-->>C: Review submitted successfully (toast notification)
```

### 5.3 Vendor Payout Flow

```mermaid
sequenceDiagram
    participant V as Vendor
    participant VS as Vendor Service
    participant PS as Payment Service
    participant ST as Stripe

    V->>VS: Request withdrawal ($500)
    VS->>VS: Check: available_earnings ≥ $500?
    VS->>VS: Check: amount ≥ min_payout_amount ($50)?
    VS->>VS: Check: Stripe account active?

    alt Validation fails
        VS-->>V: Error with specific reason
    end

    VS->>VS: Create withdrawal request (status: PENDING)
    VS->>VS: Deduct $500 from available_earnings
    VS->>PS: Process payout via Stripe

    PS->>ST: Create Payout to vendor's Stripe account
    ST-->>PS: Payout created (processing)

    Note over ST: Stripe processes payout (1-2 business days)

    ST->>PS: Webhook: payout.paid
    PS->>VS: Update withdrawal status → COMPLETED
    VS->>VS: Update total_withdrawn
    PS->>V: Email: "Payout of $500 has been processed"

    alt Payout fails
        ST->>PS: Webhook: payout.failed
        PS->>VS: Update withdrawal status → FAILED
        VS->>VS: Restore available_earnings
        PS->>V: Email: "Payout failed, funds restored"
    end
```

---

## 6. Error Scenarios & Edge Cases

### 6.1 Cart Edge Cases

| Scenario | System Behavior | User Experience |
|---|---|---|
| Product goes out of stock after being added to cart | Cart validation at checkout detects | Warning: "X is no longer available" with option to remove |
| Product price changes after being added to cart | Cart validation at checkout detects | Notice: "Price of X has changed from $Y to $Z" with updated totals |
| Vendor gets suspended with products in carts | Cart validation removes vendor items | Warning: "Items from X are no longer available" |
| Cart item quantity exceeds available stock | Reduce to max available | Notice: "Only N units of X available" |
| Coupon expires during checkout | Validate at order creation | Error: "Coupon has expired" with updated totals |

### 6.2 Order Edge Cases

| Scenario | System Behavior | User Experience |
|---|---|---|
| Vendor doesn't confirm order in 48 hours | Celery task sends reminder at 24h; escalate to admin at 48h | Customer receives "delay" notification |
| Customer cancels multi-vendor order | Per-vendor items cancelled independently | Only cancellable items cancelled; shipped items excluded |
| Partial delivery (some items from order) | Each order item tracked independently | Order status: PARTIALLY_SHIPPED; item-level tracking |
| Double payment attempt | Idempotency key on PaymentIntent | Second attempt detected; single charge processed |
| Stripe webhook arrives before client callback | Order updated via webhook; client sees updated state | No inconsistency — webhook is source of truth |

---

*← [UI/UX Design](./07-ui-ux-design.md) · Next: [Authentication & Authorization →](./09-authentication-authorization.md)*

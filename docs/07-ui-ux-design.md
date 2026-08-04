# VendorVerse — UI/UX Design

> **Document Version:** 1.0  
> **Last Updated:** 2026-07-22  
> **Status:** Approved  
> **Related Documents:** [Software Requirements](./02-software-requirements.md) · [User Flows](./08-user-flows.md) · [Django Architecture](./06-django-architecture.md)

---

## 1. Design Philosophy

### 1.1 Core Principles

| Principle | Application |
|---|---|
| **Clarity** | Every page has one primary action; visual hierarchy guides the user's eye; zero ambiguity |
| **Consistency** | Reusable component library; uniform spacing, typography, and color usage across all pages |
| **Speed** | Server-rendered pages load fast; HTMX partial updates avoid full reloads; skeleton loaders for perceived performance |
| **Trust** | Professional design signals platform credibility; verified badges, secure payment indicators, review transparency |
| **Accessibility** | WCAG 2.1 AA compliance; keyboard navigation; screen reader support; sufficient color contrast |

### 1.2 Design System: "Verse"

The design system is named "Verse" — providing a cohesive visual language across all VendorVerse interfaces.

---

## 2. Color System

### 2.1 Brand Colors

| Token | Hex | HSL | Usage |
|---|---|---|---|
| `--color-primary-50` | `#eef2ff` | 226, 100%, 97% | Primary tint (backgrounds) |
| `--color-primary-100` | `#e0e7ff` | 226, 100%, 94% | Hover backgrounds |
| `--color-primary-200` | `#c7d2fe` | 226, 100%, 88% | Borders, dividers |
| `--color-primary-300` | `#a5b4fc` | 226, 95%, 81% | Icons, secondary text |
| `--color-primary-400` | `#818cf8` | 234, 89%, 74% | Interactive elements hover |
| `--color-primary-500` | `#6366f1` | 239, 84%, 67% | **Primary brand color** — buttons, links, active states |
| `--color-primary-600` | `#4f46e5` | 243, 75%, 59% | Button hover, focused states |
| `--color-primary-700` | `#4338ca` | 245, 58%, 51% | Active/pressed states |
| `--color-primary-800` | `#3730a3` | 244, 47%, 42% | Dark accents |
| `--color-primary-900` | `#312e81` | 242, 47%, 34% | Darkest tint |

### 2.2 Semantic Colors

| Token | Color | Usage |
|---|---|---|
| `--color-success` | `#10b981` (Emerald 500) | Success states, completed orders, verified badges |
| `--color-warning` | `#f59e0b` (Amber 500) | Warnings, pending states, low stock |
| `--color-danger` | `#ef4444` (Red 500) | Errors, destructive actions, out of stock |
| `--color-info` | `#3b82f6` (Blue 500) | Information, tips, links |

### 2.3 Neutral Palette

| Token | Hex | Usage |
|---|---|---|
| `--color-gray-50` | `#f9fafb` | Page background |
| `--color-gray-100` | `#f3f4f6` | Card backgrounds, input backgrounds |
| `--color-gray-200` | `#e5e7eb` | Borders, dividers |
| `--color-gray-300` | `#d1d5db` | Disabled states |
| `--color-gray-400` | `#9ca3af` | Placeholder text |
| `--color-gray-500` | `#6b7280` | Secondary text |
| `--color-gray-600` | `#4b5563` | Body text |
| `--color-gray-700` | `#374151` | Headings |
| `--color-gray-800` | `#1f2937` | Dark backgrounds |
| `--color-gray-900` | `#111827` | Darkest surfaces |

---

## 3. Typography

### 3.1 Font Stack

| Usage | Font | Fallback | Source |
|---|---|---|---|
| **Headings** | Inter | system-ui, sans-serif | Google Fonts |
| **Body** | Inter | system-ui, sans-serif | Google Fonts |
| **Monospace** | JetBrains Mono | monospace | Google Fonts |

### 3.2 Type Scale

| Token | Size | Weight | Line Height | Usage |
|---|---|---|---|---|
| `text-display` | 36px / 2.25rem | 800 | 1.2 | Hero headlines |
| `text-h1` | 30px / 1.875rem | 700 | 1.3 | Page titles |
| `text-h2` | 24px / 1.5rem | 700 | 1.35 | Section headings |
| `text-h3` | 20px / 1.25rem | 600 | 1.4 | Card titles, subsections |
| `text-h4` | 18px / 1.125rem | 600 | 1.4 | Widget headings |
| `text-body-lg` | 18px / 1.125rem | 400 | 1.6 | Lead paragraphs |
| `text-body` | 16px / 1rem | 400 | 1.6 | Default body text |
| `text-body-sm` | 14px / 0.875rem | 400 | 1.5 | Secondary text, captions |
| `text-caption` | 12px / 0.75rem | 500 | 1.5 | Labels, badges, metadata |

---

## 4. Spacing & Layout

### 4.1 Spacing Scale

Base unit: `4px`. All spacing uses multiples of the base unit.

| Token | Value | Usage |
|---|---|---|
| `space-1` | 4px | Tight internal spacing |
| `space-2` | 8px | Icon-text gap, badge padding |
| `space-3` | 12px | Input padding, small card padding |
| `space-4` | 16px | Standard padding, gap between elements |
| `space-5` | 20px | Card padding |
| `space-6` | 24px | Section gaps |
| `space-8` | 32px | Large section spacing |
| `space-10` | 40px | Page section margins |
| `space-12` | 48px | Major layout gaps |
| `space-16` | 64px | Page top/bottom padding |

### 4.2 Grid System

| Breakpoint | Name | Min Width | Columns | Max Container |
|---|---|---|---|---|
| Mobile | `sm` | 0px | 1 | 100% |
| Tablet | `md` | 768px | 2-3 | 768px |
| Desktop | `lg` | 1024px | 3-4 | 1024px |
| Wide | `xl` | 1280px | 4-5 | 1280px |

Product grids: 1 column (mobile) → 2 columns (tablet) → 3-4 columns (desktop)

---

## 5. Component Library

### 5.1 Buttons

| Variant | Usage | Visual |
|---|---|---|
| **Primary** | Main CTA (Add to Cart, Place Order, Submit) | Solid primary-500, white text, rounded-lg, shadow |
| **Secondary** | Secondary actions (Save Draft, Cancel) | Outline primary-500, transparent bg |
| **Danger** | Destructive actions (Delete, Remove) | Solid danger, white text |
| **Ghost** | Tertiary actions, inline links | No bg/border, primary text, underline on hover |
| **Icon** | Action icons (edit, delete, heart) | Circular, icon only, tooltip |

**States:** Default → Hover (darken 10%) → Active (darken 15%) → Disabled (gray-300, cursor-not-allowed) → Loading (spinner replaces text)

### 5.2 Form Inputs

| Component | Description |
|---|---|
| **Text Input** | Rounded-lg, gray-100 bg, gray-200 border, primary focus ring; label above; error message below in danger |
| **Textarea** | Same as text input, resizable vertically |
| **Select** | Custom styled dropdown; search for long lists (Alpine.js) |
| **Checkbox / Radio** | Custom styled with primary accent; label beside |
| **File Upload** | Drag-and-drop zone; image preview; progress bar |
| **Search Input** | Rounded-full, search icon left, clear button right |

### 5.3 Cards

| Card Type | Usage | Structure |
|---|---|---|
| **Product Card** | Product listing grid | Image (aspect-ratio 1:1) → Title → Vendor name → Rating stars → Price (sale/original) → Add to Cart button |
| **Vendor Card** | Vendor directory | Logo + Banner → Business name → Rating → Product count → "Visit Store" link |
| **Order Card** | Order history | Order number + date → Status badge → Item count → Total → "View Details" link |
| **Review Card** | Product reviews | Star rating → Title → Body → Author name → Date → Helpful count → Vendor response |
| **Stat Card** | Dashboards | Icon → Metric label → Value (large) → Trend indicator (up/down %) |

### 5.4 Navigation

| Component | Description |
|---|---|
| **Top Navbar** | Fixed; logo left, search center, cart/notifications/avatar right; mobile hamburger |
| **Category Mega Menu** | Full-width dropdown on hover; 3-column category grid; featured image |
| **Breadcrumbs** | Home > Category > Subcategory > Product; chevron separators |
| **Sidebar Nav** | Vendor/admin dashboards; icon + label; active state highlight; collapsible on mobile |
| **Pagination** | Previous/Next + page numbers; ellipsis for large ranges; current page highlighted |
| **Tabs** | Horizontal tabs for related content (product description/reviews/shipping) |

### 5.5 Feedback Components

| Component | Usage | Behavior |
|---|---|---|
| **Toast** | Success/error/info notifications | Top-right, auto-dismiss 5s, swipe to dismiss |
| **Modal** | Confirmations, quick actions | Centered overlay, escape to close, focus trap |
| **Loading Spinner** | Async operations | CSS spinner, centered; skeleton loader for content areas |
| **Empty State** | No data available | Illustration + message + CTA button |
| **Progress Bar** | Multi-step processes (checkout) | Steps with labels; completed/current/upcoming states |
| **Badge** | Status indicators | Pill-shaped; semantic colors per status |

### 5.6 Status Badge Mapping

| Status | Color | Used For |
|---|---|---|
| Pending | `amber-100` bg / `amber-700` text | Pending payment, pending review, pending approval |
| Active / Published | `emerald-100` bg / `emerald-700` text | Active vendor, published product |
| Processing | `blue-100` bg / `blue-700` text | Order processing, in progress |
| Shipped | `indigo-100` bg / `indigo-700` text | Order shipped |
| Delivered / Completed | `emerald-100` bg / `emerald-700` text | Delivered, completed |
| Cancelled | `gray-100` bg / `gray-700` text | Cancelled order, archived |
| Suspended / Banned | `red-100` bg / `red-700` text | Suspended vendor, rejected |
| Draft | `gray-100` bg / `gray-500` text | Draft product |

---

## 6. Page Inventory

### 6.1 Public Pages

| Page | Route | Key Components |
|---|---|---|
| **Homepage** | `/` | Hero banner, featured products carousel, category grid, trending products, new arrivals, top vendors |
| **Product Listing** | `/products/`, `/categories/{slug}/` | Filter sidebar, sort dropdown, product grid, pagination |
| **Product Detail** | `/products/{slug}/` | Image gallery, price/variants, add to cart, description tabs, reviews, related products |
| **Search Results** | `/search/?q=` | Search bar, filter sidebar, result count, product grid |
| **Vendor Storefront** | `/store/{slug}/` | Vendor banner, about section, product grid, vendor rating |
| **Vendor Directory** | `/vendors/` | Vendor cards grid, category filter, search |
| **Static Pages** | `/about/`, `/contact/`, `/terms/`, `/privacy/` | Content pages |

### 6.2 Authentication Pages

| Page | Route | Key Components |
|---|---|---|
| **Login** | `/account/login/` | Email/password form, social login buttons, register link |
| **Register** | `/account/register/` | Registration form, social signup, login link |
| **Password Reset** | `/account/password/reset/` | Email input, submit, confirmation message |
| **Email Verification** | `/account/verify-email/{key}/` | Auto-verify, success/error message |

### 6.3 Customer Pages

| Page | Route | Key Components |
|---|---|---|
| **Profile** | `/account/profile/` | Profile form, avatar upload, notification preferences |
| **Addresses** | `/account/addresses/` | Address list, add/edit modal, default toggle |
| **Wishlist** | `/account/wishlist/` | Product grid (wishlist items), remove button |
| **Order History** | `/account/orders/` | Order cards, status filter, date filter |
| **Order Detail** | `/account/orders/{number}/` | Order summary, item list, status timeline, tracking info, actions (cancel/return) |
| **Cart** | `/cart/` | Cart items grouped by vendor, quantity controls, totals, proceed to checkout |
| **Checkout** | `/checkout/` | Multi-step: address → payment → review → confirm |

### 6.4 Vendor Dashboard Pages

| Page | Route | Key Components |
|---|---|---|
| **Dashboard** | `/vendor/dashboard/` | Stat cards (revenue, orders, rating), charts, recent orders, alerts |
| **Products** | `/vendor/products/` | Product table, status filter, bulk actions, add product button |
| **Product Form** | `/vendor/products/new/`, `/vendor/products/{slug}/edit/` | Multi-section form: basic info, images, variants, SEO |
| **Orders** | `/vendor/orders/` | Order items table, status filter, actions (confirm, ship) |
| **Order Detail** | `/vendor/orders/{id}/` | Item details, status update, tracking entry |
| **Earnings** | `/vendor/earnings/` | Earnings summary, transaction history, withdrawal form |
| **Storefront Settings** | `/vendor/storefront/` | Logo/banner upload, description, policies |
| **Analytics** | `/vendor/analytics/` | Revenue chart, top products, customer demographics |

### 6.5 Admin Panel Pages

| Page | Route | Key Components |
|---|---|---|
| **Dashboard** | `/manage/` | Platform stats, alerts, quick actions |
| **Vendor Applications** | `/manage/applications/` | Application list, approve/reject actions |
| **Vendor Management** | `/manage/vendors/` | Vendor table, status management, suspension |
| **Product Moderation** | `/manage/moderation/products/` | Pending products queue, approve/reject |
| **Review Moderation** | `/manage/moderation/reviews/` | Flagged reviews queue, approve/reject |
| **Categories** | `/manage/categories/` | Category tree editor, drag-and-drop reordering |
| **Commission Tiers** | `/manage/commissions/` | Tier configuration, commission rates |
| **Site Settings** | `/manage/settings/` | Platform name, logo, homepage config, maintenance mode |
| **Users** | `/manage/users/` | User table, role management, account actions |
| **Analytics** | `/manage/analytics/` | Platform-wide analytics, GMV trends, vendor performance |

---

## 7. Responsive Strategy

### 7.1 Breakpoint Behavior

| Component | Mobile (<768px) | Tablet (768-1023px) | Desktop (≥1024px) |
|---|---|---|---|
| **Navbar** | Hamburger menu, compact | Full nav, search visible | Full nav, search expanded |
| **Product Grid** | 1-2 columns | 2-3 columns | 3-4 columns |
| **Filter Sidebar** | Sheet from bottom (slideover) | Collapsible sidebar | Fixed sidebar |
| **Product Detail** | Stacked: image → info → tabs | 2-column: image left, info right | 2-column with wider image |
| **Dashboard** | Single column, stat cards stack | 2-column layout | 3-column layout with sidebar |
| **Cart** | Vertical item list | Item list + summary sidebar | Item list + summary sidebar |
| **Checkout** | Single column steps | Single column, wider | Two-column: form + order summary |

### 7.2 Touch Considerations

- Tap targets minimum 44×44px
- Swipe gestures for image galleries (Alpine.js)
- Bottom sheet modals on mobile (instead of center modals)
- Sticky add-to-cart bar on mobile product detail

---

## 8. Interaction Patterns (HTMX)

### 8.1 Dynamic Interactions Map

| Interaction | Trigger | HTMX Attribute | Target | Behavior |
|---|---|---|---|---|
| **Product pagination** | Scroll/Click "Load More" | `hx-get` | Product grid | Append next page of products |
| **Filter products** | Change filter value | `hx-get` with params | Product grid | Replace product grid |
| **Sort products** | Select sort option | `hx-get` with params | Product grid | Replace product grid |
| **Add to cart** | Click "Add to Cart" | `hx-post` | Cart icon count | Update cart count + show toast |
| **Update cart quantity** | Change quantity input | `hx-patch` | Cart item row | Update line total + cart total |
| **Remove cart item** | Click remove button | `hx-delete` | Cart item row | Remove row + update totals |
| **Search autocomplete** | Type in search bar | `hx-get` (debounced) | Suggestion dropdown | Show suggestions |
| **Toggle wishlist** | Click heart icon | `hx-post` | Heart icon | Toggle filled/outline + toast |
| **Notification bell** | Load / Poll | `hx-get` (triggered) | Bell badge | Update unread count |
| **Mark notification read** | Click notification | `hx-post` | Notification item | Mark as read, reduce count |
| **Order status update** | Vendor clicks action | `hx-patch` | Status badge | Update badge + show toast |
| **Review submission** | Submit review form | `hx-post` | Review list | Prepend new review |
| **Image gallery** | Click thumbnail | Alpine.js | Main image | Swap displayed image (client-side) |

### 8.2 Loading Indicators

| Pattern | Usage |
|---|---|
| **Button spinner** | Replace button text with spinner on click; restore on response |
| **Skeleton loader** | Show gray animated placeholder blocks while content loads |
| **Progress bar** | Thin bar at top of page (NProgress-style) for navigation |
| **Inline spinner** | Small spinner next to element being updated |

Implementation: HTMX's `hx-indicator` attribute points to the loading element; CSS class `htmx-request` applied during request.

---

## 9. Accessibility Requirements

| Requirement | Implementation |
|---|---|
| **Keyboard Navigation** | All interactive elements focusable; logical tab order; visible focus rings |
| **Screen Reader** | Semantic HTML; ARIA labels where needed; `aria-live` for dynamic updates |
| **Color Contrast** | All text meets WCAG AA (4.5:1 normal, 3:1 large text) |
| **Alt Text** | All images have descriptive alt text; decorative images use `alt=""` |
| **Form Labels** | Every input has associated `<label>`; error messages linked via `aria-describedby` |
| **Motion** | Respect `prefers-reduced-motion`; disable animations when user prefers |
| **Focus Management** | After HTMX swap, focus moved to new content; modal focus trap |
| **Skip Links** | "Skip to main content" link for keyboard users |

---

## 10. Email Template Design

| Email | Trigger | Key Content |
|---|---|---|
| **Welcome** | Registration | Welcome message, verify email CTA, platform intro |
| **Email Verification** | Registration | Verification link, expiry notice |
| **Order Confirmation** | Order placed | Order details, item list, totals, shipping address |
| **Order Shipped** | Vendor ships | Tracking number, carrier, estimated delivery |
| **Order Delivered** | Delivery confirmed | Delivery confirmation, review prompt, support link |
| **Vendor Approved** | Admin approves | Congratulations, next steps, storefront setup CTA |
| **Vendor Rejected** | Admin rejects | Rejection reason, reapply guidance |
| **Password Reset** | User requests | Reset link (1hr expiry), security notice |
| **Low Stock Alert** | Stock threshold | Product name, current stock, restock CTA |
| **Payout Processed** | Withdrawal complete | Amount, transaction ID, balance |

Email templates follow a consistent brand layout: logo header, content body, footer with unsubscribe link. All emails are both HTML and plain-text.

---

*← [Django Architecture](./06-django-architecture.md) · Next: [User Flows →](./08-user-flows.md)*

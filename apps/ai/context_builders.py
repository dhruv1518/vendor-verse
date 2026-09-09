"""
Context builders for VendorVerse AI chatbot.

This is the HEART of the dual-mode chatbot:
- build_global_context()     → Site-wide VendorVerse assistant
- build_storefront_context() → Vendor-specific storefront assistant
- build_product_context()    → Product-focused assistant (when on a product page)

DATA ISOLATION:
All product queries are scoped using Django ORM filters.
The AI only ever sees products we explicitly pass to it.
It physically cannot access Vendor B's data when serving Vendor A's storefront.
"""

import re
from django.db.models import Q, Avg

from apps.products.models import Product, Category
from apps.vendors.models import Storefront
from apps.reviews.models import Review


# ----- Keyword Extraction (simple, no ML needed) -----

# Common words to ignore when searching for products
STOP_WORDS = {
    "i", "me", "my", "want", "need", "looking", "for", "a", "an", "the",
    "is", "are", "do", "does", "have", "has", "can", "you", "show", "me",
    "find", "search", "get", "tell", "about", "what", "which", "where",
    "how", "much", "any", "some", "good", "best", "top", "cheap",
    "expensive", "please", "thanks", "thank", "hi", "hello", "hey",
    "recommend", "suggest", "give", "list", "available", "buy", "price",
    "cost", "under", "below", "above", "over", "between", "than",
    "product", "products", "item", "items", "thing", "things",
    "store", "shop", "vendor", "this",
}


def extract_keywords(message):
    """Extract meaningful keywords from a user message for product search."""
    # Clean the message
    words = re.findall(r"[a-zA-Z]+", message.lower())
    keywords = [w for w in words if w not in STOP_WORDS and len(w) > 1]
    return keywords


def extract_price_filters(message):
    """
    Extract price constraints from a message.
    Examples: "under ₹2000", "below 1500", "between 500 and 2000"
    """
    price_filters = {}

    # Match patterns like "under ₹2000", "below 2000", "under Rs.2000"
    under_match = re.search(
        r"(?:under|below|less than|cheaper than|within|upto|up to|max)\s*(?:₹|rs\.?|inr)?\s*(\d[\d,]*)",
        message.lower(),
    )
    if under_match:
        price_filters["max_price"] = int(under_match.group(1).replace(",", ""))

    # Match patterns like "above ₹2000", "over 2000", "more than 1500"
    above_match = re.search(
        r"(?:above|over|more than|starting from|min|at least)\s*(?:₹|rs\.?|inr)?\s*(\d[\d,]*)",
        message.lower(),
    )
    if above_match:
        price_filters["min_price"] = int(above_match.group(1).replace(",", ""))

    return price_filters


# ----- Product Formatting -----

def format_product_basic(product):
    """Format a product for global context (concise)."""
    parts = [f"• {product.name}"]
    parts.append(f"  Price: ₹{product.base_price}")
    if product.compare_at_price and product.is_on_sale:
        parts.append(f"  Was: ₹{product.compare_at_price} ({product.discount_percentage}% off)")
    if product.category:
        parts.append(f"  Category: {product.category.name}")
    parts.append(f"  Vendor: {product.vendor.business_name}")
    parts.append(f"  In stock: {'Yes' if product.in_stock else 'No'}")
    return "\n".join(parts)


def format_product_detailed(product):
    """Format a product for storefront context (detailed with variants, reviews)."""
    parts = [f"• {product.name}"]
    parts.append(f"  Price: ₹{product.base_price}")
    if product.compare_at_price and product.is_on_sale:
        parts.append(f"  Was: ₹{product.compare_at_price} ({product.discount_percentage}% off)")
    if product.category:
        parts.append(f"  Category: {product.category.name}")
    if product.short_description:
        parts.append(f"  Summary: {product.short_description}")
    if product.description:
        # Truncate long descriptions
        desc = product.description[:200]
        if len(product.description) > 200:
            desc += "..."
        parts.append(f"  Description: {desc}")
    parts.append(f"  In stock: {'Yes' if product.in_stock else 'Out of stock'}")
    if product.stock_quantity > 0:
        parts.append(f"  Stock: {product.stock_quantity} available")

    # Include tags
    tags = list(product.tags.values_list("name", flat=True))
    if tags:
        parts.append(f"  Tags: {', '.join(tags)}")

    # Include variants
    variants = list(product.variants.filter(is_active=True))
    if variants:
        variant_strs = []
        for v in variants:
            price_info = f"₹{v.effective_price}"
            stock_info = "in stock" if v.stock_quantity > 0 else "out of stock"
            variant_strs.append(f"{v.name} ({price_info}, {stock_info})")
        parts.append(f"  Variants: {'; '.join(variant_strs)}")

    # Include average rating
    avg_rating = product.reviews.aggregate(avg=Avg("rating"))["avg"]
    review_count = product.reviews.count()
    if avg_rating:
        parts.append(f"  Rating: {avg_rating:.1f}/5 ({review_count} reviews)")

    return "\n".join(parts)


# ----- Search Helpers -----

def search_products(queryset, keywords, price_filters):
    """Apply keyword and price filters to a product queryset."""
    qs = queryset

    # Apply keyword filters (search name, description, category, tags)
    if keywords:
        keyword_q = Q()
        for kw in keywords:
            keyword_q |= (
                Q(name__icontains=kw)
                | Q(description__icontains=kw)
                | Q(short_description__icontains=kw)
                | Q(category__name__icontains=kw)
                | Q(tags__name__icontains=kw)
            )
        qs = qs.filter(keyword_q).distinct()

    # Apply price filters
    if "max_price" in price_filters:
        qs = qs.filter(base_price__lte=price_filters["max_price"])
    if "min_price" in price_filters:
        qs = qs.filter(base_price__gte=price_filters["min_price"])

    return qs


# =====================================================================
# MODE 1: GLOBAL VENDORVERSE AI
# =====================================================================

def build_global_context(user_message):
    """
    Build the system prompt for the Global VendorVerse AI assistant.
    Searches across ALL active products from ALL vendors.
    """
    keywords = extract_keywords(user_message)
    price_filters = extract_price_filters(user_message)

    # Base queryset: all active products
    base_qs = (
        Product.objects.filter(status=Product.Status.ACTIVE)
        .select_related("vendor", "category")
    )

    # Try to find relevant products
    if keywords or price_filters:
        matched = search_products(base_qs, keywords, price_filters)[:15]
    else:
        matched = base_qs.none()

    # If no specific matches, show popular/featured products
    if not matched.exists():
        matched = base_qs.order_by("-is_featured", "-created_at")[:10]
        catalog_note = "Here are some of our popular products:"
    else:
        catalog_note = "Here are products matching the customer's query:"

    # Format product catalog
    product_lines = [format_product_basic(p) for p in matched]
    catalog = "\n\n".join(product_lines) if product_lines else "No products found."

    # Get all categories for navigation help
    categories = list(
        Category.objects.filter(is_active=True, parent=None)
        .values_list("name", flat=True)
    )
    categories_str = ", ".join(categories) if categories else "No categories yet"

    system_prompt = f"""You are VendorVerse AI — the friendly, helpful shopping assistant for the VendorVerse multi-vendor marketplace.

ABOUT VENDORVERSE:
- VendorVerse is an online multi-vendor marketplace where independent vendors sell their products
- Each vendor has their own storefront with unique products
- Customers can browse products from all vendors, add to cart, and checkout
- The platform supports product reviews, wishlists, and order tracking

SITE NAVIGATION (help users find pages):
- Home page: /
- Browse all products: /products/
- Browse vendors: /vendors/
- Shopping cart: /cart/
- My orders: (must be logged in)
- Become a vendor: /vendors/apply/
- Each vendor's store: /store/<vendor-name>/

PRODUCT CATEGORIES: {categories_str}

{catalog_note}
{catalog}

RULES:
- Be helpful, concise, and friendly
- Only recommend products from the catalog listed above — NEVER invent products
- If a product isn't in the list, say you couldn't find an exact match and suggest browsing /products/
- When mentioning prices, always use ₹ (Indian Rupees) format
- If asked about a specific vendor's products, suggest visiting that vendor's storefront
- If asked about orders, tell them to check "My Orders" page (they need to be logged in)
- Keep responses under 150 words unless the user asks for details
- Use emojis sparingly for a friendly tone
- Always respond in the same language the user writes in"""

    return system_prompt


# =====================================================================
# MODE 2: STOREFRONT-SPECIFIC AI
# =====================================================================

def build_storefront_context(storefront_slug, user_message):
    """
    Build the system prompt for a vendor-specific Storefront AI assistant.
    ALL data is scoped to a SINGLE vendor — absolute data isolation.
    """
    try:
        storefront = (
            Storefront.objects.select_related("vendor")
            .get(slug=storefront_slug, vendor__is_active=True)
        )
    except Storefront.DoesNotExist:
        # Fallback to global mode if storefront not found
        return build_global_context(user_message)

    vendor = storefront.vendor

    # DATA ISOLATION: Only this vendor's active products
    vendor_products = (
        Product.objects.filter(vendor=vendor, status=Product.Status.ACTIVE)
        .select_related("category")
        .prefetch_related("variants", "tags", "reviews")
    )

    keywords = extract_keywords(user_message)
    price_filters = extract_price_filters(user_message)

    # Search within this vendor's products only
    if keywords or price_filters:
        matched = search_products(vendor_products, keywords, price_filters)[:20]
    else:
        matched = vendor_products.none()

    # If no specific matches, show all of this vendor's products
    if not matched.exists():
        matched = vendor_products.order_by("-is_featured", "-created_at")[:15]
        catalog_note = "Here are all products from this store:"
    else:
        catalog_note = "Here are products matching the customer's query from this store:"

    # Format with full detail (variants, reviews, etc.)
    product_lines = [format_product_detailed(p) for p in matched]
    catalog = "\n\n".join(product_lines) if product_lines else "This store has no products listed yet."

    # Get this vendor's categories
    vendor_categories = list(
        vendor_products.exclude(category=None)
        .values_list("category__name", flat=True)
        .distinct()
    )
    categories_str = ", ".join(vendor_categories) if vendor_categories else "No categories"

    system_prompt = f"""You are the AI shopping assistant for "{vendor.business_name}" on VendorVerse marketplace.

STORE INFORMATION:
- Store name: {vendor.business_name}
- Tagline: {storefront.tagline or 'Not set'}
- About this store: {storefront.description or 'No description available'}
- Contact email: {vendor.business_email}

STORE POLICIES:
- Shipping policy: {storefront.shipping_policy or 'Contact the store for shipping details'}
- Return policy: {storefront.return_policy or 'Contact the store for return details'}

PRODUCT CATEGORIES IN THIS STORE: {categories_str}

{catalog_note}
{catalog}

CRITICAL RULES:
- You are the assistant for "{vendor.business_name}" ONLY
- ONLY recommend products listed above — they are from this store only
- NEVER invent or hallucinate products that aren't in the list above
- NEVER mention products from other stores or vendors
- If a product isn't in the list, say: "I couldn't find that in {vendor.business_name}'s store. You can browse all their products on the store page."
- When mentioning prices, always use ₹ (Indian Rupees) format
- If asked about sizes/colors/variants, check the Variants field for each product
- If asked about shipping or returns, use the store policies above
- Keep responses under 150 words unless the user asks for details
- Be helpful, friendly, and knowledgeable about this store's products
- Always respond in the same language the user writes in"""

    return system_prompt


# =====================================================================
# MODE 3: PRODUCT-SPECIFIC AI (on product detail pages)
# =====================================================================

def build_product_context(storefront_slug, product_slug, user_message):
    """
    Build the system prompt when the user is on a specific product page.
    Has full knowledge of the product AND the vendor's storefront.
    """
    try:
        storefront = (
            Storefront.objects.select_related("vendor")
            .get(slug=storefront_slug, vendor__is_active=True)
        )
    except Storefront.DoesNotExist:
        return build_global_context(user_message)

    vendor = storefront.vendor

    # Get the specific product the user is viewing
    try:
        product = (
            Product.objects.filter(
                vendor=vendor,
                slug=product_slug,
                status=Product.Status.ACTIVE,
            )
            .select_related("category")
            .prefetch_related("variants", "tags", "reviews", "reviews__user", "questions", "questions__answers")
            .first()
        )
    except Product.DoesNotExist:
        product = None

    if not product:
        # Fallback to storefront mode
        return build_storefront_context(storefront_slug, user_message)

    # Build detailed product info
    product_info = format_product_detailed(product)

    # Add full description for the focused product
    full_desc = product.description or "No detailed description available"

    # Get reviews for this product
    reviews = product.reviews.all()[:5]
    reviews_text = ""
    if reviews:
        review_lines = []
        for r in reviews:
            stars = "★" * r.rating + "☆" * (5 - r.rating)
            verified = " (Verified Purchase)" if r.is_verified_purchase else ""
            review_lines.append(f"  {stars}{verified}: {r.comment[:150] if r.comment else r.title or 'No comment'}")
        reviews_text = "\n".join(review_lines)
    else:
        reviews_text = "  No reviews yet"

    # Get Q&A for this product
    questions = product.questions.prefetch_related("answers").all()[:5]
    qa_text = ""
    if questions:
        qa_lines = []
        for q in questions:
            qa_lines.append(f"  Q: {q.text}")
            answers = q.answers.all()[:2]
            for a in answers:
                vendor_tag = " [Vendor]" if a.is_vendor else ""
                qa_lines.append(f"    A{vendor_tag}: {a.text[:150]}")
        qa_text = "\n".join(qa_lines)
    else:
        qa_text = "  No questions asked yet"

    # Get a few other products from this vendor for cross-selling
    other_products = (
        Product.objects.filter(vendor=vendor, status=Product.Status.ACTIVE)
        .exclude(pk=product.pk)
        .select_related("category")[:5]
    )
    other_products_text = "\n\n".join([format_product_basic(p) for p in other_products])
    if not other_products_text:
        other_products_text = "No other products in this store"

    system_prompt = f"""You are the AI product assistant for "{product.name}" by "{vendor.business_name}" on VendorVerse.

The customer is currently viewing this specific product and may have questions about it.

CURRENT PRODUCT (the one the customer is viewing):
{product_info}

FULL DESCRIPTION:
{full_desc}

CUSTOMER REVIEWS:
{reviews_text}

CUSTOMER Q&A:
{qa_text}

STORE POLICIES:
- Shipping: {storefront.shipping_policy or 'Contact the store for shipping details'}
- Returns: {storefront.return_policy or 'Contact the store for return details'}

OTHER PRODUCTS FROM "{vendor.business_name}":
{other_products_text}

RULES:
- You are helping the customer with questions about "{product.name}" specifically
- Use the product details, reviews, and Q&A above to answer accurately
- If asked about variants (sizes, colors), check the Variants field
- If asked about quality or experience, reference the customer reviews
- If the product doesn't have what the customer needs, suggest other products from this store
- NEVER invent specifications, features, or details not in the information above
- NEVER mention products from other vendors/stores
- When mentioning prices, always use ₹ format
- Keep responses concise but thorough (under 200 words)
- Be like a knowledgeable salesperson — helpful, honest, and not pushy
- Always respond in the same language the user writes in"""

    return system_prompt

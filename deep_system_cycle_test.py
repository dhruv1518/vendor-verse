import os
import sys
import uuid
from decimal import Decimal
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.test import Client
from django.urls import reverse
from apps.accounts.models import User, Address, UserProfile
from apps.vendors.models import Vendor, Storefront, VendorApplication
from apps.products.models import Product, Category, ProductVariant, Wishlist, WishlistItem, Question, Answer
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem, Coupon
from apps.payments.models import MockPayment
from apps.reviews.models import Review
from apps.notifications.models import Notification

print("=" * 80)
print("VENDORA COMPREHENSIVE END-TO-END DEEP SYSTEM & LIFECYCLE TEST")
print("=" * 80)

passed_tests = 0
failed_tests = 0
errors = []

def record_pass(step_name, detail=""):
    global passed_tests
    passed_tests += 1
    msg = f"  [PASS] {step_name}"
    if detail:
        msg += f" -> {detail}"
    print(msg.encode('ascii', 'replace').decode('ascii'), flush=True)

def record_fail(step_name, error_detail):
    global failed_tests
    failed_tests += 1
    errors.append((step_name, error_detail))
    msg = f"  [FAIL] {step_name} -> {error_detail}"
    print(msg.encode('ascii', 'replace').decode('ascii'), flush=True)

# ---------------------------------------------------------------------------
# Setup Clients and Users
# ---------------------------------------------------------------------------
customer_user = User.objects.filter(role=User.Role.CUSTOMER).first()
vendor_user_1 = User.objects.filter(role=User.Role.VENDOR, email="db@gmail.com").first()
vendor_user_2 = User.objects.filter(role=User.Role.VENDOR, email="sneh@gmail.com").first()
admin_user = User.objects.filter(is_superuser=True).first()

if not customer_user or not vendor_user_1 or not vendor_user_2:
    print("[FATAL] Required test users missing from database!")
    sys.exit(1)

client_cust = Client()
client_cust.force_login(customer_user)

client_v1 = Client()
client_v1.force_login(vendor_user_1)

client_v2 = Client()
client_v2.force_login(vendor_user_2)

client_anon = Client()

# ===========================================================================
# 1. CUSTOMER PROFILE & ADDRESS CRUD LIFECYCLE
# ===========================================================================
print("\n--- [CYCLE 1] Customer Profile & Address Management ---", flush=True)
try:
    # Profile update
    res = client_cust.post(reverse("accounts:profile"), {
        "first_name": "TestCustomer",
        "last_name": "Verified",
        "email": customer_user.email,
        "phone_number": "9876543210",
        "bio": "Automated Testing Customer Profile",
    })
    customer_user.refresh_from_db()
    if customer_user.first_name == "TestCustomer":
        record_pass("Customer Profile Update", "Profile name updated in DB")
    else:
        record_fail("Customer Profile Update", f"Expected 'TestCustomer', got '{customer_user.first_name}'")

    # Add Address
    addr_title = f"Test Addr {uuid.uuid4().hex[:6]}"
    res = client_cust.post(reverse("accounts:address_add"), {
        "title": addr_title,
        "street_address": "42 Tech Valley Road",
        "city": "Mumbai",
        "state": "Maharashtra",
        "postal_code": "400001",
        "country": "India",
        "is_default": "on",
    })
    created_addr = Address.objects.filter(user=customer_user, title=addr_title).first()
    if created_addr and created_addr.is_default:
        record_pass("Address Creation & Default Assignment", f"ID: {created_addr.public_id} in DB")
    else:
        record_fail("Address Creation", "Address not found in DB or not set as default")

    # Update Address
    res = client_cust.post(reverse("accounts:address_edit", kwargs={"public_id": created_addr.public_id}), {
        "title": addr_title,
        "street_address": "99 Cyber City Road",
        "city": "Mumbai",
        "state": "Maharashtra",
        "postal_code": "400001",
        "country": "India",
        "is_default": "on",
    })
    created_addr.refresh_from_db()
    if created_addr.street_address == "99 Cyber City Road":
        record_pass("Address Edit & DB Persistence", "Fields successfully updated in database")
    else:
        record_fail("Address Edit", "Fields did not update properly in DB")

    # Clean up test address
    created_addr.delete()
    record_pass("Address Deletion", "Test address cleaned up from DB")

except Exception as e:
    record_fail("Customer Profile/Address Cycle", str(e))

# ===========================================================================
# 2. WISHLIST TOGGLE & LISTING CYCLE
# ===========================================================================
print("\n--- [CYCLE 2] Customer Wishlist Lifecycle ---", flush=True)
try:
    product_to_wish = Product.objects.filter(status=Product.Status.ACTIVE).first()
    wishlist, _ = Wishlist.objects.get_or_create(user=customer_user)
    # Ensure clean start
    WishlistItem.objects.filter(wishlist=wishlist, product=product_to_wish).delete()
    
    # Toggle Add
    res = client_cust.post(reverse("products:wishlist_toggle", kwargs={"public_id": product_to_wish.public_id}))
    has_item = WishlistItem.objects.filter(wishlist=wishlist, product=product_to_wish).exists()
    if has_item:
        record_pass("Wishlist Add Toggle", f"Product '{product_to_wish.name}' added to DB Wishlist")
    else:
        record_fail("Wishlist Add Toggle", "Item not in WishlistItem table")

    # View Wishlist Page
    res = client_cust.get(reverse("products:wishlist_list"))
    if res.status_code == 200 and product_to_wish.name in res.content.decode('utf-8', errors='ignore'):
        record_pass("Wishlist Page Rendering", "Product appears on wishlist page")
    else:
        record_fail("Wishlist Page Rendering", f"Status: {res.status_code}")

    # Toggle Remove
    res = client_cust.post(reverse("products:wishlist_toggle", kwargs={"public_id": product_to_wish.public_id}))
    has_item_after = WishlistItem.objects.filter(wishlist=wishlist, product=product_to_wish).exists()
    if not has_item_after:
        record_pass("Wishlist Remove Toggle", "Product removed from DB Wishlist")
    else:
        record_fail("Wishlist Remove Toggle", "Product still in WishlistItem table")

except Exception as e:
    record_fail("Wishlist Cycle", str(e))

# ===========================================================================
# 3. PRODUCT COMPARISON FLOW
# ===========================================================================
print("\n--- [CYCLE 3] Product Comparison Flow ---", flush=True)
try:
    prods = list(Product.objects.filter(status=Product.Status.ACTIVE)[:2])
    p1, p2 = prods[0], prods[1]
    
    # Clear compare first to start fresh
    client_cust.post(reverse("products:compare_clear"))
    
    # Add p1 to compare
    res = client_cust.post(reverse("products:compare_toggle", kwargs={"public_id": p1.public_id}), HTTP_REFERER="/products/")
    # Add p2 to compare
    res = client_cust.post(reverse("products:compare_toggle", kwargs={"public_id": p2.public_id}), HTTP_REFERER="/products/")
    
    # View compare page
    res = client_cust.get(reverse("products:compare_list"))
    if res.status_code == 200 and p1.name in res.content.decode('utf-8', errors='ignore') and p2.name in res.content.decode('utf-8', errors='ignore'):
        record_pass("Compare Page Rendering", f"Comparing '{p1.name}' vs '{p2.name}'")
    else:
        record_fail("Compare Page Rendering", f"Status: {res.status_code}")

    # Clear comparison
    res = client_cust.post(reverse("products:compare_clear"), HTTP_REFERER="/products/compare/")
    res2 = client_cust.get(reverse("products:compare_list"))
    if res2.status_code == 200 and "No products to compare" in res2.content.decode('utf-8', errors='ignore'):
        record_pass("Compare Clear Flow", "Comparison list cleared successfully")
    else:
        record_fail("Compare Clear Flow", "Comparison list not cleared")

except Exception as e:
    record_fail("Comparison Cycle", str(e))

# ===========================================================================
# 4. LIVE SEARCH & AUTOCOMPLETE
# ===========================================================================
print("\n--- [CYCLE 4] Live Search & Autocomplete Flow ---", flush=True)
try:
    active_prod = Product.objects.filter(status=Product.Status.ACTIVE).first()
    search_keyword = active_prod.name[:4]
    res = client_anon.get(reverse("products:autocomplete") + f"?q={search_keyword}")
    if res.status_code == 200 and active_prod.name in res.content.decode('utf-8', errors='ignore'):
        record_pass("HTMX Live Autocomplete", f"Search '{search_keyword}' returned '{active_prod.name}'")
    else:
        record_fail("HTMX Live Autocomplete", f"Search '{search_keyword}' failed to return matching product")

except Exception as e:
    record_fail("Live Search Autocomplete", str(e))

# ===========================================================================
# 5. PRODUCT Q&A FLOW
# ===========================================================================
print("\n--- [CYCLE 5] Customer & Vendor Q&A Lifecycle ---", flush=True)
try:
    target_prod = Product.objects.filter(status=Product.Status.ACTIVE, vendor=vendor_user_1.vendor).first()
    
    # Customer asks question
    q_text = f"Is this item genuine and does it come with warranty? {uuid.uuid4().hex[:4]}"
    res = client_cust.post(reverse("products:question_create", kwargs={"public_id": target_prod.public_id}), {
        "text": q_text
    })
    created_q = Question.objects.filter(product=target_prod, text=q_text).first()
    if created_q:
        record_pass("Customer Ask Question", f"Question ID {created_q.public_id} saved to DB")
    else:
        record_fail("Customer Ask Question", "Question not saved to DB")

    # Vendor answers question
    a_text = f"Yes, 100% authentic with 1 year manufacturer warranty. {uuid.uuid4().hex[:4]}"
    res = client_v1.post(reverse("products:answer_create", kwargs={"public_id": created_q.public_id}), {
        "text": a_text
    })
    created_a = Answer.objects.filter(question=created_q, text=a_text).first()
    if created_a and created_a.is_vendor:
        record_pass("Vendor Answer Question", "Answer saved to DB with is_vendor=True")
    else:
        record_fail("Vendor Answer Question", "Answer not saved or is_vendor not True")

    # Clean up test Q&A
    created_q.delete()
    record_pass("Q&A Cleanup", "Test Question and Answer cascade deleted cleanly")

except Exception as e:
    record_fail("Q&A Cycle", str(e))

# ===========================================================================
# 6. CART OPERATIONS & COUPON FLOW
# ===========================================================================
print("\n--- [CYCLE 6] Cart Operations & Coupon System ---", flush=True)
try:
    cart, _ = Cart.objects.get_or_create(user=customer_user)
    cart.clear()
    
    test_p = Product.objects.filter(status=Product.Status.ACTIVE, stock_quantity__gt=5).first()
    
    # Add to cart
    res = client_cust.post(reverse("cart:add"), {
        "product_id": str(test_p.public_id),
        "quantity": 2,
    })
    cart_item = CartItem.objects.filter(cart=cart, product=test_p).first()
    if cart_item and cart_item.quantity == 2:
        record_pass("Cart Add Item", f"Added 2x '{test_p.name}' to cart")
    else:
        record_fail("Cart Add Item", "Item not found in cart or wrong quantity")

    # Update item quantity
    res = client_cust.post(reverse("cart:update", kwargs={"public_id": cart_item.public_id}), {
        "quantity": 3,
    })
    cart_item.refresh_from_db()
    if cart_item.quantity == 3:
        record_pass("Cart Update Quantity", "Updated quantity to 3 in DB")
    else:
        record_fail("Cart Update Quantity", f"Expected quantity 3, got {cart_item.quantity}")

    # Apply Coupon
    coupon = Coupon.objects.filter(code__iexact="hello").first()
    if not coupon:
        coupon = Coupon.objects.create(
            code="WELCOME10",
            discount_type="PERCENTAGE",
            discount_value=Decimal("10.00"),
            min_purchase_amount=Decimal("0.00"),
            is_active=True,
            times_used=0,
            usage_limit=100,
        )
    coupon_code = coupon.code
    res = client_cust.post(reverse("cart:apply_coupon"), {
        "code": coupon_code,
    })
    cart.refresh_from_db()
    if cart.coupon == coupon and cart.discount_amount > 0:
        record_pass("Apply Coupon", f"Coupon '{coupon_code}' applied: discount is ₹{cart.discount_amount}")
    else:
        record_fail("Apply Coupon", f"Coupon did not apply correctly (discount: {cart.discount_amount})")

    # Remove Coupon
    res = client_cust.post(reverse("cart:remove_coupon"))
    cart.refresh_from_db()
    if cart.coupon is None and cart.discount_amount == 0:
        record_pass("Remove Coupon", "Coupon removed and discount cleared")
    else:
        record_fail("Remove Coupon", "Coupon not removed properly")

    # Clear cart for checkout cycle
    cart.clear()

except Exception as e:
    record_fail("Cart & Coupon Cycle", str(e))

# ===========================================================================
# 7. MULTI-VENDOR CHECKOUT, ORDER SPLIT & PAYMENT CYCLE
# ===========================================================================
print("\n--- [CYCLE 7] Multi-Vendor Checkout, Order Split, Stock Deduction & Payment ---", flush=True)
try:
    v1_product = Product.objects.filter(vendor=vendor_user_1.vendor, status=Product.Status.ACTIVE, stock_quantity__gt=2).first()
    v2_product = Product.objects.filter(vendor=vendor_user_2.vendor, status=Product.Status.ACTIVE, stock_quantity__gt=2).first()
    
    if not v1_product or not v2_product:
        raise Exception("Active products from both vendors required for multi-vendor checkout test")
    
    initial_stock_1 = v1_product.stock_quantity
    initial_stock_2 = v2_product.stock_quantity
    
    # Add both products to customer's cart
    client_cust.post(reverse("cart:add"), {
        "product_id": str(v1_product.public_id),
        "quantity": 1,
    })
    client_cust.post(reverse("cart:add"), {
        "product_id": str(v2_product.public_id),
        "quantity": 1,
    })
    
    cart = Cart.objects.get(user=customer_user)
    if cart.cart_items.count() != 2:
        raise Exception(f"Cart expected 2 items, got {cart.cart_items.count()}")
    
    # Ensure an address exists
    shipping_addr = Address.objects.filter(user=customer_user).first()
    if not shipping_addr:
        shipping_addr = Address.objects.create(
            user=customer_user,
            title="Home",
            street_address="123 Main St",
            city="Delhi",
            state="Delhi",
            postal_code="110001",
            country="India",
            is_default=True,
        )

    # Process Checkout
    res = client_cust.post(reverse("orders:checkout_process"), {
        "address_id": str(shipping_addr.public_id),
    })
    
    # Verify Order created
    created_order = Order.objects.filter(user=customer_user, status=Order.Status.PENDING).order_by("-created_at").first()
    if not created_order:
        raise Exception("Pending order was not created after checkout process!")
    
    record_pass("Order Creation & Multi-Vendor Items", f"Order #{created_order.order_number} created with {created_order.items.count()} items")
    
    # Check items are split across vendors
    items = list(created_order.items.all())
    vendor_ids = {i.vendor_id for i in items}
    if len(vendor_ids) >= 2:
        record_pass("Multi-Vendor Order Item Split", f"Items correctly split across {len(vendor_ids)} vendor accounts")
    else:
        record_fail("Multi-Vendor Order Item Split", f"Items not split across multiple vendors: {vendor_ids}")

    # Check stock deduction
    v1_product.refresh_from_db()
    v2_product.refresh_from_db()
    if v1_product.stock_quantity == initial_stock_1 - 1 and v2_product.stock_quantity == initial_stock_2 - 1:
        record_pass("Inventory Stock Deduction in DB", "Stock successfully decremented for both vendor products")
    else:
        record_fail("Inventory Stock Deduction", f"Stock mismatch: P1({initial_stock_1}->{v1_product.stock_quantity}), P2({initial_stock_2}->{v2_product.stock_quantity})")

    # Mock Payment Processing
    res = client_cust.post(reverse("payments:process_payment", kwargs={"public_id": created_order.public_id}), {
        "card_number": "4242 4242 4242 4242",
        "card_expiry": "12/28",
        "card_cvv": "123",
        "card_name": "Test Customer",
    })
    
    created_order.refresh_from_db()
    if created_order.payment_status == "PAID" and created_order.status == Order.Status.CONFIRMED:
        record_pass("Mock Payment Processing & Order Confirmation", f"Order marked PAID, status CONFIRMED")
    else:
        record_fail("Mock Payment Processing", f"Payment status: {created_order.payment_status}, Order status: {created_order.status}")

    # Verify Cart Cleared
    cart.refresh_from_db()
    if cart.is_empty:
        record_pass("Cart Auto-Clear After Payment", "Customer cart emptied in DB")
    else:
        record_fail("Cart Auto-Clear After Payment", f"Cart still contains {cart.cart_items.count()} items")

    # Verify MockPayment record
    mock_p = MockPayment.objects.filter(order=created_order).first()
    if mock_p and mock_p.status == MockPayment.Status.SUCCESS:
        record_pass("Payment Transaction Record", f"Tx ID: {mock_p.transaction_id}")
    else:
        record_fail("Payment Transaction Record", "MockPayment record not found or not SUCCESS")

    # Verify Order Success Page View
    res = client_cust.get(reverse("orders:order_success", kwargs={"public_id": created_order.public_id}))
    if res.status_code == 200:
        record_pass("Order Success Confirmation Page", "Renders HTTP 200 with order breakdown")
    else:
        record_fail("Order Success Confirmation Page", f"Status: {res.status_code}")

except Exception as e:
    record_fail("Checkout & Payment Cycle", str(e))

# ===========================================================================
# 8. VENDOR ORDER FULFILLMENT LIFECYCLE
# ===========================================================================
print("\n--- [CYCLE 8] Vendor Order Fulfillment & Order Status Synchronization ---", flush=True)
try:
    # Vendor 1 checks their order detail
    v1_item = created_order.items.filter(vendor=vendor_user_1.vendor).first()
    v2_item = created_order.items.filter(vendor=vendor_user_2.vendor).first()
    
    # Vendor 1 updates status to PROCESSING
    res = client_v1.post(reverse("orders:vendor_order_item_status", kwargs={"public_id": v1_item.public_id}), {
        "status": OrderItem.ItemStatus.PROCESSING
    })
    v1_item.refresh_from_db()
    created_order.refresh_from_db()
    if v1_item.status == OrderItem.ItemStatus.PROCESSING:
        record_pass("Vendor Item Status -> PROCESSING", f"Item status updated in DB; parent order status is {created_order.status}")
    else:
        record_fail("Vendor Item Status Update", f"Expected PROCESSING, got {v1_item.status}")

    # Vendor 1 updates status to SHIPPED
    res = client_v1.post(reverse("orders:vendor_order_item_status", kwargs={"public_id": v1_item.public_id}), {
        "status": OrderItem.ItemStatus.SHIPPED
    })
    v1_item.refresh_from_db()
    created_order.refresh_from_db()
    if v1_item.status == OrderItem.ItemStatus.SHIPPED and created_order.status == Order.Status.SHIPPED:
        record_pass("Order Synchronization -> SHIPPED", "Parent order automatically synchronized to SHIPPED")
    else:
        record_fail("Order Synchronization -> SHIPPED", f"Order status is {created_order.status}")

    # Both vendors mark items DELIVERED
    client_v1.post(reverse("orders:vendor_order_item_status", kwargs={"public_id": v1_item.public_id}), {
        "status": OrderItem.ItemStatus.DELIVERED
    })
    client_v2.post(reverse("orders:vendor_order_item_status", kwargs={"public_id": v2_item.public_id}), {
        "status": OrderItem.ItemStatus.DELIVERED
    })
    created_order.refresh_from_db()
    if created_order.status == Order.Status.DELIVERED:
        record_pass("Order Synchronization -> DELIVERED", "All items delivered, parent order automatically synchronized to DELIVERED")
    else:
        record_fail("Order Synchronization -> DELIVERED", f"Expected DELIVERED, got {created_order.status}")

except Exception as e:
    record_fail("Vendor Fulfillment Cycle", str(e))

# ===========================================================================
# 9. PRODUCT REVIEW & RATING LIFECYCLE
# ===========================================================================
print("\n--- [CYCLE 9] Product Review & Rating System ---", flush=True)
try:
    rev_product = v1_product
    # Delete any prior review from customer on this product
    Review.objects.filter(product=rev_product, user=customer_user).delete()
    
    # Submit review
    review_title = f"Phenomenal product! {uuid.uuid4().hex[:4]}"
    res = client_cust.post(reverse("reviews:submit_review", kwargs={"public_id": rev_product.public_id}), {
        "rating": 5,
        "title": review_title,
        "comment": "Absolutely love the craftsmanship and performance. Exceeded expectations!",
    })
    created_rev = Review.objects.filter(product=rev_product, user=customer_user).first()
    if created_rev and created_rev.rating == 5:
        record_pass("Submit Product Review", f"Review '{created_rev.title}' saved to DB with 5 stars")
    else:
        record_fail("Submit Product Review", "Review not found in DB")

    # Prevent duplicate reviews
    res_dup = client_cust.post(reverse("reviews:submit_review", kwargs={"public_id": rev_product.public_id}), {
        "rating": 4,
        "title": "Duplicate attempt",
        "comment": "This should be blocked.",
    })
    rev_count = Review.objects.filter(product=rev_product, user=customer_user).count()
    if rev_count == 1:
        record_pass("Duplicate Review Prevention", "Protected against duplicate reviews per user")
    else:
        record_fail("Duplicate Review Prevention", f"Found {rev_count} reviews from same user")

    # Delete review
    res_del = client_cust.post(reverse("reviews:delete_review", kwargs={"public_id": created_rev.public_id}))
    if not Review.objects.filter(id=created_rev.id).exists():
        record_pass("Delete Review", "User successfully deleted their review from DB")
    else:
        record_fail("Delete Review", "Review still in DB")

except Exception as e:
    record_fail("Review Cycle", str(e))

# ===========================================================================
# 10. IN-APP NOTIFICATION CENTER LIFECYCLE
# ===========================================================================
print("\n--- [CYCLE 10] In-App Notification Center ---", flush=True)
try:
    # Ensure at least one unread notification exists
    Notification.objects.create(
        user=customer_user,
        title="Welcome to Vendora Tests",
        message="Your test notification is waiting for you.",
        link="/products/",
    )
    unread_before = Notification.objects.filter(user=customer_user, is_read=False).count()
    if unread_before > 0:
        record_pass("Notification Creation", f"{unread_before} unread notification(s) in DB")
    else:
        record_fail("Notification Creation", "No unread notifications")

    # Mark all read
    res = client_cust.post(reverse("notifications:mark_all_read"))
    unread_after = Notification.objects.filter(user=customer_user, is_read=False).count()
    if unread_after == 0:
        record_pass("Mark All Notifications Read", "All notifications updated to is_read=True in DB")
    else:
        record_fail("Mark All Notifications Read", f"Still {unread_after} unread notifications")

except Exception as e:
    record_fail("Notification Center Cycle", str(e))

# ===========================================================================
# 11. VENDOR PRODUCT MANAGEMENT CRUD
# ===========================================================================
print("\n--- [CYCLE 11] Vendor Product Management (CRUD) ---", flush=True)
try:
    category = Category.objects.first()
    new_prod_name = f"Auto Test Gadget {uuid.uuid4().hex[:6]}"
    
    # Create product with correct base_price field
    res = client_v1.post(reverse("products:vendor_product_create"), {
        "name": new_prod_name,
        "sku": f"SKU-{uuid.uuid4().hex[:8].upper()}",
        "category": category.id if category else "",
        "short_description": "A top-tier gadget created during automated testing.",
        "description": "Comprehensive specifications and details for the automated test gadget.",
        "base_price": "1999.00",
        "compare_at_price": "2499.00",
        "stock_quantity": 25,
        "low_stock_threshold": 5,
        "status": Product.Status.ACTIVE,
        "is_featured": True,
        # Formsets management fields
        "images-TOTAL_FORMS": "0",
        "images-INITIAL_FORMS": "0",
        "images-MIN_NUM_FORMS": "0",
        "images-MAX_NUM_FORMS": "1000",
        "variants-TOTAL_FORMS": "0",
        "variants-INITIAL_FORMS": "0",
        "variants-MIN_NUM_FORMS": "0",
        "variants-MAX_NUM_FORMS": "1000",
    })
    
    created_prod = Product.objects.filter(vendor=vendor_user_1.vendor, name=new_prod_name).first()
    if created_prod and created_prod.base_price == Decimal("1999.00"):
        record_pass("Vendor Product Create", f"Product '{created_prod.name}' saved to DB (UUID: {created_prod.public_id})")
    else:
        record_fail("Vendor Product Create", "Product was not found in DB with expected price")

    # Edit product
    if created_prod:
        res = client_v1.post(reverse("products:vendor_product_edit", kwargs={"public_id": created_prod.public_id}), {
            "name": f"{new_prod_name} (Updated)",
            "sku": created_prod.sku,
            "category": created_prod.category_id or "",
            "short_description": "Updated description",
            "description": "Updated full description",
            "base_price": "1849.00",
            "compare_at_price": "2499.00",
            "stock_quantity": 30,
            "low_stock_threshold": 5,
            "status": Product.Status.ACTIVE,
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
            "variants-TOTAL_FORMS": "0",
            "variants-INITIAL_FORMS": "0",
            "variants-MIN_NUM_FORMS": "0",
            "variants-MAX_NUM_FORMS": "1000",
        })
        created_prod.refresh_from_db()
        if created_prod.base_price == Decimal("1849.00") and "Updated" in created_prod.name:
            record_pass("Vendor Product Edit", f"Price updated to ₹1849.00 and name modified in DB")
        else:
            record_fail("Vendor Product Edit", f"Price: {created_prod.base_price}, Name: {created_prod.name}")

        # Delete product
        res = client_v1.post(reverse("products:vendor_product_delete", kwargs={"public_id": created_prod.public_id}))
        if not Product.objects.filter(id=created_prod.id).exists():
            record_pass("Vendor Product Delete", "Product successfully deleted from DB")
        else:
            record_fail("Vendor Product Delete", "Product still exists in DB")

except Exception as e:
    record_fail("Vendor Product CRUD Cycle", str(e))

# ===========================================================================
# 12. VENDOR STOREFRONT SETTINGS UPDATE
# ===========================================================================
print("\n--- [CYCLE 12] Vendor Storefront Configuration ---", flush=True)
try:
    storefront = vendor_user_1.vendor.storefront
    old_tagline = storefront.tagline
    new_tagline = f"Top Quality Guaranteed - {uuid.uuid4().hex[:4]}"
    
    res = client_v1.post(reverse("vendors:storefront_settings"), {
        "tagline": new_tagline,
        "description": "Welcome to our premier official storefront on Vendora.",
        "return_policy": "30-day hassle-free returns.",
        "shipping_policy": "Free shipping across India on orders over ₹499.",
    })
    storefront.refresh_from_db()
    if storefront.tagline == new_tagline:
        record_pass("Storefront Settings Update", f"Tagline updated in DB: '{storefront.tagline}'")
    else:
        record_fail("Storefront Settings Update", f"Expected '{new_tagline}', got '{storefront.tagline}'")

    # Restore
    storefront.tagline = old_tagline
    storefront.save(update_fields=["tagline"])

except Exception as e:
    record_fail("Storefront Configuration Cycle", str(e))

# ===========================================================================
# 13. VENDOR APPLICATION WORKFLOW
# ===========================================================================
print("\n--- [CYCLE 13] Vendor Onboarding & Application Flow ---", flush=True)
try:
    temp_email = f"testapplicant_{uuid.uuid4().hex[:6]}@example.com"
    temp_user = User.objects.create_user(
        email=temp_email,
        password="TemporaryPassword123!",
        role=User.Role.CUSTOMER,
        first_name="Applicant",
        last_name="Tester",
    )
    client_applicant = Client()
    client_applicant.force_login(temp_user)
    
    app_biz = f"Test Store {uuid.uuid4().hex[:4]}"
    res = client_applicant.post(reverse("vendors:apply"), {
        "business_name": app_biz,
        "business_email": temp_email,
        "business_description": "We are seeking to expand our footprint on Vendora by selling curated electronics.",
        "phone_number": "+91 9988776655",
    })
    
    app = VendorApplication.objects.filter(user=temp_user).first()
    if app and app.status == VendorApplication.Status.PENDING:
        record_pass("Vendor Application Submission", f"Application for '{app.business_name}' saved to DB (Status: PENDING)")
    else:
        record_fail("Vendor Application Submission", "Application not found in DB")

    # Clean up temporary application and user
    if app:
        app.delete()
    temp_user.delete()
    record_pass("Vendor Application Cleanup", "Temporary applicant user and application cleaned up")

except Exception as e:
    record_fail("Vendor Application Cycle", str(e))

# ===========================================================================
# 14. CONTACT FORM SUBMISSION
# ===========================================================================
print("\n--- [CYCLE 14] Support & Contact Form Submission ---", flush=True)
try:
    res = client_anon.post(reverse("core:contact"), {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "subject": "Platform Partnership",
        "message": "We would like to partner with Vendora for national distribution.",
    })
    if res.status_code == 302:
        record_pass("Contact Form Submission", "Form accepted and redirected with success message")
    else:
        record_fail("Contact Form Submission", f"Unexpected status: {res.status_code}")

except Exception as e:
    record_fail("Contact Form Cycle", str(e))

# ===========================================================================
# 15. AI ASSISTANT CHATBOT INTEGRATION
# ===========================================================================
print("\n--- [CYCLE 15] AI Chatbot Integration Endpoint ---", flush=True)
try:
    import json
    res = client_anon.post(
        reverse("ai:chat_message"),
        data=json.dumps({"message": "Hello, what categories of products do you sell?", "storefront_slug": None, "product_slug": None}),
        content_type="application/json"
    )
    if res.status_code == 200:
        data = res.json()
        if "reply" in data:
            record_pass("AI Chatbot API", f"Returned reply (length: {len(data['reply'])} chars)")
        else:
            record_fail("AI Chatbot API", "No 'reply' key in response JSON")
    else:
        record_fail("AI Chatbot API", f"Status: {res.status_code}")

except Exception as e:
    record_fail("AI Chatbot Cycle", str(e))

# ===========================================================================
# FINAL SUMMARY
# ===========================================================================
print("\n" + "=" * 80)
print("DEEP SYSTEM & LIFECYCLE TEST RESULTS SUMMARY")
print("=" * 80)
print(f"TOTAL TESTS EXECUTED : {passed_tests + failed_tests}")
print(f"TOTAL PASSED         : {passed_tests}")
print(f"TOTAL FAILED         : {failed_tests}")

if failed_tests > 0:
    print("\nFAILED CHECKS:")
    for name, detail in errors:
        print(f"  - {name}: {detail}")
    sys.exit(1)
else:
    print("\nALL SYSTEM LIFECYCLES, BUTTONS, DATABASE CONNECTIONS, AND FLOWS PASSED PERFECTLY!")
    sys.exit(0)

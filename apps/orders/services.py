import uuid
from decimal import Decimal
from django.utils import timezone

from .models import Order, OrderItem


def create_order_from_cart(user, cart, address):
    """
    Convert a cart into an Order with OrderItems.
    
    Args:
        user: The user placing the order.
        cart: The Cart instance containing items.
        address: An Address instance for shipping.
    
    Returns:
        The created Order instance.
    """
    # Calculate subtotal from cart
    subtotal = cart.subtotal
    shipping_cost = Decimal("0.00")  # Free shipping for this demo
    
    # AF-E: Apply coupon discount
    discount_amount = Decimal("0.00")
    coupon_code = ""
    if cart.coupon and cart.coupon.is_valid:
        discount_amount = Decimal(str(cart.discount_amount))
        coupon_code = cart.coupon.code
        
        # Increment usage
        cart.coupon.times_used += 1
        cart.coupon.save(update_fields=["times_used"])
        
    total = subtotal - discount_amount + shipping_cost

    # Create the order with address snapshot
    order = Order.objects.create(
        user=user,
        shipping_name=f"{user.first_name} {user.last_name}".strip() or user.email,
        shipping_address=address.street_address,
        shipping_city=address.city,
        shipping_state=address.state,
        shipping_postal_code=address.postal_code,
        shipping_country=address.country,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        discount_amount=discount_amount,
        coupon_code=coupon_code,
        total=total,
        status=Order.Status.PENDING,
    )

    # Create order items from cart items
    for cart_item in cart.cart_items.select_related("product", "variant", "product__vendor"):
        OrderItem.objects.create(
            order=order,
            vendor=cart_item.product.vendor,
            product=cart_item.product,
            variant=cart_item.variant,
            product_name=cart_item.product.name,
            variant_name=cart_item.variant.name if cart_item.variant else "",
            unit_price=cart_item.unit_price,
            quantity=cart_item.quantity,
            status=OrderItem.ItemStatus.PENDING,
        )

        # Decrement stock
        if cart_item.variant:
            cart_item.variant.stock_quantity = max(
                0, cart_item.variant.stock_quantity - cart_item.quantity
            )
            cart_item.variant.save()
        else:
            cart_item.product.stock_quantity = max(
                0, cart_item.product.stock_quantity - cart_item.quantity
            )
            cart_item.product.save()

    return order


def process_mock_payment(order, card_last_four="4242", card_brand="Visa"):
    """
    Simulate processing a payment for the order.
    
    Returns:
        A tuple (success: bool, transaction_id: str)
    """
    from apps.payments.models import MockPayment

    transaction_id = f"MOCK-{uuid.uuid4().hex[:12].upper()}"

    payment = MockPayment.objects.create(
        order=order,
        user=order.user,
        amount=order.total,
        card_last_four=card_last_four,
        card_brand=card_brand,
        status=MockPayment.Status.SUCCESS,
        transaction_id=transaction_id,
    )

    # Mark order as paid and synchronize item statuses
    order.payment_status = "PAID"
    order.paid_at = timezone.now()
    order.status = Order.Status.CONFIRMED
    order.save()

    # Align items inside with confirmed order status
    order.items.filter(status=OrderItem.ItemStatus.PENDING).update(
        status=OrderItem.ItemStatus.CONFIRMED
    )

    # Group items by vendor
    vendor_items_map = {}
    for item in order.items.select_related("vendor", "vendor__user"):
        if item.vendor:
            vendor_items_map.setdefault(item.vendor, []).append(item)

    # ----- In-app Notifications -----
    try:
        from apps.notifications.models import Notification
        from django.urls import reverse

        # Customer Notification
        Notification.objects.create(
            user=order.user,
            title=f"Order Confirmed: {order.order_number}",
            message=f"Thank you! Your order #{order.order_number} containing {order.item_count} item(s) has been placed successfully.",
            link=reverse("orders:customer_order_detail", kwargs={"public_id": order.public_id}),
        )

        # Vendor Notifications
        for vendor, items in vendor_items_map.items():
            if getattr(vendor, "user", None):
                item_names = ", ".join(i.product_name for i in items[:2])
                if len(items) > 2:
                    item_names += f" and {len(items) - 2} more"
                v_total = sum(i.line_total for i in items)
                Notification.objects.create(
                    user=vendor.user,
                    title=f"New Order Received: {order.order_number}",
                    message=f"You received an order for {item_names} (Total: ₹{v_total}) from {order.shipping_name}.",
                    link=reverse("orders:vendor_order_detail", kwargs={"public_id": order.public_id}),
                )
    except Exception:
        pass  # Notification failures should not break payment completion

    # ----- Task 38: Send email notifications -----
    try:
        from apps.notifications.services import (
            send_order_confirmation_email,
            send_vendor_new_order_email,
        )
        send_order_confirmation_email(order)
        for vendor, items in vendor_items_map.items():
            send_vendor_new_order_email(vendor, order, items)
    except Exception:
        pass  # Email failures should not block the payment flow

    return True, transaction_id


def sync_order_status(order):
    """
    Synchronizes an overall Order status based on the statuses of its individual OrderItems.
    Rules:
      - If all items are CANCELLED -> CANCELLED
      - Else if all items are DELIVERED -> DELIVERED
      - Else if any item is DELIVERED or SHIPPED -> SHIPPED
      - Else if any item is PROCESSING -> PROCESSING
      - Else if any item is CONFIRMED -> CONFIRMED
      - Else -> PENDING
    """
    items = list(order.items.all())
    if not items:
        return order.status

    statuses = [item.status for item in items]

    if all(s == OrderItem.ItemStatus.CANCELLED for s in statuses):
        new_status = Order.Status.CANCELLED
    elif all(s == OrderItem.ItemStatus.DELIVERED for s in statuses):
        new_status = Order.Status.DELIVERED
    elif any(s in (OrderItem.ItemStatus.SHIPPED, OrderItem.ItemStatus.DELIVERED) for s in statuses):
        new_status = Order.Status.SHIPPED
    elif any(s == OrderItem.ItemStatus.PROCESSING for s in statuses):
        new_status = Order.Status.PROCESSING
    elif any(s == OrderItem.ItemStatus.CONFIRMED for s in statuses):
        new_status = Order.Status.CONFIRMED
    else:
        new_status = Order.Status.PENDING

    if order.status != new_status:
        order.status = new_status
        order.save(update_fields=["status", "updated_at"])

    return order.status

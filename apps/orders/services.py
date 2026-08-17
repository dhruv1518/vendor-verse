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
    total = subtotal + shipping_cost

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

    # Mark order as paid
    order.payment_status = "PAID"
    order.paid_at = timezone.now()
    order.status = Order.Status.CONFIRMED
    order.save()

    return True, transaction_id

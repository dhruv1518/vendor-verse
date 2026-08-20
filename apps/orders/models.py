import uuid
from django.db import models
from django.conf import settings

from apps.core.models import TimeStampedModel, PublicIDModel


# ---------------------------------------------------------------------------
# Task 32 — Order & OrderItem Models
# ---------------------------------------------------------------------------

class Order(TimeStampedModel, PublicIDModel):
    """
    Represents a completed order placed by a customer.
    An order can contain items from multiple vendors.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        PROCESSING = "PROCESSING", "Processing"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    # Generate a user-friendly order number
    order_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    # Shipping address (snapshot at time of order)
    shipping_name = models.CharField(max_length=200)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default="India")

    # Totals
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # Payment info
    payment_method = models.CharField(max_length=50, default="Mock Card Payment")
    payment_status = models.CharField(
        max_length=20,
        choices=[("PAID", "Paid"), ("UNPAID", "Unpaid"), ("REFUNDED", "Refunded")],
        default="UNPAID",
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number: VV-XXXXXXXX (8 hex chars)
            self.order_number = f"VV-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(TimeStampedModel, PublicIDModel):
    """
    A single line item within an order.
    Stores a snapshot of the product info at the time of purchase.
    """

    class ItemStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )

    # Snapshot fields (preserved even if the product is later changed/deleted)
    product_name = models.CharField(max_length=255)
    variant_name = models.CharField(max_length=150, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    status = models.CharField(
        max_length=20,
        choices=ItemStatus.choices,
        default=ItemStatus.PENDING,
        db_index=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity


# ---------------------------------------------------------------------------
# AF-E: Coupon / Discount System
# ---------------------------------------------------------------------------

class Coupon(TimeStampedModel, PublicIDModel):
    """Discount codes that can be applied to carts/orders."""
    
    code = models.CharField(max_length=50, unique=True, db_index=True)
    discount_percentage = models.PositiveIntegerField(
        help_text="Discount percentage (e.g., 10 for 10%)"
    )
    max_uses = models.PositiveIntegerField(
        null=True, blank=True, help_text="Maximum times this coupon can be used across all users"
    )
    times_used = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.code
        
    @property
    def is_valid(self):
        from django.utils import timezone
        if not self.is_active:
            return False
        if self.max_uses is not None and self.times_used >= self.max_uses:
            return False
        now = timezone.now()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return True

from django.db import models
from django.conf import settings

from apps.core.models import TimeStampedModel, PublicIDModel


# ---------------------------------------------------------------------------
# Task 28 — Cart Model (database-backed multi-vendor cart)
# ---------------------------------------------------------------------------

class Cart(TimeStampedModel, PublicIDModel):
    """
    Shopping cart for a logged-in user.
    Each user has at most one active cart at a time.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Cart for {self.user.email}"

    @property
    def items(self):
        return self.cart_items.all()

    @property
    def total_items(self):
        return sum(item.quantity for item in self.cart_items.all())

    @property
    def subtotal(self):
        return sum(item.line_total for item in self.cart_items.all())

    @property
    def is_empty(self):
        return self.cart_items.count() == 0

    def clear(self):
        """Remove all items from the cart."""
        self.cart_items.all().delete()


class CartItem(TimeStampedModel, PublicIDModel):
    """
    A single line item in a cart, referencing a product and optionally a variant.
    """

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("cart", "product", "variant")]

    def __str__(self):
        name = self.product.name
        if self.variant:
            name += f" ({self.variant.name})"
        return f"{name} × {self.quantity}"

    @property
    def unit_price(self):
        """Return variant price if selected, otherwise product base price."""
        if self.variant:
            return self.variant.effective_price
        return self.product.base_price

    @property
    def line_total(self):
        return self.unit_price * self.quantity

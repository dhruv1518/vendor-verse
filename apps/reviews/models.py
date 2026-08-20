from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.core.models import TimeStampedModel, PublicIDModel


# ---------------------------------------------------------------------------
# Task 36 — Review Model & Product Ratings
# ---------------------------------------------------------------------------

class Review(TimeStampedModel, PublicIDModel):
    """
    A customer review for a product.
    Only customers who have purchased and received the product (via a DELIVERED
    order item) should be able to leave a review. One review per user per product.
    """

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    order_item = models.ForeignKey(
        "orders.OrderItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="review",
        help_text="The specific order item this review is associated with.",
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Star rating from 1 to 5.",
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional review headline.",
    )
    comment = models.TextField(
        blank=True,
        help_text="Detailed review text.",
    )
    is_verified_purchase = models.BooleanField(
        default=False,
        help_text="Set automatically when the user has a completed order for this product.",
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("product", "user")]

    def __str__(self):
        return f"{self.user.email} → {self.product.name} ({self.rating}★)"

    def save(self, *args, **kwargs):
        # Auto-mark verified purchase if user has a delivered order for this product
        if not self.is_verified_purchase:
            from apps.orders.models import OrderItem
            has_purchase = OrderItem.objects.filter(
                order__user=self.user,
                product=self.product,
                order__payment_status="PAID",
            ).exists()
            self.is_verified_purchase = has_purchase
        super().save(*args, **kwargs)

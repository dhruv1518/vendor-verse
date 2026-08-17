from django.db import models
from django.conf import settings

from apps.core.models import TimeStampedModel, PublicIDModel


# ---------------------------------------------------------------------------
# Task 31 — Mock Payment Model
# ---------------------------------------------------------------------------

class MockPayment(TimeStampedModel, PublicIDModel):
    """
    Records a mock (simulated) payment transaction.
    No real money is processed — this is for demonstration purposes only.
    """

    class Status(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payment",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    card_last_four = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, default="Visa")

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUCCESS,
    )
    transaction_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated mock transaction ID.",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Mock Payment"
        verbose_name_plural = "Mock Payments"

    def __str__(self):
        return f"Payment {self.transaction_id} — ₹{self.amount}"

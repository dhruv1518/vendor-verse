from django.contrib import admin
from .models import Review


# ---------------------------------------------------------------------------
# Task 36 — Review Admin
# ---------------------------------------------------------------------------

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "user",
        "rating",
        "title",
        "is_verified_purchase",
        "created_at",
    ]
    list_filter = ["rating", "is_verified_purchase", "created_at"]
    search_fields = ["product__name", "user__email", "title", "comment"]
    readonly_fields = ["public_id", "is_verified_purchase", "created_at", "updated_at"]
    raw_id_fields = ["product", "user", "order_item"]
    ordering = ["-created_at"]

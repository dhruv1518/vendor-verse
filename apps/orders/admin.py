from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "variant_name", "unit_price", "line_total")
    raw_id_fields = ("product", "variant", "vendor")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "status",
        "payment_status",
        "total",
        "created_at",
    )
    list_filter = ("status", "payment_status", "created_at")
    search_fields = ("order_number", "user__email")
    readonly_fields = ("public_id", "order_number", "created_at", "updated_at")
    inlines = [OrderItemInline]

    fieldsets = (
        (None, {
            "fields": ("public_id", "order_number", "user", "status"),
        }),
        ("Shipping", {
            "fields": (
                "shipping_name", "shipping_address", "shipping_city",
                "shipping_state", "shipping_postal_code", "shipping_country",
            ),
        }),
        ("Payment", {
            "fields": (
                "subtotal", "shipping_cost", "total",
                "payment_method", "payment_status", "paid_at",
            ),
        }),
        ("Notes", {
            "fields": ("notes",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

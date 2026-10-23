from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Order, OrderItem, Coupon


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "variant_name", "unit_price", "line_total")
    raw_id_fields = ("product", "variant", "vendor")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_badge",
        "is_active",
        "validity_status",
        "times_used",
        "max_uses",
        "valid_from",
        "valid_until",
        "created_at",
    )
    list_filter = ("is_active", "created_at", "valid_from", "valid_until")
    search_fields = ("code",)
    readonly_fields = ("public_id", "times_used", "created_at", "updated_at", "status_overview")
    
    fieldsets = (
        ("Coupon Information", {
            "fields": ("code", "discount_percentage", "is_active", "status_overview"),
            "description": "Specify the coupon code customers will enter at checkout and the percentage discount.",
        }),
        ("Usage Limits", {
            "fields": ("max_uses", "times_used"),
            "description": "Maximum number of times this coupon can be redeemed across all customers.",
        }),
        ("Validity Schedule", {
            "fields": ("valid_from", "valid_until"),
            "description": "Optional schedule window. Leave blank for no expiration date.",
        }),
        ("System Metadata", {
            "fields": ("public_id", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Discount")
    def discount_badge(self, obj):
        return format_html(
            '<span style="background: #eef2ff; color: #4f46e5; font-weight: 700; padding: 3px 10px; border-radius: 9999px; font-size: 12px; border: 1px solid #c7d2fe;">{}% OFF</span>',
            obj.discount_percentage
        )

    @admin.display(description="Status")
    def validity_status(self, obj):
        if not obj.is_active:
            return format_html('<span style="background: #fee2e2; color: #dc2626; font-weight: 600; padding: 2px 8px; border-radius: 6px; font-size: 11px;">Inactive</span>')
        if obj.max_uses is not None and obj.times_used >= obj.max_uses:
            return format_html('<span style="background: #fef3c7; color: #d97706; font-weight: 600; padding: 2px 8px; border-radius: 6px; font-size: 11px;">Maxed Out ({}/{})</span>', obj.times_used, obj.max_uses)
        now = timezone.now()
        if obj.valid_from and now < obj.valid_from:
            return format_html('<span style="background: #f1f5f9; color: #64748b; font-weight: 600; padding: 2px 8px; border-radius: 6px; font-size: 11px;">Scheduled</span>')
        if obj.valid_until and now > obj.valid_until:
            return format_html('<span style="background: #fee2e2; color: #dc2626; font-weight: 600; padding: 2px 8px; border-radius: 6px; font-size: 11px;">Expired</span>')
        return format_html('<span style="background: #dcfce7; color: #16a34a; font-weight: 600; padding: 2px 8px; border-radius: 6px; font-size: 11px;">Active & Valid</span>')

    @admin.display(description="Current Status")
    def status_overview(self, obj):
        if not obj.pk:
            return "Save coupon to view live status."
        if obj.is_valid:
            return format_html('<span style="color: #16a34a; font-weight: 600;">Active & valid for customer orders</span>')
        return format_html('<span style="color: #dc2626; font-weight: 600;">Invalid (Inactive, expired, or max uses reached)</span>')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "status",
        "payment_status",
        "subtotal",
        "coupon_code",
        "discount_amount",
        "total",
        "created_at",
    )
    list_filter = ("status", "payment_status", "created_at")
    search_fields = ("order_number", "user__email", "coupon_code")
    readonly_fields = ("public_id", "order_number", "coupon_code", "discount_amount", "created_at", "updated_at")
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
        ("Payment & Discounts", {
            "fields": (
                "subtotal", "shipping_cost", "coupon_code", "discount_amount", "total",
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


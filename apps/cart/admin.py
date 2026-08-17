from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("unit_price", "line_total")
    raw_id_fields = ("product", "variant")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "total_items", "subtotal", "created_at")
    readonly_fields = ("public_id", "created_at", "updated_at")
    search_fields = ("user__email",)
    inlines = [CartItemInline]

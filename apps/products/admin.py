from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Tag, Product, ProductImage, ProductVariant


# ---------------------------------------------------------------------------
# Task 21 — Category Admin
# ---------------------------------------------------------------------------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug", "is_active", "display_order")
    list_filter = ("is_active", "parent")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("display_order", "is_active")
    ordering = ("display_order", "name")


# ---------------------------------------------------------------------------
# Task 23 — Tag Admin
# ---------------------------------------------------------------------------

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


# ---------------------------------------------------------------------------
# Task 22 — Product Admin with inline images and variants
# ---------------------------------------------------------------------------

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "is_primary", "display_order")
    readonly_fields = ("public_id",)


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ("name", "sku", "price_override", "stock_quantity", "is_active")
    readonly_fields = ("public_id",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "vendor",
        "category",
        "base_price",
        "stock_quantity",
        "status",
        "is_featured",
        "created_at",
    )
    list_filter = ("status", "is_featured", "category", "vendor")
    search_fields = ("name", "slug", "sku", "vendor__business_name")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("status", "is_featured")
    readonly_fields = ("public_id", "created_at", "updated_at")
    filter_horizontal = ("tags",)

    fieldsets = (
        (None, {"fields": ("vendor", "public_id", "name", "slug", "status", "is_featured")}),
        (
            "Details",
            {
                "fields": (
                    "category",
                    "tags",
                    "short_description",
                    "description",
                )
            },
        ),
        (
            "Pricing & Inventory",
            {
                "fields": (
                    "base_price",
                    "compare_at_price",
                    "stock_quantity",
                    "sku",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    inlines = [ProductImageInline, ProductVariantInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "is_primary", "display_order", "image_preview")
    list_filter = ("is_primary",)
    search_fields = ("product__name",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; border-radius:4px;" />',
                obj.image.url,
            )
        return "—"

    image_preview.short_description = "Preview"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "effective_price", "stock_quantity", "is_active")
    list_filter = ("is_active",)
    search_fields = ("product__name", "name", "sku")

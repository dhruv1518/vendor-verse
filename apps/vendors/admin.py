from django.contrib import admin, messages

from .models import VendorApplication, Vendor, Storefront
from .services import approve_vendor_application, reject_vendor_application


@admin.register(VendorApplication)
class VendorApplicationAdmin(admin.ModelAdmin):
    list_display = ("business_name", "user", "status", "created_at", "reviewed_at")
    list_filter = ("status", "created_at")
    search_fields = ("business_name", "user__email", "business_email")
    readonly_fields = ("user", "created_at", "updated_at", "reviewed_at", "public_id")
    ordering = ("-created_at",)

    fieldsets = (
        ("Applicant", {"fields": ("user", "public_id")}),
        (
            "Business Details",
            {
                "fields": (
                    "business_name",
                    "business_description",
                    "business_email",
                    "phone_number",
                )
            },
        ),
        (
            "Review",
            {"fields": ("status", "admin_notes", "reviewed_at")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = ["approve_selected", "reject_selected"]

    @admin.action(description="✅ Approve selected applications")
    def approve_selected(self, request, queryset):
        approved = 0
        for application in queryset.filter(status=VendorApplication.Status.PENDING):
            approve_vendor_application(application)
            approved += 1
        self.message_user(
            request,
            f"Successfully approved {approved} application(s).",
            messages.SUCCESS,
        )

    @admin.action(description="❌ Reject selected applications")
    def reject_selected(self, request, queryset):
        rejected = 0
        for application in queryset.filter(status=VendorApplication.Status.PENDING):
            reject_vendor_application(application, admin_notes="Rejected via bulk action.")
            rejected += 1
        self.message_user(
            request,
            f"Rejected {rejected} application(s).",
            messages.WARNING,
        )


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("business_name", "user", "business_email", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("business_name", "user__email", "business_email")
    readonly_fields = ("public_id", "created_at", "updated_at")


@admin.register(Storefront)
class StorefrontAdmin(admin.ModelAdmin):
    list_display = ("vendor", "slug", "tagline", "updated_at")
    search_fields = ("vendor__business_name", "slug")
    prepopulated_fields = {"slug": ("tagline",)}
    readonly_fields = ("public_id", "created_at", "updated_at")

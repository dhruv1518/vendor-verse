from django.db import models
from django.conf import settings
from django.utils.text import slugify

from apps.core.models import TimeStampedModel, PublicIDModel


class VendorApplication(TimeStampedModel, PublicIDModel):
    """
    Tracks a user's application to become a vendor.
    Created when a customer submits the 'Become a Vendor' form.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending Review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendor_applications",
    )
    business_name = models.CharField(max_length=200)
    business_description = models.TextField(
        help_text="Describe your business, products, and why you want to sell on VendorVerse."
    )
    business_email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes (e.g., reason for rejection).",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Vendor Application"
        verbose_name_plural = "Vendor Applications"

    def __str__(self):
        return f"{self.business_name} — {self.get_status_display()}"


class Vendor(TimeStampedModel, PublicIDModel):
    """
    Represents an approved vendor who can sell products.
    Created automatically when a VendorApplication is approved.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendor",
    )
    business_name = models.CharField(max_length=200)
    business_email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.business_name


class Storefront(TimeStampedModel, PublicIDModel):
    """
    A vendor's public-facing shop page.
    Created automatically when a vendor is approved.
    """

    vendor = models.OneToOneField(
        Vendor,
        on_delete=models.CASCADE,
        related_name="storefront",
    )
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    tagline = models.CharField(
        max_length=255,
        blank=True,
        help_text="A short tagline for your store (e.g., 'Handmade with love').",
    )
    description = models.TextField(
        blank=True,
        help_text="Tell customers about your store.",
    )
    logo = models.ImageField(upload_to="storefronts/logos/", null=True, blank=True)
    banner = models.ImageField(upload_to="storefronts/banners/", null=True, blank=True)
    return_policy = models.TextField(blank=True)
    shipping_policy = models.TextField(blank=True)

    class Meta:
        ordering = ["vendor__business_name"]

    def __str__(self):
        return f"{self.vendor.business_name} Storefront"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.vendor.business_name)
            slug = base_slug
            counter = 1
            while Storefront.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

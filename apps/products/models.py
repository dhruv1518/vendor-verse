from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator

from apps.core.models import TimeStampedModel, PublicIDModel


# ---------------------------------------------------------------------------
# Task 21 — Category Model (hierarchical categories)
# ---------------------------------------------------------------------------

class Category(TimeStampedModel, PublicIDModel):
    """
    Product category with support for a single level of nesting.
    A parent=None category is a top-level category; otherwise it is a sub-category.
    """

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, db_index=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", null=True, blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Task 23 — Tag Model
# ---------------------------------------------------------------------------

class Tag(TimeStampedModel):
    """Simple tag for organizing and filtering products."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Task 22 — Product Model
# ---------------------------------------------------------------------------

class Product(TimeStampedModel, PublicIDModel):
    """
    Represents a product listed by a vendor.
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        ARCHIVED = "ARCHIVED", "Archived"

    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.CASCADE,
        related_name="products",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="products")

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, db_index=True)
    description = models.TextField(
        blank=True,
        help_text="Full product description (supports plain text).",
    )
    short_description = models.CharField(
        max_length=300,
        blank=True,
        help_text="Brief summary shown on product cards.",
    )

    # Pricing
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Base price in INR.",
    )
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Original price before discount (shown as strikethrough).",
    )

    # Inventory
    stock_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Total available stock for the base product.",
    )
    sku = models.CharField(
        max_length=100,
        blank=True,
        help_text="Stock Keeping Unit identifier.",
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("vendor", "slug")]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while (
                Product.objects.filter(vendor=self.vendor, slug=slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def primary_image(self):
        """Return the primary image or the first available image."""
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def is_on_sale(self):
        return self.compare_at_price and self.compare_at_price > self.base_price

    @property
    def discount_percentage(self):
        if self.is_on_sale:
            return int(
                ((self.compare_at_price - self.base_price) / self.compare_at_price)
                * 100
            )
        return 0

    @property
    def in_stock(self):
        return self.stock_quantity > 0


# ---------------------------------------------------------------------------
# Task 22 — ProductImage Model
# ---------------------------------------------------------------------------

class ProductImage(TimeStampedModel, PublicIDModel):
    """An image attached to a product. One image can be marked as primary."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/images/")
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(
        default=False,
        help_text="Mark as the main display image.",
    )
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-is_primary", "display_order"]

    def __str__(self):
        return f"Image for {self.product.name}"


# ---------------------------------------------------------------------------
# Task 23 — ProductVariant Model
# ---------------------------------------------------------------------------

class ProductVariant(TimeStampedModel, PublicIDModel):
    """
    Represents a specific variant of a product (e.g., Size: Large, Color: Red).
    Each variant can have its own price and stock.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )
    name = models.CharField(
        max_length=150,
        help_text="Variant label, e.g., 'Large / Red', 'Size M', '500ml'.",
    )
    sku = models.CharField(max_length=100, blank=True)
    price_override = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Leave blank to use the product's base price.",
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.product.name} — {self.name}"

    @property
    def effective_price(self):
        """Return the variant price or fall back to the product base price."""
        if self.price_override is not None:
            return self.price_override
        return self.product.base_price


# ---------------------------------------------------------------------------
# AF-B: Wishlist Models
# ---------------------------------------------------------------------------

class Wishlist(TimeStampedModel):
    """A user's saved items."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist"
    )

    def __str__(self):
        return f"{self.user.email}'s Wishlist"

class WishlistItem(TimeStampedModel):
    """An individual item saved in a wishlist."""
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlisted_by"
    )

    class Meta:
        unique_together = ("wishlist", "product")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} in {self.wishlist.user.email}'s wishlist"


# ---------------------------------------------------------------------------
# AF-I: Customer Q&A
# ---------------------------------------------------------------------------

class Question(TimeStampedModel, PublicIDModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="questions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Q by {self.user.email} on {self.product.name}"


class Answer(TimeStampedModel, PublicIDModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="answers")
    text = models.TextField()
    is_vendor = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"A by {self.user.email} on {self.question.product.name}"

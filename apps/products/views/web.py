from django.db.models import Q
from django.views.generic import ListView, DetailView

from apps.products.models import Product, Category


# ---------------------------------------------------------------------------
# Task 26 — Public Product Listing Page
# ---------------------------------------------------------------------------

class ProductListView(ListView):
    """Public catalog page listing all active products with search and filters."""

    template_name = "products/list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Product.objects.filter(status=Product.Status.ACTIVE)
            .select_related("vendor", "category")
            .prefetch_related("images")
            .order_by("-created_at")
        )

        # Search by name
        search = self.request.GET.get("q", "").strip()
        if search:
            qs = qs.filter(name__icontains=search)

        # Category filter — also include products in child categories
        category_slug = self.request.GET.get("category", "").strip()
        if category_slug:
            qs = qs.filter(
                Q(category__slug=category_slug) | Q(category__parent__slug=category_slug)
            )

        # Price sort
        sort = self.request.GET.get("sort", "").strip()
        if sort == "price_low":
            qs = qs.order_by("base_price")
        elif sort == "price_high":
            qs = qs.order_by("-base_price")
        elif sort == "newest":
            qs = qs.order_by("-created_at")

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(
            is_active=True, parent__isnull=True
        ).prefetch_related("children")
        context["search_query"] = self.request.GET.get("q", "")
        context["current_category"] = self.request.GET.get("category", "")
        context["current_sort"] = self.request.GET.get("sort", "")
        context["total_count"] = self.get_queryset().count()
        return context


# ---------------------------------------------------------------------------
# Task 27 — Public Product Detail Page
# ---------------------------------------------------------------------------

class ProductDetailView(DetailView):
    """Detailed display page of a single product."""

    template_name = "products/detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "product_slug"

    def get_queryset(self):
        return (
            Product.objects.filter(status=Product.Status.ACTIVE)
            .select_related("vendor", "vendor__storefront", "category")
            .prefetch_related("images", "variants", "tags")
        )

    def get_object(self, queryset=None):
        """Look up by vendor slug + product slug combo."""
        if queryset is None:
            queryset = self.get_queryset()

        vendor_slug = self.kwargs.get("vendor_slug")
        product_slug = self.kwargs.get("product_slug")

        return queryset.get(
            vendor__storefront__slug=vendor_slug,
            slug=product_slug,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        # Get all images
        context["images"] = product.images.all()
        context["primary_image"] = product.primary_image

        # Get active variants
        context["variants"] = product.variants.filter(is_active=True)

        # Related products from same vendor or category
        related_qs = (
            Product.objects.filter(status=Product.Status.ACTIVE)
            .exclude(pk=product.pk)
            .select_related("vendor", "category")
            .prefetch_related("images")
        )

        # Try same category first, then same vendor
        if product.category:
            related = related_qs.filter(category=product.category)[:4]
        else:
            related = related_qs.filter(vendor=product.vendor)[:4]

        if related.count() < 4:
            more = related_qs.exclude(pk__in=related.values_list("pk", flat=True))[:4 - related.count()]
            related = list(related) + list(more)

        context["related_products"] = related
        return context

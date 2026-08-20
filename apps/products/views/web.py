from django.db.models import Q, Exists, OuterRef
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views import View

from apps.products.models import Product, Category, Wishlist, WishlistItem


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

        if self.request.user.is_authenticated:
            qs = qs.annotate(
                in_wishlist=Exists(
                    WishlistItem.objects.filter(
                        wishlist__user=self.request.user,
                        product_id=OuterRef('pk')
                    )
                )
            )

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
        qs = (
            Product.objects.filter(status=Product.Status.ACTIVE)
            .select_related("vendor", "vendor__storefront", "category")
            .prefetch_related("images", "variants", "tags")
        )
        if self.request.user.is_authenticated:
            qs = qs.annotate(
                in_wishlist=Exists(
                    WishlistItem.objects.filter(
                        wishlist__user=self.request.user,
                        product_id=OuterRef('pk')
                    )
                )
            )
        return qs

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

        # ----- Reviews (Task 37) -----
        from django.db.models import Avg
        from apps.reviews.models import Review
        from apps.reviews.forms import ReviewForm

        reviews = Review.objects.filter(product=product).select_related("user")
        context["reviews"] = reviews
        context["review_count"] = reviews.count()

        avg = reviews.aggregate(avg=Avg("rating"))["avg"]
        context["avg_rating"] = avg

        # Check if the current user already has a review
        if self.request.user.is_authenticated:
            context["user_review"] = reviews.filter(user=self.request.user).first()
        else:
            context["user_review"] = None

        context["review_form"] = ReviewForm()

        return context


# ---------------------------------------------------------------------------
# AF-A: Live Search with Autocomplete (HTMX)
# ---------------------------------------------------------------------------

class ProductAutocompleteView(ListView):
    """HTMX view to return autocomplete suggestions for the search bar."""

    template_name = "products/partials/autocomplete.html"
    context_object_name = "products"

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        if len(query) < 2:
            return Product.objects.none()

        return (
            Product.objects.filter(
                status=Product.Status.ACTIVE,
                name__icontains=query,
            )
            .select_related("vendor__storefront")
            .prefetch_related("images")
            .order_by("-is_featured", "-created_at")[:5]
        )


# ---------------------------------------------------------------------------
# AF-B: Wishlist Views
# ---------------------------------------------------------------------------

class WishlistToggleView(LoginRequiredMixin, View):
    """HTMX view to toggle a product in/out of the user's wishlist."""

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, public_id=self.kwargs.get("public_id"))
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        
        item = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()
        
        if item:
            item.delete()
            in_wishlist = False
        else:
            WishlistItem.objects.create(wishlist=wishlist, product=product)
            in_wishlist = True
            
        return render(request, "products/partials/wishlist_btn.html", {
            "product": product,
            "in_wishlist": in_wishlist
        })


class WishlistListView(LoginRequiredMixin, ListView):
    """Page displaying all products in the user's wishlist."""

    template_name = "wishlist/detail.html"
    context_object_name = "items"
    paginate_by = 12

    def get_queryset(self):
        wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
        return WishlistItem.objects.filter(wishlist=wishlist).select_related(
            "product", "product__vendor__storefront"
        ).prefetch_related("product__images")


from django.db.models import Q, Exists, OuterRef
from django.views.generic import ListView, DetailView, TemplateView
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

    def get_template_names(self):
        if self.request.htmx:
            return ["products/partials/product_grid.html"]
        return ["products/list.html"]

    def get_queryset(self):
        qs = (
            Product.objects.filter(status=Product.Status.ACTIVE)
            .select_related("vendor", "category")
            .prefetch_related("images")
        )
        
        from apps.products.filters import ProductFilter
        self.filterset = ProductFilter(self.request.GET, queryset=qs)
        qs = self.filterset.qs

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
        context["filterset"] = getattr(self, "filterset", None)
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

        # AF-H: Track recently viewed products
        recently_viewed = self.request.session.get("recently_viewed", [])
        product_id = str(product.public_id)
        if product_id in recently_viewed:
            recently_viewed.remove(product_id)
        recently_viewed.insert(0, product_id)
        # Keep only the last 10
        self.request.session["recently_viewed"] = recently_viewed[:10]
        self.request.session.modified = True

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

        # ----- AF-I: Customer Q&A -----
        from apps.products.forms import QuestionForm, AnswerForm
        from apps.products.models import Question
        
        context["questions"] = Question.objects.filter(product=product).prefetch_related("answers", "answers__user", "user")
        context["question_form"] = QuestionForm()
        context["answer_form"] = AnswerForm()

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


# ---------------------------------------------------------------------------
# AF-F: Product Comparison Tool
# ---------------------------------------------------------------------------

class CompareToggleView(View):
    """HTMX view to toggle a product in/out of the comparison list (session)."""
    
    def post(self, request, *args, **kwargs):
        product_id = str(self.kwargs.get("public_id"))
        compare_list = request.session.get("compare_list", [])
        
        in_compare = False
        if product_id in compare_list:
            compare_list.remove(product_id)
        else:
            if len(compare_list) < 4:
                compare_list.append(product_id)
                in_compare = True
            else:
                # Can't add more than 4, but we need to know the state
                pass
                
        request.session["compare_list"] = compare_list
        request.session.modified = True
        
        product = get_object_or_404(Product, public_id=product_id)
        return render(request, "products/partials/compare_btn.html", {
            "product": product,
            "in_compare": in_compare,
            "compare_full": len(compare_list) >= 4 and not in_compare
        })


class CompareListView(TemplateView):
    """View to show products side-by-side."""
    template_name = "products/compare.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compare_list = self.request.session.get("compare_list", [])
        products = Product.objects.filter(public_id__in=compare_list).select_related("vendor__storefront").prefetch_related("images")
        
        product_dict = {str(p.public_id): p for p in products}
        context["products"] = [product_dict[pid] for pid in compare_list if pid in product_dict]
        return context


# ---------------------------------------------------------------------------
# AF-I: Customer Q&A
# ---------------------------------------------------------------------------

from django.contrib import messages
from django.shortcuts import redirect
from apps.products.forms import QuestionForm, AnswerForm
from apps.products.models import Question, Answer

class QuestionCreateView(LoginRequiredMixin, View):
    def post(self, request, public_id):
        product = get_object_or_404(Product, public_id=public_id)
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.product = product
            question.user = request.user
            question.save()
            messages.success(request, "Your question has been posted!")
        else:
            messages.error(request, "There was an error posting your question.")
        return redirect(product.get_absolute_url())

class AnswerCreateView(LoginRequiredMixin, View):
    def post(self, request, public_id):
        question = get_object_or_404(Question, public_id=public_id)
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.user = request.user
            # Check if user is the vendor of this product
            if hasattr(request.user, 'vendor') and request.user.vendor == question.product.vendor:
                answer.is_vendor = True
            answer.save()
            messages.success(request, "Your answer has been posted!")
        else:
            messages.error(request, "There was an error posting your answer.")
        return redirect(question.product.get_absolute_url())


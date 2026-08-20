from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.shortcuts import redirect, get_object_or_404
from django.views import View

from apps.products.models import Product
from .forms import ReviewForm
from .models import Review


# ---------------------------------------------------------------------------
# Task 37 — Submit Review View
# ---------------------------------------------------------------------------

class SubmitReviewView(LoginRequiredMixin, View):
    """Handle review form submission from the product detail page."""

    def post(self, request, public_id):
        product = get_object_or_404(Product, public_id=public_id)

        # Check if user already reviewed this product
        if Review.objects.filter(product=product, user=request.user).exists():
            messages.warning(request, "You have already reviewed this product.")
            return redirect(
                "products:product_detail",
                vendor_slug=product.vendor.storefront.slug,
                product_slug=product.slug,
            )

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()

            messages.success(request, "Thank you! Your review has been submitted.")
        else:
            # Collect form errors into message
            error_msg = " ".join(
                error for errors in form.errors.values() for error in errors
            )
            messages.error(request, f"Could not submit review: {error_msg}")

        return redirect(
            "products:product_detail",
            vendor_slug=product.vendor.storefront.slug,
            product_slug=product.slug,
        )


class DeleteReviewView(LoginRequiredMixin, View):
    """Allow a user to delete their own review."""

    def post(self, request, public_id):
        review = get_object_or_404(Review, public_id=public_id, user=request.user)
        product = review.product
        review.delete()
        messages.success(request, "Your review has been deleted.")
        return redirect(
            "products:product_detail",
            vendor_slug=product.vendor.storefront.slug,
            product_slug=product.slug,
        )

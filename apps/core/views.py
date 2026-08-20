from django.shortcuts import render


# ---------------------------------------------------------------------------
# Task 41 — Custom Error Pages
# ---------------------------------------------------------------------------

def custom_404(request, exception):
    """Custom 404 error page."""
    return render(request, "404.html", status=404)


def custom_500(request):
    """Custom 500 error page."""
    return render(request, "500.html", status=500)


# ---------------------------------------------------------------------------
# Home Page
# ---------------------------------------------------------------------------

from django.views.generic import TemplateView
from apps.vendors.models import Vendor
from apps.products.models import Product
from apps.orders.models import Order
from apps.reviews.models import Review
from django.db.models import Avg


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dynamic stats
        context["vendor_count"] = Vendor.objects.filter(is_active=True).count()
        context["product_count"] = Product.objects.filter(status=Product.Status.ACTIVE).count()
        context["customer_count"] = Order.objects.values("user").distinct().count()
        
        avg_rating = Review.objects.aggregate(avg=Avg("rating"))["avg"]
        context["avg_rating"] = f"{avg_rating:.1f}" if avg_rating else "5.0"
        
        return context

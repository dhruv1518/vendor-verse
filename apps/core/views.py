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
        
        # Featured stores / vendors
        context["featured_vendors"] = (
            Vendor.objects.filter(is_active=True)
            .select_related("storefront")
            .prefetch_related("products")
            .order_by("-created_at")[:6]
        )

        # Latest products for product showcase
        context["latest_products"] = (
            Product.objects.filter(status=Product.Status.ACTIVE)
            .select_related("vendor", "vendor__storefront", "category")
            .prefetch_related("images")
            .order_by("-created_at")[:8]
        )
        
        return context


# ---------------------------------------------------------------------------
# Footer Pages: Vendor Resources
# ---------------------------------------------------------------------------

class SellingGuidesView(TemplateView):
    template_name = "pages/selling_guides.html"


class VendorPoliciesView(TemplateView):
    template_name = "pages/vendor_policies.html"


# ---------------------------------------------------------------------------
# Footer Pages: Company
# ---------------------------------------------------------------------------

class AboutView(TemplateView):
    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vendor_count"] = Vendor.objects.filter(is_active=True).count()
        context["product_count"] = Product.objects.filter(status=Product.Status.ACTIVE).count()
        context["customer_count"] = Order.objects.values("user").distinct().count()
        return context


class BlogView(TemplateView):
    template_name = "pages/blog.html"


class CareersView(TemplateView):
    template_name = "pages/careers.html"


class PressView(TemplateView):
    template_name = "pages/press.html"


# ---------------------------------------------------------------------------
# Footer Pages: Support & Legal
# ---------------------------------------------------------------------------

class HelpCenterView(TemplateView):
    template_name = "pages/help.html"


from django.views import View
from django.shortcuts import redirect
from django.contrib import messages

class ContactView(View):
    template_name = "pages/contact.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not email or not message:
            messages.error(request, "Please fill in all required fields (Name, Email, Message).")
            return render(request, self.template_name, {
                "name": name,
                "email": email,
                "subject": subject,
                "message": message,
            })

        messages.success(
            request,
            f"Thank you, {name}! Your message has been received. Our support team will get back to you at {email} within 24 hours."
        )
        return redirect("core:contact")


class PrivacyPolicyView(TemplateView):
    template_name = "pages/privacy.html"


class TermsOfServiceView(TemplateView):
    template_name = "pages/terms.html"


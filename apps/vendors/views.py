from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.views import View

from apps.core.mixins import VendorRequiredMixin
from .models import VendorApplication, Vendor, Storefront
from .forms import VendorApplicationForm, StorefrontSettingsForm


# ---------------------------------------------------------------------------
# Vendor Application (Task 15)
# ---------------------------------------------------------------------------

class VendorApplyView(LoginRequiredMixin, TemplateView):
    """Page where customers can apply to become a vendor."""

    template_name = "vendors/apply.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # If user is already a vendor, redirect to dashboard
        if getattr(request.user, "role", "") == "VENDOR":
            messages.info(request, "You are already a vendor!")
            return redirect("vendors:dashboard")

        # If user has a pending application, redirect to success page
        if VendorApplication.objects.filter(
            user=request.user, status=VendorApplication.Status.PENDING
        ).exists():
            messages.info(request, "You already have a pending application.")
            return redirect("vendors:apply_success")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = kwargs.get("form", VendorApplicationForm())

        # Check if user has a rejected application (allow re-apply)
        rejected = VendorApplication.objects.filter(
            user=self.request.user, status=VendorApplication.Status.REJECTED
        ).first()
        context["rejected_application"] = rejected
        return context

    def post(self, request, *args, **kwargs):
        form = VendorApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(request, "Your vendor application has been submitted!")
            return redirect("vendors:apply_success")

        messages.error(request, "Please correct the errors below.")
        return self.render_to_response(self.get_context_data(form=form))


class VendorApplySuccessView(LoginRequiredMixin, TemplateView):
    """Confirmation page after submitting a vendor application."""

    template_name = "vendors/apply_success.html"


# ---------------------------------------------------------------------------
# Vendor Dashboard (Task 17)
# ---------------------------------------------------------------------------

class VendorDashboardView(VendorRequiredMixin, TemplateView):
    """Dashboard home page for vendors showing overview stats."""

    template_name = "vendors/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.request.user.vendor
        storefront = getattr(vendor, "storefront", None)
        context["vendor"] = vendor
        context["storefront"] = storefront
        context["active_page"] = "dashboard"
        # Static stats for now — will be dynamic in later phases
        context["stats"] = {
            "total_products": 0,
            "total_orders": 0,
            "revenue": "0.00",
            "pending_orders": 0,
        }
        return context


# ---------------------------------------------------------------------------
# Storefront Settings (Task 18)
# ---------------------------------------------------------------------------

class StorefrontSettingsView(VendorRequiredMixin, TemplateView):
    """Page for vendors to configure their storefront."""

    template_name = "vendors/storefront_settings.html"

    def get_storefront(self):
        vendor = self.request.user.vendor
        storefront, _ = Storefront.objects.get_or_create(vendor=vendor)
        return storefront

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        storefront = self.get_storefront()
        context["form"] = kwargs.get("form", StorefrontSettingsForm(instance=storefront))
        context["storefront"] = storefront
        context["vendor"] = self.request.user.vendor
        context["active_page"] = "storefront_settings"
        return context

    def post(self, request, *args, **kwargs):
        storefront = self.get_storefront()
        form = StorefrontSettingsForm(request.POST, request.FILES, instance=storefront)
        if form.is_valid():
            form.save()
            messages.success(request, "Storefront settings updated successfully!")
            return redirect("vendors:storefront_settings")

        messages.error(request, "Please correct the errors below.")
        return self.render_to_response(self.get_context_data(form=form))


# ---------------------------------------------------------------------------
# Public Vendor Directory (Task 19)
# ---------------------------------------------------------------------------

class VendorDirectoryView(ListView):
    """Public directory listing all active vendor storefronts."""

    template_name = "vendors/directory.html"
    context_object_name = "storefronts"
    paginate_by = 12

    def get_queryset(self):
        return (
            Storefront.objects.filter(vendor__is_active=True)
            .select_related("vendor")
            .order_by("vendor__business_name")
        )


# ---------------------------------------------------------------------------
# Public Storefront Page (Task 20)
# ---------------------------------------------------------------------------

class StorefrontDetailView(DetailView):
    """Public page showing a specific vendor's storefront."""

    template_name = "vendors/storefront.html"
    context_object_name = "storefront"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Storefront.objects.filter(vendor__is_active=True).select_related("vendor")

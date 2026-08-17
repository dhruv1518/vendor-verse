from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.orders.models import Order


# ---------------------------------------------------------------------------
# Task 34 — Customer Order History & Detail Pages
# ---------------------------------------------------------------------------

class CustomerOrderListView(LoginRequiredMixin, TemplateView):
    """List all orders placed by the logged-in customer."""

    template_name = "account/orders.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["orders"] = (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items", "items__vendor")
            .order_by("-created_at")
        )
        return context


class CustomerOrderDetailView(LoginRequiredMixin, TemplateView):
    """Detailed view of a single customer order."""

    template_name = "account/order_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        public_id = self.kwargs.get("public_id")
        order = get_object_or_404(
            Order, public_id=public_id, user=self.request.user
        )
        context["order"] = order
        context["order_items"] = order.items.select_related(
            "vendor", "product", "product__vendor__storefront"
        ).prefetch_related("product__images")
        return context

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from django.views import View

from apps.core.mixins import VendorRequiredMixin
from apps.orders.models import Order, OrderItem


# ---------------------------------------------------------------------------
# Task 35 — Vendor Order List & Detail Pages
# ---------------------------------------------------------------------------

class VendorOrderListView(VendorRequiredMixin, TemplateView):
    """List orders that contain items from this vendor."""

    template_name = "vendors/orders/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.request.user.vendor
        context["vendor"] = vendor
        context["storefront"] = getattr(vendor, "storefront", None)
        context["active_page"] = "orders"

        # Get unique orders that have items from this vendor
        vendor_item_qs = OrderItem.objects.filter(vendor=vendor).select_related("order")
        order_ids = vendor_item_qs.values_list("order_id", flat=True).distinct()
        orders = (
            Order.objects.filter(id__in=order_ids)
            .prefetch_related("items")
            .order_by("-created_at")
        )

        # Filter by status if requested
        status_filter = self.request.GET.get("status", "")
        if status_filter:
            orders = orders.filter(
                items__vendor=vendor, items__status=status_filter
            ).distinct()

        context["orders"] = orders
        context["current_status"] = status_filter
        return context


class VendorOrderDetailView(VendorRequiredMixin, TemplateView):
    """Detail view of a single order from the vendor's perspective."""

    template_name = "vendors/orders/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.request.user.vendor
        context["vendor"] = vendor
        context["storefront"] = getattr(vendor, "storefront", None)
        context["active_page"] = "orders"

        public_id = self.kwargs.get("public_id")
        order = get_object_or_404(Order, public_id=public_id)

        # Only show items belonging to this vendor
        vendor_items = order.items.filter(vendor=vendor).select_related(
            "product", "variant"
        )

        if not vendor_items.exists():
            messages.error(self.request, "No items from your store in this order.")
            return redirect("orders:vendor_order_list")

        context["order"] = order
        context["order_items"] = vendor_items

        # Calculate vendor-specific subtotal
        context["vendor_subtotal"] = sum(
            item.line_total for item in vendor_items
        )
        return context


class VendorOrderItemStatusView(VendorRequiredMixin, View):
    """Update the status of a single order item (vendor perspective)."""

    def post(self, request, public_id):
        vendor = request.user.vendor
        item = get_object_or_404(
            OrderItem, public_id=public_id, vendor=vendor
        )

        new_status = request.POST.get("status")
        valid_statuses = [s[0] for s in OrderItem.ItemStatus.choices]

        if new_status not in valid_statuses:
            messages.error(request, "Invalid status.")
            return redirect("orders:vendor_order_detail", public_id=item.order.public_id)

        item.status = new_status
        item.save()
        
        # AF-G: Create in-app notification for the customer
        from apps.notifications.models import Notification
        from django.urls import reverse
        
        Notification.objects.create(
            user=item.order.user,
            title=f"Order Update: {item.product_name}",
            message=f"The status of your item has been updated to {item.get_status_display()}.",
            link=reverse("orders:customer_order_detail", kwargs={"public_id": item.order.public_id})
        )
        
        messages.success(
            request,
            f'Item "{item.product_name}" status updated to {item.get_status_display()}.',
        )
        return redirect("orders:vendor_order_detail", public_id=item.order.public_id)

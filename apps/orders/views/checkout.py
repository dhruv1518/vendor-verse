from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from django.views import View

from apps.cart.models import Cart
from apps.accounts.models import Address
from apps.orders.models import Order
from apps.orders.services import create_order_from_cart, process_mock_payment


# ---------------------------------------------------------------------------
# Task 30 — Checkout Page
# ---------------------------------------------------------------------------

class CheckoutView(LoginRequiredMixin, TemplateView):
    """
    Checkout page showing cart summary and address selection.
    """

    template_name = "checkout/checkout.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        cart = Cart.objects.filter(user=request.user).first()
        if not cart or cart.is_empty:
            messages.warning(request, "Your cart is empty.")
            return redirect("cart:detail")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart.objects.get(user=self.request.user)
        context["cart"] = cart
        context["cart_items"] = cart.cart_items.select_related(
            "product", "product__vendor", "variant"
        ).prefetch_related("product__images")
        context["addresses"] = Address.objects.filter(
            user=self.request.user
        ).order_by("-is_default", "-created_at")
        context["selected_address_id"] = self.request.GET.get("address", "")
        return context


class CheckoutProcessView(LoginRequiredMixin, View):
    """
    Process the checkout: validate address, create order, redirect to payment.
    """

    def post(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or cart.is_empty:
            messages.warning(request, "Your cart is empty.")
            return redirect("cart:detail")

        address_id = request.POST.get("address_id")
        if not address_id:
            messages.error(request, "Please select a shipping address.")
            return redirect("orders:checkout")

        address = get_object_or_404(
            Address, public_id=address_id, user=request.user
        )

        # Create the order
        order = create_order_from_cart(request.user, cart, address)

        # Store order ID in session for payment page
        request.session["pending_order_id"] = str(order.public_id)

        return redirect("payments:payment", public_id=order.public_id)


# ---------------------------------------------------------------------------
# Task 33 — Order Confirmation / Success Page
# ---------------------------------------------------------------------------

class OrderSuccessView(LoginRequiredMixin, TemplateView):
    """Order success / confirmation page after payment."""

    template_name = "checkout/success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        public_id = self.kwargs.get("public_id")
        order = get_object_or_404(Order, public_id=public_id, user=self.request.user)
        context["order"] = order
        context["order_items"] = order.items.select_related("vendor", "product")
        return context

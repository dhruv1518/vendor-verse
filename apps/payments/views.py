import time

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from django.views import View

from apps.orders.models import Order
from apps.orders.services import process_mock_payment
from apps.cart.models import Cart


# ---------------------------------------------------------------------------
# Task 31 — Mock Payment Page
# ---------------------------------------------------------------------------

class MockPaymentView(LoginRequiredMixin, TemplateView):
    """
    Display the mock payment form with card inputs.
    """

    template_name = "checkout/payment.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        public_id = kwargs.get("public_id")
        order = get_object_or_404(Order, public_id=public_id, user=request.user)

        # Don't allow re-payment on already paid orders
        if order.payment_status == "PAID":
            messages.info(request, "This order has already been paid.")
            return redirect("orders:order_success", public_id=order.public_id)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        public_id = self.kwargs.get("public_id")
        order = get_object_or_404(Order, public_id=public_id, user=self.request.user)
        context["order"] = order
        context["order_items"] = order.items.select_related("vendor", "product")
        return context


class ProcessPaymentView(LoginRequiredMixin, View):
    """
    Process the mock payment: validate card inputs, simulate delay, mark paid.
    """

    def post(self, request, public_id):
        order = get_object_or_404(Order, public_id=public_id, user=request.user)

        if order.payment_status == "PAID":
            messages.info(request, "This order has already been paid.")
            return redirect("orders:order_success", public_id=order.public_id)

        # Get mock card details from form
        card_number = request.POST.get("card_number", "").replace(" ", "")
        card_expiry = request.POST.get("card_expiry", "")
        card_cvv = request.POST.get("card_cvv", "")
        card_name = request.POST.get("card_name", "")

        # Basic validation
        errors = []
        if len(card_number) < 13 or len(card_number) > 19:
            errors.append("Card number must be 13-19 digits.")
        if not card_expiry or len(card_expiry) < 4:
            errors.append("Please enter a valid expiry date (MM/YY).")
        if not card_cvv or len(card_cvv) < 3:
            errors.append("Please enter a valid CVV.")
        if not card_name:
            errors.append("Please enter the cardholder name.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect("payments:payment", public_id=order.public_id)

        # Determine card brand from first digits
        card_brand = "Visa"
        if card_number.startswith("5"):
            card_brand = "Mastercard"
        elif card_number.startswith("3"):
            card_brand = "Amex"
        elif card_number.startswith("6"):
            card_brand = "Discover"

        # Simulate processing delay (1 second)
        time.sleep(1)

        # Process the mock payment
        success, transaction_id = process_mock_payment(
            order=order,
            card_last_four=card_number[-4:],
            card_brand=card_brand,
        )

        if success:
            # Clear the cart after successful payment
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                cart.clear()

            # Clean up session
            if "pending_order_id" in request.session:
                del request.session["pending_order_id"]

            messages.success(request, "Payment successful! Your order has been placed.")
            return redirect("orders:order_success", public_id=order.public_id)
        else:
            messages.error(request, "Payment failed. Please try again.")
            return redirect("payments:payment", public_id=order.public_id)

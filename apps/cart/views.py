from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from django.views import View

from .models import Cart, CartItem
from apps.products.models import Product, ProductVariant
from apps.orders.models import Coupon


# ---------------------------------------------------------------------------
# Task 28 — Add to Cart / Remove / Update Quantity
# ---------------------------------------------------------------------------

class AddToCartView(LoginRequiredMixin, View):
    """Add a product (with optional variant) to the cart."""

    def post(self, request):
        product_id = request.POST.get("product_id")
        variant_id = request.POST.get("variant_id") or None
        quantity = int(request.POST.get("quantity", 1))

        product = get_object_or_404(
            Product, public_id=product_id, status=Product.Status.ACTIVE
        )

        variant = None
        if variant_id:
            variant = get_object_or_404(
                ProductVariant, public_id=variant_id, product=product, is_active=True
            )

        # Check stock
        available_stock = variant.stock_quantity if variant else product.stock_quantity
        if quantity > available_stock:
            messages.error(request, f"Only {available_stock} units available.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        # Get or create cart
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # Check if item already exists
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={"quantity": quantity},
        )

        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > available_stock:
                cart_item.quantity = available_stock
                messages.warning(
                    request,
                    f"Quantity capped to {available_stock} (max available stock).",
                )
            cart_item.save()
        
        messages.success(request, f'"{product.name}" added to cart!')
        return redirect("cart:detail")


class UpdateCartItemView(LoginRequiredMixin, View):
    """Update the quantity of a cart item."""

    def post(self, request, public_id):
        cart_item = get_object_or_404(
            CartItem, public_id=public_id, cart__user=request.user
        )
        quantity = int(request.POST.get("quantity", 1))

        if quantity < 1:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
        else:
            available = (
                cart_item.variant.stock_quantity
                if cart_item.variant
                else cart_item.product.stock_quantity
            )
            if quantity > available:
                quantity = available
                messages.warning(request, f"Quantity capped to {available}.")
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated.")

        return redirect("cart:detail")


class RemoveCartItemView(LoginRequiredMixin, View):
    """Remove a single item from the cart."""

    def post(self, request, public_id):
        cart_item = get_object_or_404(
            CartItem, public_id=public_id, cart__user=request.user
        )
        name = cart_item.product.name
        cart_item.delete()
        messages.success(request, f'"{name}" removed from cart.')
        return redirect("cart:detail")


# ---------------------------------------------------------------------------
# Task 29 — Cart Page View
# ---------------------------------------------------------------------------

class CartDetailView(LoginRequiredMixin, TemplateView):
    """Shopping cart page showing all items, totals, and proceed to checkout."""

    template_name = "cart/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart.objects.filter(user=self.request.user).first()
        if cart:
            context["cart"] = cart
            context["cart_items"] = cart.cart_items.select_related(
                "product", "product__vendor", "product__vendor__storefront", "variant"
            ).prefetch_related("product__images")
        else:
            context["cart"] = None
            context["cart_items"] = []
        return context


# ---------------------------------------------------------------------------
# AF-E: Coupon Views
# ---------------------------------------------------------------------------

class ApplyCouponView(LoginRequiredMixin, View):
    """Apply a discount coupon to the user's cart."""

    def post(self, request):
        code = request.POST.get("code", "").strip()
        cart = Cart.objects.filter(user=request.user).first()
        
        if not cart or cart.is_empty:
            messages.error(request, "Your cart is empty.")
            return redirect("cart:detail")
            
        coupon = Coupon.objects.filter(code__iexact=code).first()
        
        if not coupon:
            messages.error(request, "Invalid coupon code.")
        elif not coupon.is_valid:
            messages.error(request, "This coupon has expired or reached its usage limit.")
        else:
            cart.coupon = coupon
            cart.save(update_fields=["coupon"])
            messages.success(request, f"Coupon '{coupon.code}' applied successfully!")
            
        return redirect("cart:detail")


class RemoveCouponView(LoginRequiredMixin, View):
    """Remove a discount coupon from the user's cart."""

    def post(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if cart and cart.coupon:
            cart.coupon = None
            cart.save(update_fields=["coupon"])
            messages.info(request, "Coupon removed.")
        return redirect("cart:detail")

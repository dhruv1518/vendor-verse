from django.db.models import Sum


def cart_processor(request):
    """
    Make the cart item count available in all templates for the navbar badge.
    Uses DB-level aggregation instead of Python iteration for performance.
    """
    cart_count = 0
    if request.user.is_authenticated:
        from apps.cart.models import CartItem
        result = CartItem.objects.filter(
            cart__user=request.user
        ).aggregate(total=Sum("quantity"))
        cart_count = result["total"] or 0
    return {"cart_count": cart_count}

def cart_processor(request):
    """
    Make the cart item count available in all templates for the navbar badge.
    """
    cart_count = 0
    if request.user.is_authenticated:
        from apps.cart.models import Cart
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = cart.total_items
    return {"cart_count": cart_count}

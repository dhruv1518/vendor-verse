from apps.products.models import Category


def categories_processor(request):
    """
    Make top-level categories (with their children) available in all templates
    for the mega menu / category dropdown in the navbar.
    """
    categories = (
        Category.objects.filter(is_active=True, parent__isnull=True)
        .prefetch_related("children")
        .order_by("display_order", "name")
    )
    return {"nav_categories": categories}

def recently_viewed_processor(request):
    """
    Exposes recently viewed products to templates based on session data.
    """
    from apps.products.models import Product
    recently_viewed_ids = request.session.get("recently_viewed", [])
    if not recently_viewed_ids:
        return {"recently_viewed_products": []}
        
    products = Product.objects.filter(public_id__in=recently_viewed_ids, status=Product.Status.ACTIVE).select_related("vendor__storefront").prefetch_related("images")
    product_dict = {str(p.public_id): p for p in products}
    ordered_products = [product_dict[pid] for pid in recently_viewed_ids if pid in product_dict]
    
    return {"recently_viewed_products": ordered_products}

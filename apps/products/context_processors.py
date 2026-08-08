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

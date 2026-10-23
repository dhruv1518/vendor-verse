import django_filters
from django import forms
from django.db.models import Q
from .models import Product, Category


class ProductFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method="filter_search", 
        label="Search",
        widget=forms.TextInput(attrs={
            "class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6",
            "placeholder": "Search products...",
            "autocomplete": "off",
            "id": "filter-search-input",
            "oninput": "const hq = document.getElementById('catalog-search-input'); if(hq && hq.value !== this.value) hq.value = this.value;",
        })
    )
    
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.filter(is_active=True).order_by("parent__id", "display_order", "name"),
        to_field_name="slug",
        empty_label="All Categories",
        method="filter_category",
        label="Category",
        widget=forms.Select(attrs={
            "class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6",
            "id": "filter-category-select",
        })
    )
    
    price_min = django_filters.NumberFilter(
        field_name="base_price",
        lookup_expr="gte",
        label="Min Price",
        widget=forms.NumberInput(attrs={
            "class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6",
            "placeholder": "₹ Min",
            "min": "0",
            "id": "filter-price-min",
        })
    )
    
    price_max = django_filters.NumberFilter(
        field_name="base_price",
        lookup_expr="lte",
        label="Max Price",
        widget=forms.NumberInput(attrs={
            "class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6",
            "placeholder": "₹ Max",
            "min": "0",
            "id": "filter-price-max",
        })
    )

    SORT_CHOICES = (
        ("newest", "Newest Arrivals"),
        ("price_asc", "Price: Low to High"),
        ("price_desc", "Price: High to Low"),
        ("name_asc", "Name: A to Z"),
    )
    
    sort_by = django_filters.ChoiceFilter(
        choices=SORT_CHOICES,
        method="filter_sort",
        label="Sort By",
        empty_label=None,
        widget=forms.Select(attrs={
            "class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6",
            "id": "filter-sort-select",
        })
    )

    class Meta:
        model = Product
        fields = ["category", "price_min", "price_max"]

    def filter_category(self, queryset, name, value):
        if not value:
            return queryset
        # Value is the Category model instance
        return queryset.filter(Q(category=value) | Q(category__parent=value)).distinct()

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | 
            Q(short_description__icontains=value) | 
            Q(description__icontains=value) |
            Q(vendor__business_name__icontains=value) |
            Q(tags__name__icontains=value)
        ).distinct()
        
    def filter_sort(self, queryset, name, value):
        if value == "price_asc":
            return queryset.order_by("base_price")
        elif value == "price_desc":
            return queryset.order_by("-base_price")
        elif value == "name_asc":
            return queryset.order_by("name")
        else:
            return queryset.order_by("-created_at")

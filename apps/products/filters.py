import django_filters
from django import forms
from .models import Product, Category

class ProductFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method="filter_search", 
        label="Search",
        widget=forms.TextInput(attrs={
            "class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6",
            "placeholder": "Search products..."
        })
    )
    
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={
            "class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6",
        })
    )
    
    price_min = django_filters.NumberFilter(
        field_name="base_price", lookup_expr="gte", label="Min Price",
        widget=forms.NumberInput(attrs={
            "class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6",
            "placeholder": "₹ Min"
        })
    )
    
    price_max = django_filters.NumberFilter(
        field_name="base_price", lookup_expr="lte", label="Max Price",
        widget=forms.NumberInput(attrs={
            "class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6",
            "placeholder": "₹ Max"
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
            "onchange": "this.form.dispatchEvent(new Event('submit', { cancelable: true }))"
        })
    )

    class Meta:
        model = Product
        fields = ["category"]

    def filter_search(self, queryset, name, value):
        from django.db.models import Q
        return queryset.filter(
            Q(name__icontains=value) | 
            Q(short_description__icontains=value) | 
            Q(description__icontains=value) |
            Q(vendor__business_name__icontains=value)
        )
        
    def filter_sort(self, queryset, name, value):
        if value == "price_asc":
            return queryset.order_by("base_price")
        elif value == "price_desc":
            return queryset.order_by("-base_price")
        elif value == "name_asc":
            return queryset.order_by("name")
        else:
            return queryset.order_by("-created_at")

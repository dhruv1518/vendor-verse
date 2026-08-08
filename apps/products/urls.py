from django.urls import path

from .views.vendor import (
    VendorProductListView,
    VendorProductCreateView,
    VendorProductEditView,
    VendorProductDeleteView,
)
from .views.web import ProductListView, ProductDetailView

app_name = "products"

urlpatterns = [
    # ----- Vendor Dashboard Product Management (Tasks 24 & 25) -----
    # These MUST come before the slug-based patterns to avoid conflicts
    path(
        "manage/",
        VendorProductListView.as_view(),
        name="vendor_product_list",
    ),
    path(
        "manage/add/",
        VendorProductCreateView.as_view(),
        name="vendor_product_create",
    ),
    path(
        "manage/<uuid:public_id>/edit/",
        VendorProductEditView.as_view(),
        name="vendor_product_edit",
    ),
    path(
        "manage/<uuid:public_id>/delete/",
        VendorProductDeleteView.as_view(),
        name="vendor_product_delete",
    ),

    # ----- Public Catalog (Task 26 & 27) -----
    path("", ProductListView.as_view(), name="product_list"),
    path(
        "<slug:vendor_slug>/<slug:product_slug>/",
        ProductDetailView.as_view(),
        name="product_detail",
    ),
]

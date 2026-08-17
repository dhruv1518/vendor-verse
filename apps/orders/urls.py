from django.urls import path

from .views.checkout import CheckoutView, CheckoutProcessView, OrderSuccessView
from .views.customer import CustomerOrderListView, CustomerOrderDetailView
from .views.vendor import (
    VendorOrderListView,
    VendorOrderDetailView,
    VendorOrderItemStatusView,
)

app_name = "orders"

urlpatterns = [
    # ----- Checkout Flow (Tasks 30 & 33) -----
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("checkout/process/", CheckoutProcessView.as_view(), name="checkout_process"),
    path(
        "success/<uuid:public_id>/",
        OrderSuccessView.as_view(),
        name="order_success",
    ),

    # ----- Customer Order History (Task 34) -----
    path("my-orders/", CustomerOrderListView.as_view(), name="customer_orders"),
    path(
        "my-orders/<uuid:public_id>/",
        CustomerOrderDetailView.as_view(),
        name="customer_order_detail",
    ),

    # ----- Vendor Order Management (Task 35) -----
    path(
        "vendor/orders/",
        VendorOrderListView.as_view(),
        name="vendor_order_list",
    ),
    path(
        "vendor/orders/<uuid:public_id>/",
        VendorOrderDetailView.as_view(),
        name="vendor_order_detail",
    ),
    path(
        "vendor/orders/item/<uuid:public_id>/status/",
        VendorOrderItemStatusView.as_view(),
        name="vendor_order_item_status",
    ),
]

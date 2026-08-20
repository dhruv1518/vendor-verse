from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.CartDetailView.as_view(), name="detail"),
    path("add/", views.AddToCartView.as_view(), name="add"),
    path(
        "update/<uuid:public_id>/",
        views.UpdateCartItemView.as_view(),
        name="update",
    ),
    path(
        "remove/<uuid:public_id>/",
        views.RemoveCartItemView.as_view(),
        name="remove",
    ),
    path("coupon/apply/", views.ApplyCouponView.as_view(), name="apply_coupon"),
    path("coupon/remove/", views.RemoveCouponView.as_view(), name="remove_coupon"),
]

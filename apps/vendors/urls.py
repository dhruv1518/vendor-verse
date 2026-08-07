from django.urls import path
from . import views

app_name = "vendors"

urlpatterns = [
    # Vendor Application (public-facing, under /vendors/)
    path("apply/", views.VendorApplyView.as_view(), name="apply"),
    path("apply/success/", views.VendorApplySuccessView.as_view(), name="apply_success"),

    # Public Vendor Directory (under /vendors/)
    path("", views.VendorDirectoryView.as_view(), name="directory"),

    # Vendor Dashboard (under /vendors/dashboard/)
    path("dashboard/", views.VendorDashboardView.as_view(), name="dashboard"),
    path(
        "dashboard/storefront/",
        views.StorefrontSettingsView.as_view(),
        name="storefront_settings",
    ),
]

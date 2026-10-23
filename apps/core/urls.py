from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    # Vendor Guides & Policies
    path("selling-guides/", views.SellingGuidesView.as_view(), name="selling_guides"),
    path("vendor-policies/", views.VendorPoliciesView.as_view(), name="vendor_policies"),

    # Company
    path("about/", views.AboutView.as_view(), name="about"),
    path("blog/", views.BlogView.as_view(), name="blog"),
    path("careers/", views.CareersView.as_view(), name="careers"),
    path("press/", views.PressView.as_view(), name="press"),

    # Support
    path("help/", views.HelpCenterView.as_view(), name="help"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("privacy/", views.PrivacyPolicyView.as_view(), name="privacy"),
    path("terms/", views.TermsOfServiceView.as_view(), name="terms"),
]

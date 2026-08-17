from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path(
        "<uuid:public_id>/",
        views.MockPaymentView.as_view(),
        name="payment",
    ),
    path(
        "<uuid:public_id>/process/",
        views.ProcessPaymentView.as_view(),
        name="process_payment",
    ),
]

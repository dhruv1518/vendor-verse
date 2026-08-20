from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path(
        "submit/<uuid:public_id>/",
        views.SubmitReviewView.as_view(),
        name="submit_review",
    ),
    path(
        "delete/<uuid:public_id>/",
        views.DeleteReviewView.as_view(),
        name="delete_review",
    ),
]

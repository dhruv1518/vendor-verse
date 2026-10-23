from django.urls import path
from .views import NotificationListView, MarkAllReadView, NotificationReadRedirectView

app_name = "notifications"

urlpatterns = [
    path("", NotificationListView.as_view(), name="list"),
    path("mark-all-read/", MarkAllReadView.as_view(), name="mark_all_read"),
    path("<uuid:pk>/read/", NotificationReadRedirectView.as_view(), name="read_redirect"),
]

from django.urls import path
from .views import NotificationListView, MarkAllReadView

app_name = "notifications"

urlpatterns = [
    path("", NotificationListView.as_view(), name="list"),
    path("mark-all-read/", MarkAllReadView.as_view(), name="mark_all_read"),
]

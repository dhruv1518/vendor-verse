from django.views.generic import ListView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from .models import Notification

class NotificationListView(LoginRequiredMixin, ListView):
    template_name = "notifications/list.html"
    context_object_name = "notifications"
    paginate_by = 20

    def get_queryset(self):
        # Mark all as read when viewed on this page? Optional, maybe we just list them.
        return Notification.objects.filter(user=self.request.user)

class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        # Redirect back to where they came from or home
        return redirect(request.META.get('HTTP_REFERER', '/'))

from django.views.generic import ListView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    template_name = "notifications/list.html"
    context_object_name = "notifications"
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class MarkAllReadView(LoginRequiredMixin, View):
    """Mark all unread notifications as read for the current user."""

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        
        # Check for AJAX, fetch, or HTMX
        if (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or "application/json" in request.headers.get("Accept", "")
            or getattr(request, "htmx", False)
        ):
            return JsonResponse({"status": "success", "unread_count": 0})
            
        messages.success(request, "All notifications marked as read.")
        referrer = request.META.get("HTTP_REFERER")
        if referrer and referrer.strip():
            return redirect(referrer)
        return redirect("notifications:list")


class NotificationReadRedirectView(LoginRequiredMixin, View):
    """Marks a single notification as read and redirects to its target link."""

    def get(self, request, pk, *args, **kwargs):
        notif = get_object_or_404(Notification, id=pk, user=request.user)
        if not notif.is_read:
            notif.is_read = True
            notif.save(update_fields=["is_read"])
            
        if notif.link and notif.link.strip():
            return redirect(notif.link)
        return redirect("notifications:list")

from .models import Notification

def notifications(request):
    """Adds unread notifications count to the context."""
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        # Fetch the latest 5 for the dropdown
        latest_notifications = Notification.objects.filter(user=request.user)[:5]
        return {
            "unread_notifications_count": unread_count,
            "latest_notifications": latest_notifications
        }
    return {
        "unread_notifications_count": 0,
        "latest_notifications": []
    }

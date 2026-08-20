from allauth.account.adapter import DefaultAccountAdapter


class VendorVerseAccountAdapter(DefaultAccountAdapter):
    """
    Custom allauth adapter that redirects admin/staff users
    to the Django admin panel after login, and regular users to the homepage.
    Also sends a welcome email on new user registration (Task 38).
    """

    def get_login_redirect_url(self, request):
        user = request.user
        if user.is_staff or user.is_superuser:
            return "/admin/"
        return "/"

    def save_user(self, request, user, form, commit=True):
        """Override to send welcome email after registration."""
        user = super().save_user(request, user, form, commit=commit)
        try:
            from apps.notifications.services import send_welcome_email
            send_welcome_email(user)
        except Exception:
            pass  # Email failures should not block registration
        return user

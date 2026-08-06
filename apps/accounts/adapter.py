from allauth.account.adapter import DefaultAccountAdapter


class VendorVerseAccountAdapter(DefaultAccountAdapter):
    """
    Custom allauth adapter that redirects admin/staff users
    to the Django admin panel after login, and regular users to the homepage.
    """

    def get_login_redirect_url(self, request):
        user = request.user
        if user.is_staff or user.is_superuser:
            return "/admin/"
        return "/"

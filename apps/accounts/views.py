from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from .forms import UserBasicForm, UserProfileForm
from .models import UserProfile


class ProfileView(LoginRequiredMixin, TemplateView):
    """View/Edit profile page. Shows two forms: user basics + profile details."""

    template_name = "account/profile.html"

    def get_profile(self):
        """Get or create the UserProfile for the logged-in user."""
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_profile()
        context["user_form"] = kwargs.get(
            "user_form", UserBasicForm(instance=self.request.user)
        )
        context["profile_form"] = kwargs.get(
            "profile_form", UserProfileForm(instance=profile)
        )
        return context

    def post(self, request, *args, **kwargs):
        profile = self.get_profile()
        user_form = UserBasicForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("accounts:profile")

        messages.error(request, "Please correct the errors below.")
        return self.render_to_response(
            self.get_context_data(
                user_form=user_form, profile_form=profile_form
            )
        )

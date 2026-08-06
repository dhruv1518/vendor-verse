from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from django.views import View

from .forms import UserBasicForm, UserProfileForm, AddressForm
from .models import Address, UserProfile


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


class AddressListView(LoginRequiredMixin, TemplateView):
    """List all addresses for the logged-in user, with an inline add/edit form."""

    template_name = "account/addresses.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["addresses"] = Address.objects.filter(
            user=self.request.user
        ).order_by("-is_default", "-created_at")
        # Pre-populate form for editing, or blank for adding
        edit_id = self.request.GET.get("edit")
        if edit_id:
            address = get_object_or_404(
                Address, public_id=edit_id, user=self.request.user
            )
            context["form"] = AddressForm(instance=address)
            context["editing"] = address
        else:
            context["form"] = AddressForm()
            context["editing"] = None
        return context


class AddressCreateView(LoginRequiredMixin, View):
    """Handle adding a new address."""

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            # If this is set as default, clear other defaults
            if address.is_default:
                Address.objects.filter(user=request.user, is_default=True).update(
                    is_default=False
                )
            address.save()
            messages.success(request, f'Address "{address.title}" added successfully!')
            return redirect("accounts:addresses")

        messages.error(request, "Please correct the errors below.")
        # Re-render the list page with the invalid form
        addresses = Address.objects.filter(user=request.user).order_by(
            "-is_default", "-created_at"
        )
        return AddressListView.as_view()(request)


class AddressEditView(LoginRequiredMixin, View):
    """Handle editing an existing address."""

    def post(self, request, public_id):
        address = get_object_or_404(Address, public_id=public_id, user=request.user)
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            if address.is_default:
                Address.objects.filter(user=request.user, is_default=True).exclude(
                    pk=address.pk
                ).update(is_default=False)
            address.save()
            messages.success(request, f'Address "{address.title}" updated successfully!')
            return redirect("accounts:addresses")

        messages.error(request, "Please correct the errors below.")
        return AddressListView.as_view()(request)


class AddressDeleteView(LoginRequiredMixin, View):
    """Handle deleting an address."""

    def post(self, request, public_id):
        address = get_object_or_404(Address, public_id=public_id, user=request.user)
        title = address.title
        address.delete()
        messages.success(request, f'Address "{title}" deleted.')
        return redirect("accounts:addresses")


class AddressSetDefaultView(LoginRequiredMixin, View):
    """Set an address as the default."""

    def post(self, request, public_id):
        address = get_object_or_404(Address, public_id=public_id, user=request.user)
        # Clear all defaults, then set this one
        Address.objects.filter(user=request.user, is_default=True).update(
            is_default=False
        )
        address.is_default = True
        address.save()
        messages.success(request, f'"{address.title}" is now your default address.')
        return redirect("accounts:addresses")


from django import forms
from django.contrib.auth import get_user_model
from .models import Address, UserProfile

User = get_user_model()


class UserBasicForm(forms.ModelForm):
    """Form for editing the User model fields (first_name, last_name)."""

    class Meta:
        model = User
        fields = ["first_name", "last_name"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6",
                    "placeholder": "First name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6",
                    "placeholder": "Last name",
                }
            ),
        }


class UserProfileForm(forms.ModelForm):
    """Form for editing the UserProfile model fields (avatar, bio, phone)."""

    class Meta:
        model = UserProfile
        fields = ["avatar", "bio", "phone_number"]
        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6",
                    "rows": 4,
                    "placeholder": "Tell us about yourself...",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6",
                    "placeholder": "+91 98765 43210",
                }
            ),
            "avatar": forms.ClearableFileInput(
                attrs={
                    "class": "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 cursor-pointer",
                    "accept": "image/*",
                }
            ),
        }


INPUT_CLASS = (
    "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm "
    "ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 "
    "focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
)


class AddressForm(forms.ModelForm):
    """Form for creating/editing a shipping address."""

    class Meta:
        model = Address
        fields = [
            "title",
            "street_address",
            "city",
            "state",
            "postal_code",
            "country",
            "is_default",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "e.g., Home, Work, Mom's Place"}
            ),
            "street_address": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "123 Main Street, Apt 4B"}
            ),
            "city": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "Mumbai"}
            ),
            "state": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "Maharashtra"}
            ),
            "postal_code": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "400001"}
            ),
            "country": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "India"}
            ),
            "is_default": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-600"
                }
            ),
        }

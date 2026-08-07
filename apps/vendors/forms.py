from django import forms

from .models import VendorApplication, Storefront

INPUT_CLASS = (
    "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm "
    "ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 "
    "focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
)

TEXTAREA_CLASS = (
    "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm "
    "ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 "
    "focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
)

FILE_CLASS = (
    "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 "
    "file:rounded-md file:border-0 file:text-sm file:font-semibold "
    "file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 cursor-pointer"
)


class VendorApplicationForm(forms.ModelForm):
    """Form for customers to apply to become a vendor."""

    class Meta:
        model = VendorApplication
        fields = ["business_name", "business_description", "business_email", "phone_number"]
        widgets = {
            "business_name": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Your business or brand name",
                }
            ),
            "business_description": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "rows": 5,
                    "placeholder": "Tell us about your business, what products you sell, and why you'd like to join VendorVerse...",
                }
            ),
            "business_email": forms.EmailInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "business@example.com",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "+91 98765 43210 (optional)",
                }
            ),
        }


class StorefrontSettingsForm(forms.ModelForm):
    """Form for vendors to update their storefront details."""

    class Meta:
        model = Storefront
        fields = [
            "tagline",
            "description",
            "logo",
            "banner",
            "return_policy",
            "shipping_policy",
        ]
        widgets = {
            "tagline": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "A short tagline for your store",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "rows": 5,
                    "placeholder": "Tell customers what makes your store special...",
                }
            ),
            "logo": forms.ClearableFileInput(
                attrs={
                    "class": FILE_CLASS,
                    "accept": "image/*",
                }
            ),
            "banner": forms.ClearableFileInput(
                attrs={
                    "class": FILE_CLASS,
                    "accept": "image/*",
                }
            ),
            "return_policy": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "rows": 4,
                    "placeholder": "Describe your return and refund policy...",
                }
            ),
            "shipping_policy": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "rows": 4,
                    "placeholder": "Describe your shipping options and delivery times...",
                }
            ),
        }

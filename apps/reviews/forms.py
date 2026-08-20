from django import forms
from .models import Review


# ---------------------------------------------------------------------------
# Task 37 — Review Form
# ---------------------------------------------------------------------------

class ReviewForm(forms.ModelForm):
    """Form for customers to submit a product review."""

    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.HiddenInput(),
        error_messages={
            "required": "Please select a star rating.",
            "min_value": "Rating must be at least 1 star.",
            "max_value": "Rating cannot exceed 5 stars.",
        },
    )

    class Meta:
        model = Review
        fields = ["rating", "title", "comment"]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Summarize your experience (optional)",
                "class": "mt-1 block w-full rounded-xl border-gray-300 shadow-sm "
                         "focus:border-primary-500 focus:ring-primary-500 text-sm",
            }),
            "comment": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Tell other customers about your experience with this product...",
                "class": "mt-1 block w-full rounded-xl border-gray-300 shadow-sm "
                         "focus:border-primary-500 focus:ring-primary-500 text-sm",
            }),
        }

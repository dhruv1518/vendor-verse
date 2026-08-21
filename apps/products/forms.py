from django import forms
from django.forms import inlineformset_factory

from .models import Product, ProductImage, ProductVariant, Category

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

SELECT_CLASS = (
    "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm "
    "ring-1 ring-inset ring-gray-300 "
    "focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
)

FILE_CLASS = (
    "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 "
    "file:rounded-md file:border-0 file:text-sm file:font-semibold "
    "file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 cursor-pointer"
)

CHECKBOX_CLASS = (
    "h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-600"
)

NUMBER_CLASS = (
    "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm "
    "ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 "
    "focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
)


class ProductForm(forms.ModelForm):
    """Form for vendors to create/edit products."""

    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "short_description",
            "description",
            "base_price",
            "compare_at_price",
            "stock_quantity",
            "sku",
            "status",
            "is_featured",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Product name",
                    "id": "product-name",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": SELECT_CLASS,
                    "id": "product-category",
                }
            ),
            "short_description": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Brief summary for product cards",
                    "id": "product-short-desc",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "rows": 6,
                    "placeholder": "Full product description...",
                    "id": "product-description",
                }
            ),
            "base_price": forms.NumberInput(
                attrs={
                    "class": NUMBER_CLASS,
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0",
                    "id": "product-price",
                }
            ),
            "compare_at_price": forms.NumberInput(
                attrs={
                    "class": NUMBER_CLASS,
                    "placeholder": "Original price (optional)",
                    "step": "0.01",
                    "min": "0",
                    "id": "product-compare-price",
                }
            ),
            "stock_quantity": forms.NumberInput(
                attrs={
                    "class": NUMBER_CLASS,
                    "placeholder": "0",
                    "min": "0",
                    "id": "product-stock",
                }
            ),
            "sku": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "SKU-001 (optional)",
                    "id": "product-sku",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": SELECT_CLASS,
                    "id": "product-status",
                }
            ),
            "is_featured": forms.CheckboxInput(
                attrs={
                    "class": CHECKBOX_CLASS,
                    "id": "product-featured",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active categories
        self.fields["category"].queryset = Category.objects.filter(is_active=True)
        self.fields["category"].empty_label = "— Select a category —"


class ProductImageForm(forms.ModelForm):
    """Form for uploading a product image."""

    class Meta:
        model = ProductImage
        fields = ["image", "alt_text", "is_primary"]
        widgets = {
            "image": forms.ClearableFileInput(
                attrs={
                    "class": FILE_CLASS,
                    "accept": "image/*",
                }
            ),
            "alt_text": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Image description",
                }
            ),
            "is_primary": forms.CheckboxInput(
                attrs={
                    "class": CHECKBOX_CLASS,
                }
            ),
        }


# Inline formset for managing multiple images at once
ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=3,
    max_num=10,
    can_delete=True,
)


class ProductVariantForm(forms.ModelForm):
    """Form for managing a product variant."""

    class Meta:
        model = ProductVariant
        fields = ["name", "sku", "price_override", "stock_quantity", "is_active"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "e.g., Large / Red",
                }
            ),
            "sku": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Variant SKU (optional)",
                }
            ),
            "price_override": forms.NumberInput(
                attrs={
                    "class": NUMBER_CLASS,
                    "placeholder": "Leave blank for base price",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "stock_quantity": forms.NumberInput(
                attrs={
                    "class": NUMBER_CLASS,
                    "placeholder": "0",
                    "min": "0",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": CHECKBOX_CLASS,
                }
            ),
        }


# Inline formset for managing multiple variants at once
ProductVariantFormSet = inlineformset_factory(
    Product,
    ProductVariant,
    form=ProductVariantForm,
    extra=2,
    max_num=20,
    can_delete=True,
)


# ---------------------------------------------------------------------------
# AF-I: Q&A Forms
# ---------------------------------------------------------------------------

from .models import Question, Answer

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={
                "class": TEXTAREA_CLASS,
                "rows": 3,
                "placeholder": "Ask a question about this product..."
            }),
        }
        labels = {
            "text": ""
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={
                "class": TEXTAREA_CLASS,
                "rows": 2,
                "placeholder": "Type your answer..."
            }),
        }
        labels = {
            "text": ""
        }

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, TemplateView

from apps.core.mixins import VendorRequiredMixin
from apps.products.models import Product, ProductImage
from apps.products.forms import ProductForm, ProductImageFormSet, ProductVariantFormSet


# ---------------------------------------------------------------------------
# Task 24 — Vendor Product List Page
# ---------------------------------------------------------------------------

class VendorProductListView(VendorRequiredMixin, ListView):
    """List products belonging only to the logged-in vendor."""

    template_name = "vendors/products/list.html"
    context_object_name = "products"
    paginate_by = 15

    def get_queryset(self):
        vendor = self.request.user.vendor
        qs = (
            Product.objects.filter(vendor=vendor)
            .select_related("category")
            .prefetch_related("images")
            .order_by("-created_at")
        )

        # Simple search
        search = self.request.GET.get("q", "").strip()
        if search:
            qs = qs.filter(name__icontains=search)

        # Status filter
        status = self.request.GET.get("status", "").strip()
        if status in dict(Product.Status.choices):
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vendor"] = self.request.user.vendor
        context["storefront"] = getattr(self.request.user.vendor, "storefront", None)
        context["active_page"] = "products"
        context["search_query"] = self.request.GET.get("q", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["status_choices"] = Product.Status.choices
        return context


# ---------------------------------------------------------------------------
# Task 25 — Vendor Product Create & Edit Page
# ---------------------------------------------------------------------------

class VendorProductCreateView(VendorRequiredMixin, TemplateView):
    """Form page to add a new product."""

    template_name = "vendors/products/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = kwargs.get("form", ProductForm())
        context["image_formset"] = kwargs.get("image_formset", ProductImageFormSet())
        context["variant_formset"] = kwargs.get("variant_formset", ProductVariantFormSet())
        context["vendor"] = self.request.user.vendor
        context["storefront"] = getattr(self.request.user.vendor, "storefront", None)
        context["active_page"] = "products"
        context["is_edit"] = False
        context["page_title"] = "Add New Product"
        return context

    def post(self, request, *args, **kwargs):
        form = ProductForm(request.POST)
        image_formset = ProductImageFormSet(request.POST, request.FILES)
        variant_formset = ProductVariantFormSet(request.POST)

        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.save()
            form.save_m2m()  # Save tags ManyToMany

            # Process images
            image_formset = ProductImageFormSet(
                request.POST, request.FILES, instance=product
            )
            if image_formset.is_valid():
                image_formset.save()

            # Process variants
            variant_formset = ProductVariantFormSet(request.POST, instance=product)
            if variant_formset.is_valid():
                variant_formset.save()

            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect("products:vendor_product_list")

        messages.error(request, "Please correct the errors below.")
        return self.render_to_response(
            self.get_context_data(
                form=form,
                image_formset=image_formset,
                variant_formset=variant_formset,
            )
        )


class VendorProductEditView(VendorRequiredMixin, TemplateView):
    """Form page to edit an existing product."""

    template_name = "vendors/products/form.html"

    def get_product(self):
        return get_object_or_404(
            Product, public_id=self.kwargs["public_id"], vendor=self.request.user.vendor
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_product()
        context["form"] = kwargs.get("form", ProductForm(instance=product))
        context["image_formset"] = kwargs.get(
            "image_formset", ProductImageFormSet(instance=product)
        )
        context["variant_formset"] = kwargs.get(
            "variant_formset", ProductVariantFormSet(instance=product)
        )
        context["product"] = product
        context["vendor"] = self.request.user.vendor
        context["storefront"] = getattr(self.request.user.vendor, "storefront", None)
        context["active_page"] = "products"
        context["is_edit"] = True
        context["page_title"] = f"Edit: {product.name}"
        return context

    def post(self, request, *args, **kwargs):
        product = self.get_product()
        form = ProductForm(request.POST, instance=product)
        image_formset = ProductImageFormSet(
            request.POST, request.FILES, instance=product
        )
        variant_formset = ProductVariantFormSet(request.POST, instance=product)

        if form.is_valid() and image_formset.is_valid() and variant_formset.is_valid():
            product = form.save()
            image_formset.save()
            variant_formset.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect("products:vendor_product_list")

        messages.error(request, "Please correct the errors below.")
        return self.render_to_response(
            self.get_context_data(
                form=form,
                image_formset=image_formset,
                variant_formset=variant_formset,
            )
        )


class VendorProductDeleteView(VendorRequiredMixin, TemplateView):
    """Confirm and delete a product."""

    template_name = "vendors/products/confirm_delete.html"

    def get_product(self):
        return get_object_or_404(
            Product, public_id=self.kwargs["public_id"], vendor=self.request.user.vendor
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product"] = self.get_product()
        context["vendor"] = self.request.user.vendor
        context["storefront"] = getattr(self.request.user.vendor, "storefront", None)
        context["active_page"] = "products"
        return context

    def post(self, request, *args, **kwargs):
        product = self.get_product()
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" has been deleted.')
        return redirect("products:vendor_product_list")

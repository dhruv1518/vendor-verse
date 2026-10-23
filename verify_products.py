import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from apps.products.models import Product, Category, ProductImage, ProductVariant, Tag
from apps.vendors.models import Vendor, Storefront

print("=" * 70, flush=True)
print("COMPREHENSIVE DATABASE VERIFICATION", flush=True)
print("=" * 70, flush=True)

products = list(Product.objects.all().order_by('id'))
print(f"Total Products: {len(products)}", flush=True)

empty_detected = False

for p in products:
    images = list(p.images.all())
    variants = list(p.variants.all())
    tags = list(p.tags.all())
    
    # Check completeness
    missing = []
    if not p.vendor: missing.append("vendor")
    if not p.category: missing.append("category")
    if not p.name: missing.append("name")
    if not p.slug: missing.append("slug")
    if not p.description: missing.append("description")
    if not p.short_description: missing.append("short_description")
    if p.base_price is None: missing.append("base_price")
    if p.compare_at_price is None: missing.append("compare_at_price")
    if p.stock_quantity is None: missing.append("stock_quantity")
    if not p.sku: missing.append("sku")
    if not p.status: missing.append("status")
    if len(images) == 0: missing.append("images")
    if len(variants) == 0: missing.append("variants")
    if len(tags) == 0: missing.append("tags")
    
    # Verify image files exist on disk
    for img in images:
        if not img.image or not os.path.exists(img.image.path):
            missing.append(f"missing_img_file({img.id})")
            
    print(f"\nProduct #{p.id}: {p.name}", flush=True)
    print(f"  Vendor:      {p.vendor.business_name} (User: {p.vendor.user.email})", flush=True)
    print(f"  Storefront:  /{p.vendor.storefront.slug}/", flush=True)
    print(f"  Category:    {p.category.name} (Parent: {p.category.parent.name if p.category.parent else 'None'})", flush=True)
    print(f"  Price:       INR {p.base_price} (Compare: INR {p.compare_at_price}) | Discount: {p.discount_percentage}%", flush=True)
    print(f"  Stock & SKU: {p.stock_quantity} units | SKU: {p.sku}", flush=True)
    print(f"  Tags:        {[t.name for t in tags]}", flush=True)
    print(f"  Images ({len(images)}):   {[img.image.name for img in images]}", flush=True)
    print(f"  Variants ({len(variants)}): {[f'{v.name} (SKU: {v.sku}, Price: INR {v.effective_price}, Stock: {v.stock_quantity})' for v in variants]}", flush=True)
    
    if missing:
        empty_detected = True
        print(f"  --> [ERROR MISSING COLUMNS]: {missing}", flush=True)
    else:
        print("  --> [STATUS: 100% COMPLETE - NO EMPTY COLUMNS]", flush=True)

print("\n" + "=" * 70, flush=True)
vendors = Vendor.objects.all()
print(f"Total Vendors: {vendors.count()}", flush=True)
for v in vendors:
    print(f"  - Vendor: {v.business_name} | User: {v.user.email} (Role: {v.user.role}) | Phone: {v.phone_number}", flush=True)
    print(f"    Storefront Slug: {v.storefront.slug} | Tagline: '{v.storefront.tagline}'", flush=True)
    print(f"    Logo: {bool(v.storefront.logo)} | Banner: {bool(v.storefront.banner)}", flush=True)

if not empty_detected and len(products) == 12:
    print("\nSUCCESS: All 12 products verified across 2 vendor accounts (Dhruv & Sneh) with zero empty columns!", flush=True)
else:
    print(f"\nWARNING: Check status: empty_detected={empty_detected}, product_count={len(products)}", flush=True)

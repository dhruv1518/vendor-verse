import os
import re
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from pathlib import Path
from django.conf import settings
from django.urls import get_resolver, reverse
from apps.products.models import Product, Category, ProductImage, ProductVariant, Tag
from apps.vendors.models import Vendor, Storefront, VendorApplication
from apps.orders.models import Order, OrderItem
from apps.cart.models import Cart, CartItem
from apps.reviews.models import Review
from apps.accounts.models import User

print("=" * 70, flush=True)
print("COMPREHENSIVE CODEBASE AUDIT", flush=True)
print("=" * 70, flush=True)

issues = []

# -------------------------------------------------------------
# 1. URL Resolution & Template URL Tag Audit
# -------------------------------------------------------------
print("\n[CHECK 1] Auditing template {% url %} tags against registered routes...", flush=True)
resolver = get_resolver()

def collect_urls(url_patterns, prefix=''):
    names = set()
    for pattern in url_patterns:
        if hasattr(pattern, 'url_patterns'):
            ns = getattr(pattern, 'namespace', None)
            new_prefix = f"{prefix}:{ns}" if prefix and ns else (ns or prefix)
            names.update(collect_urls(pattern.url_patterns, new_prefix))
        elif hasattr(pattern, 'name') and pattern.name:
            full_name = f"{prefix}:{pattern.name}" if prefix else pattern.name
            names.add(full_name)
    return names

all_named_urls = collect_urls(resolver.url_patterns)
print(f"  Total registered URL pattern names: {len(all_named_urls)}", flush=True)

url_pattern_regex = re.compile(r'{%\s*url\s+[\'"]([^\'" ]+)[\'"]')
template_dir = Path(settings.BASE_DIR) / 'templates'

invalid_template_urls = []
for root, dirs, files in os.walk(template_dir):
    for f in files:
        if f.endswith('.html'):
            filepath = Path(root) / f
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            matches = url_pattern_regex.findall(content)
            for m in matches:
                if not m.startswith('http') and m not in all_named_urls:
                    invalid_template_urls.append((filepath.name, m))

if invalid_template_urls:
    for fname, u in set(invalid_template_urls):
        issues.append(f"Template {fname} references unknown URL pattern '{u}'")
        print(f"  [FAIL] {fname} -> '{u}' not found in registered URLs!", flush=True)
else:
    print("  [PASS] All template {% url %} tags resolve to valid route names.", flush=True)

# -------------------------------------------------------------
# 2. Storefront & Vendor Safety Audit
# -------------------------------------------------------------
print("\n[CHECK 2] Auditing Vendors, Storefronts & Product linkages...", flush=True)
for v in Vendor.objects.all():
    if not hasattr(v, 'storefront'):
        issues.append(f"Vendor '{v.business_name}' (ID: {v.id}) is missing a Storefront object.")
        print(f"  [WARN] Vendor '{v.business_name}' has no storefront!", flush=True)
    elif not v.storefront.slug:
        issues.append(f"Vendor '{v.business_name}' storefront has an empty slug.")
        print(f"  [WARN] Vendor '{v.business_name}' storefront slug is empty!", flush=True)
    else:
        print(f"  [PASS] Vendor '{v.business_name}' -> Storefront slug: '{v.storefront.slug}'", flush=True)

for p in Product.objects.all():
    if not p.vendor:
        issues.append(f"Product '{p.name}' (ID: {p.id}) has NO vendor assigned.")
    elif not hasattr(p.vendor, 'storefront') or not p.vendor.storefront.slug:
        issues.append(f"Product '{p.name}' vendor '{p.vendor.business_name}' has no valid storefront slug! Product card links will break!")

# -------------------------------------------------------------
# 3. Product Media & Image References Audit
# -------------------------------------------------------------
print("\n[CHECK 3] Auditing Product Images on disk...", flush=True)
for p in Product.objects.all():
    primary = p.primary_image
    if not primary:
        issues.append(f"Product '{p.name}' has no primary image.")
    elif not primary.image or not os.path.exists(primary.image.path):
        issues.append(f"Product '{p.name}' image file '{primary.image.name}' missing from disk.")

# -------------------------------------------------------------
# 4. Categories Hierarchy & Cycles Audit
# -------------------------------------------------------------
print("\n[CHECK 4] Auditing Category hierarchy and cycle detection...", flush=True)
for cat in Category.objects.all():
    visited = set()
    curr = cat
    has_cycle = False
    while curr.parent:
        if curr.id in visited:
            has_cycle = True
            break
        visited.add(curr.id)
        curr = curr.parent
    if has_cycle:
        issues.append(f"Circular parent hierarchy detected in category '{cat.name}'")

# -------------------------------------------------------------
# 5. Template Image Safety Check (.url without guard)
# -------------------------------------------------------------
print("\n[CHECK 5] Auditing unsafe .image.url or .avatar.url access in templates...", flush=True)
unsafe_url_regex = re.compile(r'\{\{\s*([a-zA-Z0-9_\.]+\.(?:image|avatar|logo|banner)\.url)\s*\}\}')
for root, dirs, files in os.walk(template_dir):
    for f in files:
        if f.endswith('.html'):
            filepath = Path(root) / f
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            matches = unsafe_url_regex.findall(content)
            for m in matches:
                # Check if preceding block has an {% if ... %} guard
                var_base = m.replace('.url', '')
                if f"if {var_base}" not in content and f"if not" not in content:
                    print(f"  [NOTICE] Potential unguarded media access in {filepath.name}: {m}", flush=True)

# -------------------------------------------------------------
# 6. Static Files Referenced in Templates
# -------------------------------------------------------------
print("\n[CHECK 6] Auditing {% static %} references...", flush=True)
static_pattern_regex = re.compile(r'{%\s*static\s+[\'"]([^\'" ]+)[\'"]')
static_dirs = [Path(settings.BASE_DIR) / 'static']
for s in getattr(settings, 'STATICFILES_DIRS', []):
    static_dirs.append(Path(s))

missing_static = []
for root, dirs, files in os.walk(template_dir):
    for f in files:
        if f.endswith('.html'):
            filepath = Path(root) / f
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            matches = static_pattern_regex.findall(content)
            for m in matches:
                exists = any((d / m).exists() for d in static_dirs)
                if not exists:
                    missing_static.append((filepath.name, m))

if missing_static:
    for fname, s in set(missing_static):
        print(f"  [WARN] {fname} references static file '{s}' not found in static dirs.", flush=True)
else:
    print("  [PASS] All static references resolved.", flush=True)

# -------------------------------------------------------------
# SUMMARY REPORT
# -------------------------------------------------------------
print("\n" + "=" * 70, flush=True)
print("AUDIT SUMMARY", flush=True)
print("=" * 70, flush=True)
if issues:
    print(f"FAILED: Found {len(issues)} issue(s):", flush=True)
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}", flush=True)
else:
    print("SUCCESS: Zero errors or contradictions found across models, routes, templates, and assets!", flush=True)

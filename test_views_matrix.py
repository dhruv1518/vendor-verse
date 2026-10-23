import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.test import Client
from apps.accounts.models import User
from apps.products.models import Product
from apps.vendors.models import Storefront

print("=" * 70, flush=True)
print("TESTING ALL VIEWS ACROSS ROLES", flush=True)
print("=" * 70, flush=True)

anon_client = Client()

customer = User.objects.filter(role=User.Role.CUSTOMER).first()
customer_client = Client()
if customer:
    customer_client.force_login(customer)

vendor = User.objects.filter(role=User.Role.VENDOR, email="db@gmail.com").first()
vendor_client = Client()
if vendor:
    vendor_client.force_login(vendor)

admin = User.objects.filter(is_superuser=True).first()
admin_client = Client()
if admin:
    admin_client.force_login(admin)

test_matrix = [
    # (Client, Role, URL, Expected Statuses)
    (anon_client, "ANON", "/", [200]),
    (anon_client, "ANON", "/products/", [200]),
    (anon_client, "ANON", "/cart/", [302]),
    (anon_client, "ANON", "/vendors/apply/", [200, 302]),
    (anon_client, "ANON", "/store/dhruv-retail-shop/", [200]),
    (anon_client, "ANON", "/store/sneh-fashion-hub/", [200]),
    (anon_client, "ANON", "/products/dhruv-retail-shop/ultra-smartphone-pro-max-5g/", [200]),
    (anon_client, "ANON", "/products/sneh-fashion-hub/royal-heritage-chanderi-silk-anarkali-set/", [200]),
    
    # Customer
    (customer_client, "CUSTOMER", "/profile/", [200]),
    (customer_client, "CUSTOMER", "/profile/addresses/", [200]),
    (customer_client, "CUSTOMER", "/cart/", [200]),
    (customer_client, "CUSTOMER", "/products/wishlist/", [200]),
    (customer_client, "CUSTOMER", "/vendors/apply/", [200]),
    
    # Vendor
    (vendor_client, "VENDOR", "/vendors/dashboard/", [200]),
    (vendor_client, "VENDOR", "/products/manage/", [200]),
    (vendor_client, "VENDOR", "/vendors/dashboard/storefront/", [200]),
    (vendor_client, "VENDOR", "/orders/vendor/orders/", [200]),
    
    # Admin
    (admin_client, "ADMIN", "/admin/", [200]),
    (admin_client, "ADMIN", "/admin/products/product/", [200]),
    (admin_client, "ADMIN", "/admin/vendors/vendor/", [200]),
    (admin_client, "ADMIN", "/admin/orders/order/", [200]),
]

failed = []
passed = 0

for client_inst, role, url, allowed_statuses in test_matrix:
    try:
        res = client_inst.get(url, HTTP_HOST='127.0.0.1')
        if res.status_code in allowed_statuses:
            passed += 1
            print(f"  [PASS] ({role}) {url} -> {res.status_code}", flush=True)
        else:
            failed.append((role, url, res.status_code))
            print(f"  [FAIL] ({role}) {url} -> {res.status_code} (Expected {allowed_statuses})", flush=True)
    except Exception as e:
        failed.append((role, url, str(e)))
        print(f"  [EXCEPTION] ({role}) {url} -> {e}", flush=True)

print("\n" + "=" * 70, flush=True)
if failed:
    print(f"FAILED: {len(failed)} route(s) failed:", flush=True)
    for r, u, s in failed:
        print(f"  - ({r}) {u} -> {s}", flush=True)
else:
    print(f"ALL {passed} ROUTES TESTED PASSED WITH FLYING COLORS!", flush=True)

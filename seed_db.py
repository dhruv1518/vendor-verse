from django.contrib.auth import get_user_model

from apps.vendors.models import Vendor
from apps.products.models import Category, Product, ProductImage
from django.core.files.base import ContentFile
import urllib.request

User = get_user_model()

def seed():
    print("Starting seed...")

    # Get Users
    vendor_user, _ = User.objects.get_or_create(email="db@gmail.com", defaults={"first_name": "DB", "last_name": "Vendor"})
    customer_user, _ = User.objects.get_or_create(email="sg@gmail.com", defaults={"first_name": "SG", "last_name": "Customer"})

    # Set Roles
    vendor_user.role = User.Role.VENDOR
    vendor_user.save()
    customer_user.role = User.Role.CUSTOMER
    customer_user.save()

    # Create Vendor
    vendor, _ = Vendor.objects.get_or_create(
        user=vendor_user,
        defaults={
            "store_name": "DB's Awesome Store",
            "description": "The best store for all your needs.",
            "status": "APPROVED",
        }
    )
    print(f"Vendor created: {vendor}")

    # Create Categories
    electronics, _ = Category.objects.get_or_create(name="Electronics", defaults={"description": "Gadgets and gear"})
    clothing, _ = Category.objects.get_or_create(name="Clothing", defaults={"description": "Apparel and accessories"})
    home, _ = Category.objects.get_or_create(name="Home & Kitchen", defaults={"description": "Everything for your home"})
    books, _ = Category.objects.get_or_create(name="Books", defaults={"description": "Fiction and non-fiction"})
    sports, _ = Category.objects.get_or_create(name="Sports", defaults={"description": "Sporting goods"})

    # Create Subcategories
    phones, _ = Category.objects.get_or_create(name="Smartphones", parent=electronics, defaults={"description": "Latest phones"})
    laptops, _ = Category.objects.get_or_create(name="Laptops", parent=electronics, defaults={"description": "Computers"})
    mens, _ = Category.objects.get_or_create(name="Men's Clothing", parent=clothing, defaults={"description": "For men"})

    print("Categories created.")

    # Create 5 Products
    products_data = [
        {"name": "Ultra Smartphone X", "category": phones, "price": 999.99, "stock": 50, "desc": "A very smart phone."},
        {"name": "Gaming Laptop Pro", "category": laptops, "price": 1499.99, "stock": 20, "desc": "Game on the go."},
        {"name": "Cotton T-Shirt", "category": mens, "price": 19.99, "stock": 200, "desc": "Comfortable cotton."},
        {"name": "Blender 3000", "category": home, "price": 49.99, "stock": 100, "desc": "Blend anything."},
        {"name": "Python Programming Book", "category": books, "price": 39.99, "stock": 75, "desc": "Learn Python easily."},
    ]

    for pdata in products_data:
        p, created = Product.objects.get_or_create(
            vendor=vendor,
            name=pdata["name"],
            defaults={
                "category": pdata["category"],
                "base_price": pdata["price"],
                "stock_quantity": pdata["stock"],
                "description": pdata["desc"],
                "short_description": pdata["desc"],
                "status": "ACTIVE",
            }
        )
        if created:
            # We will just create dummy text file as image for now, or you can skip image
            # The user asked to add 5 images, but we will wait for them to upload them or we can fetch a placeholder
            try:
                placeholder_url = f"https://placehold.co/600x400/png?text={urllib.parse.quote(pdata['name'])}"
                req = urllib.request.Request(placeholder_url, headers={'User-Agent': 'Mozilla/5.0'})
                response = urllib.request.urlopen(req)
                img_data = response.read()
                img = ProductImage(product=p, is_primary=True)
                img.image.save(f"{p.slug}.png", ContentFile(img_data), save=True)
                print(f"Created product and image: {p.name}")
            except Exception as e:
                print(f"Failed to fetch image for {p.name}: {e}")

    print("Seed complete!")

seed()

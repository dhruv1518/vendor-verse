import os
import sys
import django
import urllib.request
from decimal import Decimal
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.text import slugify

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from apps.accounts.models import User
from apps.vendors.models import Vendor, Storefront, VendorApplication
from apps.vendors.services import approve_vendor_application
from apps.products.models import Category, Product, ProductImage, ProductVariant, Tag

from concurrent.futures import ThreadPoolExecutor

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
IMAGE_CACHE = {}

def fetch_single_image(url):
    if not url or url in IMAGE_CACHE:
        return url, IMAGE_CACHE.get(url)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            IMAGE_CACHE[url] = data
            return url, data
    except Exception as e:
        print(f"  [WARN] Failed to fetch image from {url}: {e}", flush=True)
        return url, None

def prefetch_all_images(url_list):
    print(f">>> Pre-fetching {len(url_list)} images concurrently in background pool...", flush=True)
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(fetch_single_image, url_list))
    print(f"  [OK] Successfully cached {len([r for r in results if r[1]])} images.", flush=True)

def get_image(url):
    return IMAGE_CACHE.get(url) or fetch_single_image(url)[1]

def run():
    print("=" * 60)
    print("Starting Comprehensive Product & Vendor Population")
    print("=" * 60)

    # Gather all URLs for prefetching
    all_urls = [
        "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&q=80",
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80",
        "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=400&q=80",
        "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1200&q=80",
        "https://images.unsplash.com/photo-1550009158-9ebf69173e03?w=800&q=80",
        "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=800&q=80",
        "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=800&q=80",
        "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800&q=80",
        "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=800&q=80",
        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&q=80",
        "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800&q=80",
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=800&q=80",
        "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&q=80",
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80",
        "https://images.unsplash.com/photo-1627123424574-724758594e93?w=800&q=80",
        "https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=800&q=80",
        "https://images.unsplash.com/photo-1612196808214-b8e1d6145a8c?w=800&q=80",
        "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800&q=80",
        "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&q=80",
        "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=1000&q=80",
    ]
    prefetch_all_images(all_urls)

    # -------------------------------------------------------------
    # 1. SETUP VENDORS: DHRUV & SNEH
    # -------------------------------------------------------------
    print("\n>>> Setting up Vendor: Dhruv...", flush=True)
    dhruv_user, _ = User.objects.get_or_create(
        email="db@gmail.com",
        defaults={
            "first_name": "Dhruv",
            "last_name": "Bhavsar",
            "role": User.Role.VENDOR,
            "is_active": True,
        }
    )
    dhruv_user.first_name = "Dhruv"
    dhruv_user.last_name = "Bhavsar"
    dhruv_user.role = User.Role.VENDOR
    dhruv_user.save()

    dhruv_vendor, _ = Vendor.objects.get_or_create(
        user=dhruv_user,
        defaults={
            "business_name": "Dhruv Retail Shop",
            "business_email": "db@gmail.com",
            "phone_number": "+91 98251 44520",
            "is_active": True,
        }
    )
    dhruv_vendor.business_name = "Dhruv Retail Shop"
    dhruv_vendor.business_email = "db@gmail.com"
    dhruv_vendor.phone_number = "+91 98251 44520"
    dhruv_vendor.is_active = True
    dhruv_vendor.save()

    dhruv_store, _ = Storefront.objects.get_or_create(vendor=dhruv_vendor)
    dhruv_store.slug = "dhruv-retail-shop"
    dhruv_store.tagline = "Premium Consumer Electronics, Computing & Modern Living"
    dhruv_store.description = (
        "Welcome to Dhruv Retail Shop. We curate high-performance electronics, gaming rigs, "
        "studio acoustics, and intelligent home appliances backed by complete manufacturer warranty."
    )
    dhruv_store.return_policy = (
        "30-day hassle-free returns. Items must be returned with all original accessories and intact packaging."
    )
    dhruv_store.shipping_policy = (
        "Fast express courier dispatch within 24 hours. Free insured delivery across India on prepaid orders."
    )
    
    # Storefront images if missing
    if not dhruv_store.logo:
        img_bytes = get_image("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&q=80")
        if img_bytes:
            dhruv_store.logo.save("dhruv_logo.jpg", ContentFile(img_bytes), save=False)
    if not dhruv_store.banner:
        img_bytes = get_image("https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80")
        if img_bytes:
            dhruv_store.banner.save("dhruv_banner.jpg", ContentFile(img_bytes), save=False)
    dhruv_store.save()
    print("  [OK] Dhruv Vendor & Storefront configured.", flush=True)

    print("\n>>> Setting up Vendor: Sneh...", flush=True)
    sneh_user, _ = User.objects.get_or_create(
        email="sneh@gmail.com",
        defaults={
            "first_name": "Sneh",
            "last_name": "Patel",
            "role": User.Role.VENDOR,
            "is_active": True,
        }
    )
    sneh_user.first_name = "Sneh"
    sneh_user.last_name = "Patel"
    sneh_user.role = User.Role.VENDOR
    sneh_user.save()

    # Check vendor application for Sneh and approve it
    sneh_app = VendorApplication.objects.filter(user=sneh_user).first()
    if sneh_app:
        sneh_vendor = approve_vendor_application(sneh_app, admin_notes="Approved by Administrator.")
    else:
        sneh_vendor, _ = Vendor.objects.get_or_create(
            user=sneh_user,
            defaults={
                "business_name": "Sneh Fashion Hub",
                "business_email": "sneh@gmail.com",
                "phone_number": "+91 87452 13690",
                "is_active": True,
            }
        )

    sneh_vendor.business_name = "Sneh Fashion Hub"
    sneh_vendor.business_email = "sneh@gmail.com"
    sneh_vendor.phone_number = "+91 87452 13690"
    sneh_vendor.is_active = True
    sneh_vendor.save()

    sneh_store, _ = Storefront.objects.get_or_create(vendor=sneh_vendor)
    sneh_store.slug = "sneh-fashion-hub"
    sneh_store.tagline = "Contemporary Apparel, Ethnic Wear, Footwear & Designer Accents"
    sneh_store.description = (
        "Sneh Fashion Hub brings you bespoke contemporary fashion, artisanal festive ethnic attire, "
        "comfort athletic footwear, and aesthetic home textiles crafted for modern elegance."
    )
    sneh_store.return_policy = (
        "15-day exchange and return policy on all unworn apparel and footwear with original security tags."
    )
    sneh_store.shipping_policy = (
        "Dispatched within 24 hours. Standard express shipping delivers in 2-4 business days."
    )
    if not sneh_store.logo:
        img_bytes = get_image("https://images.unsplash.com/photo-1534447677768-be436bb09401?w=400&q=80")
        if img_bytes:
            sneh_store.logo.save("sneh_logo.jpg", ContentFile(img_bytes), save=False)
    if not sneh_store.banner:
        img_bytes = get_image("https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1200&q=80")
        if img_bytes:
            sneh_store.banner.save("sneh_banner.jpg", ContentFile(img_bytes), save=False)
    sneh_store.save()
    print("  [OK] Sneh Vendor & Storefront configured.", flush=True)

    # -------------------------------------------------------------
    # 2. SETUP CATEGORIES
    # -------------------------------------------------------------
    print("\n>>> Setting up Categories & Category Images...")
    categories_spec = [
        # (name, slug, desc, img_url, parent_slug, display_order)
        ("Electronics", "electronics", "Next-generation gadgets, smartphones, computing, acoustics, and smart wearables.", "https://images.unsplash.com/photo-1550009158-9ebf69173e03?w=800&q=80", None, 1),
        ("Clothing", "clothing", "Contemporary fashion, designer apparel, timeless ethnic wear, and footwear.", "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=800&q=80", None, 2),
        ("Home & Kitchen", "home-kitchen", "Ergonomic countertop appliances, cookware, and artisanal living room accents.", "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=800&q=80", None, 3),
        ("Sports", "sports", "High-performance fitness gear, training equipment, and outdoor lifestyle essentials.", "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800&q=80", None, 4),
        ("Books", "books", "Engineering volumes, technical architectural guides, bestsellers, and literature.", "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=800&q=80", None, 5),

        # Subcategories
        ("Smartphones", "smartphones", "Latest flagship 5G smartphones and ultra-portable devices.", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&q=80", "electronics", 1),
        ("Laptops", "laptops", "High-performance workstation and gaming laptops.", "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800&q=80", "electronics", 2),
        ("Audio & Headphones", "audio-headphones", "Studio-grade wireless over-ear headphones and audiophile gear.", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80", "electronics", 3),
        ("Men's Clothing", "mens-clothing", "Premium denim, jackets, casual shirts, and everyday essentials for men.", "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=800&q=80", "clothing", 1),
        ("Women's Apparel", "womens-apparel", "Handcrafted ethnic kurta sets, designer dresses, and festive wear.", "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&q=80", "clothing", 2),
        ("Footwear", "footwear", "Athletic running sneakers, lifestyle footwear, and trainers.", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80", "clothing", 3),
        ("Fashion Accessories", "fashion-accessories", "Hand-stitched leather wallets, belts, and luxury accents.", "https://images.unsplash.com/photo-1627123424574-724758594e93?w=800&q=80", "clothing", 4),
        ("Kitchen Appliances", "kitchen-appliances", "High-speed vortex blenders, juicers, and smart kitchen tools.", "https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=800&q=80", "home-kitchen", 1),
        ("Home Decor", "home-decor", "Ceramic fluted vases, decorative pottery, and woven throw textiles.", "https://images.unsplash.com/photo-1612196808214-b8e1d6145a8c?w=800&q=80", "home-kitchen", 2),
        ("Fitness Equipment", "fitness-equipment", "Hexagonal cast-iron dumbbells and strength training equipment.", "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800&q=80", "sports", 1),
        ("Tech Books", "tech-books", "In-depth guides on Python, cloud computing, and backend architecture.", "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&q=80", "books", 1),
    ]

    cat_map = {}
    for name, slug, desc, img_url, parent_slug, order in categories_spec:
        parent = cat_map.get(parent_slug) if parent_slug else None
        cat, created = Category.objects.get_or_create(slug=slug, defaults={"name": name, "parent": parent})
        cat.name = name
        cat.description = desc
        cat.parent = parent
        cat.display_order = order
        cat.is_active = True
        if not cat.image:
            img_data = get_image(img_url)
            if img_data:
                cat.image.save(f"{slug}.jpg", ContentFile(img_data), save=False)
        cat.save()
        cat_map[slug] = cat
        print(f"  [OK] Category '{name}' ready.", flush=True)

    # -------------------------------------------------------------
    # 3. SETUP TAGS
    # -------------------------------------------------------------
    print("\n>>> Setting up Tags...")
    tag_names = [
        "Electronics", "Gaming", "Audio", "Wireless", "Fitness",
        "Kitchen", "HomeDecor", "Denim", "EthnicWear", "Sneakers",
        "Leather", "Books", "Python", "Bestseller", "EcoFriendly",
        "Luxury", "Handcrafted"
    ]
    tags_map = {}
    for tname in tag_names:
        tslug = slugify(tname)
        tag, _ = Tag.objects.get_or_create(slug=tslug, defaults={"name": tname})
        tags_map[tname] = tag

    # -------------------------------------------------------------
    # 4. PRODUCTS SPECIFICATION: 12 PRODUCTS (6 DHRUV, 6 SNEH)
    # -------------------------------------------------------------
    print("\n>>> Preparing 12 Products across categories...")

    products_spec = [
        # ---------------- VENDOR 1: DHRUV (6 Products) ----------------
        {
            "id": 1,  # Matches existing Product 1
            "vendor": dhruv_vendor,
            "category": cat_map["smartphones"],
            "name": "Ultra Smartphone Pro Max 5G",
            "slug": "ultra-smartphone-pro-max-5g",
            "short_description": "Flagship 5G smartphone featuring 6.7-inch AMOLED 120Hz display, Snapdragon processor, and triple 108MP camera array.",
            "description": (
                "Experience unprecedented speed and performance with the Ultra Smartphone Pro Max 5G. "
                "Engineered with aerospace-grade brushed aluminum and Ceramic Shield scratch-resistant glass, "
                "it features a vibrant 6.7-inch 120Hz LTPO AMOLED display, an all-day 5,000mAh battery with 65W SuperDart fast charging, "
                "and a studio-caliber triple camera system with AI Nightscape vision. Perfect for power users, creators, and mobile gamers."
            ),
            "base_price": Decimal("69999.00"),
            "compare_at_price": Decimal("79999.00"),
            "stock_quantity": 40,
            "sku": "DHR-ELEC-PHN-01",
            "status": Product.Status.ACTIVE,
            "is_featured": True,
            "tags": ["Electronics", "Wireless", "Bestseller"],
            "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=1000&q=80",
            "alt_text": "Ultra Smartphone Pro Max 5G sleek ceramic glass back and camera system",
            "variants": [
                {"name": "Phantom Black / 256GB", "sku": "DHR-ELEC-PHN-01-256B", "price": Decimal("69999.00"), "stock": 25},
                {"name": "Cosmic Silver / 512GB", "sku": "DHR-ELEC-PHN-01-512S", "price": Decimal("75999.00"), "stock": 15},
            ]
        },
        {
            "id": 2,  # Matches existing Product 2
            "vendor": dhruv_vendor,
            "category": cat_map["laptops"],
            "name": "Titan Stealth RTX 16 Gaming Laptop",
            "slug": "titan-stealth-rtx-16-gaming-laptop",
            "short_description": "High-octane 16-inch gaming powerhouse with Intel Core i9, NVIDIA RTX 4080, and 240Hz QHD display.",
            "description": (
                "Unleash extreme computing with the Titan Stealth RTX 16 Laptop. Featuring dual liquid-metal cooling fans, "
                "a calibrated 240Hz QHD IPS matte anti-glare screen, per-key RGB mechanical switches, and Dolby Atmos 4-speaker spatial audio. "
                "With 32GB high-frequency DDR5 memory and 1TB ultra-fast PCIe Gen4 NVMe storage, render 3D scenes or conquer competitive AAA games without frame drops."
            ),
            "base_price": Decimal("114999.00"),
            "compare_at_price": Decimal("129999.00"),
            "stock_quantity": 20,
            "sku": "DHR-ELEC-LAP-02",
            "status": Product.Status.ACTIVE,
            "is_featured": True,
            "tags": ["Gaming", "Electronics", "Bestseller"],
            "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=1000&q=80",
            "alt_text": "Titan Stealth RTX 16 Gaming Laptop open with glowing illuminated keyboard",
            "variants": [
                {"name": "16GB RAM / 1TB SSD", "sku": "DHR-ELEC-LAP-02-16", "price": Decimal("114999.00"), "stock": 12},
                {"name": "32GB RAM / 2TB SSD", "sku": "DHR-ELEC-LAP-02-32", "price": Decimal("132999.00"), "stock": 8},
            ]
        },
        {
            "id": 4,  # Matches existing Product 4
            "vendor": dhruv_vendor,
            "category": cat_map["kitchen-appliances"],
            "name": "Vortex 3000 Smart Countertop Blender",
            "slug": "vortex-3000-smart-countertop-blender",
            "short_description": "1400W commercial-grade vortex blender with 6 touch presets, stainless steel blades, and 2.0L pitcher.",
            "description": (
                "Pulverize whole fruits, tough root vegetables, ice cubes, and nuts into silky smoothies, nut butters, and gourmet soups. "
                "The Vortex 3000 features laser-cut hardened Japanese stainless steel blades, an intuitive digital touchscreen with 6 auto-programs, "
                "variable 10-speed dial, and self-cleaning function. Includes a 2.0L shatterproof BPA-free Tritan jar and custom tamper."
            ),
            "base_price": Decimal("4999.00"),
            "compare_at_price": Decimal("6499.00"),
            "stock_quantity": 35,
            "sku": "DHR-HOME-BLN-03",
            "status": Product.Status.ACTIVE,
            "is_featured": False,
            "tags": ["Kitchen", "EcoFriendly"],
            "image_url": "https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=1000&q=80",
            "alt_text": "Vortex 3000 commercial kitchen blender preparing fresh healthy fruit smoothie",
            "variants": [
                {"name": "Brushed Stainless Steel / 2.0L", "sku": "DHR-HOME-BLN-03-SS", "price": Decimal("4999.00"), "stock": 20},
                {"name": "Matte Obsidian Black / 2.0L", "sku": "DHR-HOME-BLN-03-MB", "price": Decimal("5299.00"), "stock": 15},
            ]
        },
        {
            "id": 5,  # Matches existing Product 5 (keeps review and wishlist intact!)
            "vendor": dhruv_vendor,
            "category": cat_map["tech-books"],
            "name": "Mastering Production Python & Architecture",
            "slug": "mastering-production-python-and-architecture",
            "short_description": "Definitive handbook for architecting scalable cloud-native microservices, databases, and APIs with Python.",
            "description": (
                "Written by principal distributed systems architects, this comprehensive guide takes you deep into asynchronous programming, "
                "database query indexing, Redis caching patterns, Docker orchestration, and high-concurrency API performance optimization. "
                "Packed with 60+ real-world case studies, architectural diagrams, and production-tested battle-hardened designs."
            ),
            "base_price": Decimal("1299.00"),
            "compare_at_price": Decimal("1799.00"),
            "stock_quantity": 75,
            "sku": "DHR-BOOK-PYT-04",
            "status": Product.Status.ACTIVE,
            "is_featured": False,
            "tags": ["Books", "Python", "Bestseller"],
            "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=1000&q=80",
            "alt_text": "Mastering Production Python hardcover book displayed on wooden study desk",
            "variants": [
                {"name": "Paperback Edition", "sku": "DHR-BOOK-PYT-04-PB", "price": Decimal("1299.00"), "stock": 50},
                {"name": "Hardcover Collector Edition", "sku": "DHR-BOOK-PYT-04-HC", "price": Decimal("1899.00"), "stock": 25},
            ]
        },
        {
            "id": 3,  # Upgrades Product 3 into Studio Headphones
            "vendor": dhruv_vendor,
            "category": cat_map["audio-headphones"],
            "name": "AcousticPro ANC Studio Wireless Headphones",
            "slug": "acousticpro-anc-studio-wireless-headphones",
            "short_description": "Active Noise-Cancelling over-ear headphones with 40mm custom beryllium drivers and 45-hour battery life.",
            "description": (
                "Escape ambient distractions and enjoy audiophile clarity with AcousticPro Studio Wireless. "
                "Features hybrid 4-microphone active noise cancellation that neutralizes 98% of background noise, multipoint Bluetooth 5.3, "
                "ultra-low latency gaming mode, and memory-foam protein leather ear cushions that stay comfortable during marathon sessions. "
                "USB-C fast charging provides 5 hours of playback in just 10 minutes."
            ),
            "base_price": Decimal("5499.00"),
            "compare_at_price": Decimal("7999.00"),
            "stock_quantity": 50,
            "sku": "DHR-ELEC-AUD-05",
            "status": Product.Status.ACTIVE,
            "is_featured": True,
            "tags": ["Audio", "Wireless", "Electronics"],
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=1000&q=80",
            "alt_text": "AcousticPro Studio Wireless over-ear headphones in matte carbon black",
            "variants": [
                {"name": "Midnight Carbon", "sku": "DHR-ELEC-AUD-05-MC", "price": Decimal("5499.00"), "stock": 30},
                {"name": "Ivory Gold", "sku": "DHR-ELEC-AUD-05-IG", "price": Decimal("5799.00"), "stock": 20},
            ]
        },
        {
            "id": None,  # Brand new 6th product for Dhruv
            "vendor": dhruv_vendor,
            "category": cat_map["fitness-equipment"],
            "name": "IronPulse Hexagonal Cast Iron Dumbbells (Pair)",
            "slug": "ironpulse-hexagonal-cast-iron-dumbbells-pair",
            "short_description": "Anti-roll rubber-encased hexagonal solid cast iron dumbbell pair with knurled ergonomic chrome handles.",
            "description": (
                "Built to withstand punishing daily strength routines, the IronPulse Hex Dumbbells feature solid cast iron heads "
                "permanently welded to ergonomic knurled chrome steel handles. Encased in odorless heavy-duty virgin rubber that protects flooring, "
                "muffles impact noise, and prevents rolling. Ideal for presses, deadlifts, squats, and functional CrossFit workouts."
            ),
            "base_price": Decimal("3499.00"),
            "compare_at_price": Decimal("4499.00"),
            "stock_quantity": 30,
            "sku": "DHR-SPOR-FIT-06",
            "status": Product.Status.ACTIVE,
            "is_featured": False,
            "tags": ["Fitness", "Bestseller"],
            "image_url": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=1000&q=80",
            "alt_text": "Pair of heavy duty black rubber hex dumbbells sitting on gym floor mat",
            "variants": [
                {"name": "Pair of 10 KG", "sku": "DHR-SPOR-FIT-06-10", "price": Decimal("3499.00"), "stock": 15},
                {"name": "Pair of 15 KG", "sku": "DHR-SPOR-FIT-06-15", "price": Decimal("4999.00"), "stock": 15},
            ]
        },

        # ---------------- VENDOR 2: SNEH (6 Products) ----------------
        {
            "id": None,
            "vendor": sneh_vendor,
            "category": cat_map["womens-apparel"],
            "name": "Royal Heritage Chanderi Silk Anarkali Set",
            "slug": "royal-heritage-chanderi-silk-anarkali-set",
            "short_description": "Handcrafted 3-piece pure Chanderi silk kurta set with intricate Zari needlework, palazzo, and organza dupatta.",
            "description": (
                "Exude regal sophistication at festivals and weddings in this 3-piece handcrafted designer ensemble. "
                "Spun from pure breathable Chanderi silk with delicate golden Zari embroidery across the neckline and cuffs. "
                "Includes matching tailored silk palazzo pants with elasticized waistband and a lightweight scalloped sheer organza dupatta."
            ),
            "base_price": Decimal("3899.00"),
            "compare_at_price": Decimal("5299.00"),
            "stock_quantity": 45,
            "sku": "SNE-CLTH-ETH-01",
            "status": Product.Status.ACTIVE,
            "is_featured": True,
            "tags": ["EthnicWear", "Handcrafted", "Luxury"],
            "image_url": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=1000&q=80",
            "alt_text": "Traditional pure silk embroidered ethnic attire with matching dupatta",
            "variants": [
                {"name": "Size M / Royal Emerald", "sku": "SNE-CLTH-ETH-01-M-EM", "price": Decimal("3899.00"), "stock": 25},
                {"name": "Size L / Royal Emerald", "sku": "SNE-CLTH-ETH-01-L-EM", "price": Decimal("3899.00"), "stock": 20},
            ]
        },
        {
            "id": None,
            "vendor": sneh_vendor,
            "category": cat_map["mens-clothing"],
            "name": "Classic Vintage Indigo Selvedge Denim Trucker Jacket",
            "slug": "classic-vintage-indigo-selvedge-denim-trucker-jacket",
            "short_description": "Heavyweight 14oz 100% cotton selvedge denim jacket with custom antique brass buttons and relaxed fit.",
            "description": (
                "A timeless outerwear silhouette built for lasting comfort. Loomed from 14oz ring-spun authentic indigo selvedge denim, "
                "this jacket features felled double-needle stitching, dual button-flap chest pockets, welt hand pockets, and adjustable waist tabs. "
                "Pre-washed for instant softness while naturally fading and developing a personalized vintage patina over years of wear."
            ),
            "base_price": Decimal("2999.00"),
            "compare_at_price": Decimal("3999.00"),
            "stock_quantity": 50,
            "sku": "SNE-CLTH-DEN-02",
            "status": Product.Status.ACTIVE,
            "is_featured": True,
            "tags": ["Denim", "Luxury"],
            "image_url": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=1000&q=80",
            "alt_text": "Classic vintage washed indigo blue denim trucker jacket on hanger",
            "variants": [
                {"name": "Size M / Washed Indigo", "sku": "SNE-CLTH-DEN-02-M", "price": Decimal("2999.00"), "stock": 25},
                {"name": "Size L / Washed Indigo", "sku": "SNE-CLTH-DEN-02-L", "price": Decimal("2999.00"), "stock": 25},
            ]
        },
        {
            "id": None,
            "vendor": sneh_vendor,
            "category": cat_map["footwear"],
            "name": "Aeroknit CloudStep Cushioned Running Sneakers",
            "slug": "aeroknit-cloudstep-cushioned-running-sneakers",
            "short_description": "Ultra-lightweight breathable knit athletic running shoes with high-rebound EVA cushioning and memory foam insole.",
            "description": (
                "Step into effortless comfort with the Aeroknit CloudStep sneakers. Engineered with an adaptive one-piece flyknit mesh upper "
                "that promotes maximum airflow, a sculpted high-rebound EVA midsole that absorbs road impact, and an orthotic memory foam insole. "
                "Finished with a grooved rubber outsole delivering multi-surface grip for 10K runs, gym training, or daily commutes."
            ),
            "base_price": Decimal("2799.00"),
            "compare_at_price": Decimal("3899.00"),
            "stock_quantity": 60,
            "sku": "SNE-FOOT-SNK-03",
            "status": Product.Status.ACTIVE,
            "is_featured": False,
            "tags": ["Sneakers", "Fitness"],
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=1000&q=80",
            "alt_text": "Sporty modern lightweight red and white running athletic sneakers",
            "variants": [
                {"name": "UK 8 / Crimson Red & White", "sku": "SNE-FOOT-SNK-03-08R", "price": Decimal("2799.00"), "stock": 30},
                {"name": "UK 9 / Crimson Red & White", "sku": "SNE-FOOT-SNK-03-09R", "price": Decimal("2799.00"), "stock": 30},
            ]
        },
        {
            "id": None,
            "vendor": sneh_vendor,
            "category": cat_map["fashion-accessories"],
            "name": "Artisan Handcrafted Full-Grain Leather Wallet",
            "slug": "artisan-handcrafted-full-grain-leather-wallet",
            "short_description": "Slim RFID-blocking bi-fold wallet meticulously crafted from vegetable-tanned full-grain top layer leather.",
            "description": (
                "Distinguished by artisanal hand-stitching and premium full-grain saddle leather that ages gracefully over time. "
                "Includes 8 precision card slots, 2 hidden document slip pockets, and a full-size bill divider. "
                "Features military-grade RFID-blocking inner lining to shield credit cards and passports from contactless skimming."
            ),
            "base_price": Decimal("1499.00"),
            "compare_at_price": Decimal("2199.00"),
            "stock_quantity": 70,
            "sku": "SNE-ACCS-WAL-04",
            "status": Product.Status.ACTIVE,
            "is_featured": False,
            "tags": ["Leather", "Handcrafted", "Luxury"],
            "image_url": "https://images.unsplash.com/photo-1627123424574-724758594e93?w=1000&q=80",
            "alt_text": "Handcrafted brown full-grain leather wallet laid open on stone surface",
            "variants": [
                {"name": "Cognac Amber Leather", "sku": "SNE-ACCS-WAL-04-CA", "price": Decimal("1499.00"), "stock": 40},
                {"name": "Espresso Dark Brown", "sku": "SNE-ACCS-WAL-04-EB", "price": Decimal("1499.00"), "stock": 30},
            ]
        },
        {
            "id": None,
            "vendor": sneh_vendor,
            "category": cat_map["home-decor"],
            "name": "Minimalist Fluted Ceramic Decorative Vase Set",
            "slug": "minimalist-fluted-ceramic-decorative-vase-set",
            "short_description": "Set of 2 matte glazed textural ribbed ceramic vases designed for dried pampas florals and table decor.",
            "description": (
                "Infuse Scandinavian warmth and sculptural elegance into your dining table, bookshelf, or mantel. "
                "Handcrafted from high-fire stoneware clay with a distinctive fluted vertical ribbed texture and matte chalk-white glaze. "
                "Waterproof interior makes it equally suited for freshly clipped seasonal floral stems or dried pampas grass."
            ),
            "base_price": Decimal("1399.00"),
            "compare_at_price": Decimal("1899.00"),
            "stock_quantity": 40,
            "sku": "SNE-HOME-VAS-05",
            "status": Product.Status.ACTIVE,
            "is_featured": False,
            "tags": ["HomeDecor", "Handcrafted", "EcoFriendly"],
            "image_url": "https://images.unsplash.com/photo-1612196808214-b8e1d6145a8c?w=1000&q=80",
            "alt_text": "Minimalist ceramic ribbed decorative flower vase on wooden table",
            "variants": [
                {"name": "Set of 2 / Chalk White", "sku": "SNE-HOME-VAS-05-CW", "price": Decimal("1399.00"), "stock": 25},
                {"name": "Set of 2 / Terracotta Blush", "sku": "SNE-HOME-VAS-05-TB", "price": Decimal("1499.00"), "stock": 15},
            ]
        },
        {
            "id": None,
            "vendor": sneh_vendor,
            "category": cat_map["home-decor"],
            "name": "Bohemian Woven Cotton Throw Blanket with Tassels",
            "slug": "bohemian-woven-cotton-throw-blanket-with-tassels",
            "short_description": "100% natural breathable woven cotton throw blanket (130x170cm) with geometric herringbone patterns and fringed edges.",
            "description": (
                "Drape your sofa or bedroom in cozy artisan texture. Hand-loomed from 100% combed Turkish natural cotton yarns, "
                "this versatile throw blanket features a reversible geometric jacquard herringbone weave and hand-knotted tassel fringe trim. "
                "Pre-washed for luxurious cloud-soft touch that stays durable through regular machine cycles without pilling."
            ),
            "base_price": Decimal("1899.00"),
            "compare_at_price": Decimal("2599.00"),
            "stock_quantity": 35,
            "sku": "SNE-HOME-THR-06",
            "status": Product.Status.ACTIVE,
            "is_featured": True,
            "tags": ["HomeDecor", "Handcrafted", "Bestseller"],
            "image_url": "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=1000&q=80",
            "alt_text": "Cozy mustard and cream bohemian woven cotton throw blanket folded on armchair",
            "variants": [
                {"name": "Mustard Gold & Cream (130x170cm)", "sku": "SNE-HOME-THR-06-MG", "price": Decimal("1899.00"), "stock": 20},
                {"name": "Sage Green & Cream (130x170cm)", "sku": "SNE-HOME-THR-06-SG", "price": Decimal("1899.00"), "stock": 15},
            ]
        },
    ]

    # Save and verify every product
    for idx, pspec in enumerate(products_spec, 1):
        pid = pspec.get("id")
        prod = None
        if pid:
            prod = Product.objects.filter(id=pid).first()

        if not prod:
            prod = Product(
                vendor=pspec["vendor"],
                name=pspec["name"],
                slug=pspec["slug"]
            )

        prod.vendor = pspec["vendor"]
        prod.category = pspec["category"]
        prod.name = pspec["name"]
        prod.slug = pspec["slug"]
        prod.short_description = pspec["short_description"]
        prod.description = pspec["description"]
        prod.base_price = pspec["base_price"]
        prod.compare_at_price = pspec["compare_at_price"]
        prod.stock_quantity = pspec["stock_quantity"]
        prod.sku = pspec["sku"]
        prod.status = pspec["status"]
        prod.is_featured = pspec["is_featured"]
        prod.save()

        # Set Tags
        prod.tags.clear()
        for tname in pspec["tags"]:
            tag_obj = tags_map.get(tname)
            if tag_obj:
                prod.tags.add(tag_obj)

        # Set Product Image
        # Clear existing images for this product if placeholder or dummy
        prod.images.all().delete()
        img_data = get_image(pspec["image_url"])
        if img_data:
            pimg = ProductImage(
                product=prod,
                alt_text=pspec["alt_text"],
                is_primary=True,
                display_order=1
            )
            pimg.image.save(f"{prod.slug}-main.jpg", ContentFile(img_data), save=True)
            print(f"  [OK] Product {idx}/12: '{prod.name}' saved with image ({len(img_data)} bytes).", flush=True)
        else:
            print(f"  [WARN] Product {idx}/12: '{prod.name}' saved WITHOUT image!", flush=True)

        # Set Product Variants
        prod.variants.all().delete()
        for var_spec in pspec["variants"]:
            ProductVariant.objects.create(
                product=prod,
                name=var_spec["name"],
                sku=var_spec["sku"],
                price_override=var_spec["price"],
                stock_quantity=var_spec["stock"],
                is_active=True
            )

    print("\n" + "=" * 60)
    print("Database Population Complete! Running Verification Checks...")
    print("=" * 60)

    # Verification
    total_products = Product.objects.count()
    dhruv_prods = Product.objects.filter(vendor=dhruv_vendor).count()
    sneh_prods = Product.objects.filter(vendor=sneh_vendor).count()
    print(f"Total Products in DB: {total_products}")
    print(f"  - Dhruv's Products: {dhruv_prods}")
    print(f"  - Sneh's Products:  {sneh_prods}")

    # Column completeness check
    missing_fields_found = False
    for p in Product.objects.all():
        missing = []
        if not p.vendor_id: missing.append("vendor")
        if not p.category_id: missing.append("category")
        if not p.name: missing.append("name")
        if not p.slug: missing.append("slug")
        if not p.description: missing.append("description")
        if not p.short_description: missing.append("short_description")
        if p.base_price is None: missing.append("base_price")
        if p.compare_at_price is None: missing.append("compare_at_price")
        if p.stock_quantity is None: missing.append("stock_quantity")
        if not p.sku: missing.append("sku")
        if not p.status: missing.append("status")
        if p.images.count() == 0: missing.append("no_images")
        if p.variants.count() == 0: missing.append("no_variants")
        if p.tags.count() == 0: missing.append("no_tags")

        if missing:
            missing_fields_found = True
            print(f"  [FAIL] Product '{p.name}' missing columns: {missing}")
        else:
            print(f"  [PASS] Product #{p.id} '{p.name}' -> Vendor: {p.vendor.business_name} | Cat: {p.category.name} | Base: INR {p.base_price} | Compare: INR {p.compare_at_price} | SKU: {p.sku} | Images: {p.images.count()} | Variants: {p.variants.count()} | Tags: {p.tags.count()}", flush=True)

    if not missing_fields_found:
        print("\n>>> ALL 12 PRODUCTS HAVE ZERO EMPTY COLUMNS! All images, variants, and tags properly saved. <<<")

if __name__ == "__main__":
    run()

from django.utils import timezone
from django.utils.text import slugify

from .models import VendorApplication, Vendor, Storefront


def approve_vendor_application(application, admin_notes=""):
    """
    Approve a vendor application:
    1. Update application status to APPROVED
    2. Create Vendor record
    3. Update user role to VENDOR
    4. Auto-create Storefront with slugified business name
    """
    application.status = VendorApplication.Status.APPROVED
    application.admin_notes = admin_notes
    application.reviewed_at = timezone.now()
    application.save()

    # Create Vendor record
    vendor, created = Vendor.objects.get_or_create(
        user=application.user,
        defaults={
            "business_name": application.business_name,
            "business_email": application.business_email,
            "phone_number": application.phone_number,
        },
    )

    # Update user role
    user = application.user
    user.role = "VENDOR"
    user.save(update_fields=["role"])

    # Create Storefront
    if not hasattr(vendor, "storefront"):
        Storefront.objects.create(vendor=vendor)

    # In-app notification
    try:
        from apps.notifications.models import Notification
        Notification.objects.create(
            user=user,
            title="Vendor Application Approved! 🎉",
            message=f"Congratulations! Your application for '{application.business_name}' has been approved. You can now access your Seller Dashboard.",
            link="/vendors/dashboard/",
        )
    except Exception:
        pass

    return vendor


def reject_vendor_application(application, admin_notes=""):
    """
    Reject a vendor application with optional notes.
    """
    application.status = VendorApplication.Status.REJECTED
    application.admin_notes = admin_notes
    application.reviewed_at = timezone.now()
    application.save()

    # In-app notification
    try:
        from apps.notifications.models import Notification
        msg = f"Your application for '{application.business_name}' was not approved."
        if admin_notes:
            msg += f" Note: {admin_notes}"
        Notification.objects.create(
            user=application.user,
            title="Vendor Application Update",
            message=msg,
            link="/help/",
        )
    except Exception:
        pass

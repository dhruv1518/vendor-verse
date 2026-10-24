import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Task 38 — Simple Email Notifications
# ---------------------------------------------------------------------------

def _safe_text(text):
    if not text:
        return ""
    # Clean non-ascii/emojis that crash Windows cp1252 console email backend
    return text.encode("ascii", "replace").decode("ascii")


def send_welcome_email(user):
    """
    Send a welcome email when a new user registers.
    Uses Django's console email backend in development.
    """
    subject = _safe_text("Welcome to Vendora! 🎉")
    html_message = render_to_string("emails/welcome.html", {
        "user": user,
        "site_name": "Vendora",
    })
    plain_message = _safe_text(strip_tags(html_message))

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Welcome email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {e}")


def send_order_confirmation_email(order):
    """
    Send an order confirmation email after a successful payment.
    Includes order number, items summary, and total.
    """
    subject = _safe_text(f"Order Confirmed — {order.order_number} | Vendora")
    html_message = render_to_string("emails/order_confirmation.html", {
        "order": order,
        "order_items": order.items.select_related("vendor", "product"),
        "site_name": "Vendora",
    })
    plain_message = _safe_text(strip_tags(html_message))

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Order confirmation email sent for {order.order_number} to {order.user.email}")
    except Exception as e:
        logger.error(f"Failed to send order confirmation email for {order.order_number}: {e}")


def send_vendor_new_order_email(vendor, order, vendor_items):
    """
    Notify a vendor that they have a new order with their items.
    """
    subject = _safe_text(f"New Order Received — {order.order_number} | Vendora")
    html_message = render_to_string("emails/vendor_new_order.html", {
        "vendor": vendor,
        "order": order,
        "items": vendor_items,
        "site_name": "Vendora",
    })
    plain_message = _safe_text(strip_tags(html_message))

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[vendor.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Vendor order notification sent to {vendor.user.email} for {order.order_number}")
    except Exception as e:
        logger.error(f"Failed to send vendor notification to {vendor.user.email}: {e}")

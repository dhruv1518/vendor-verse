"""
AI Chatbot views for VendorVerse.

Single endpoint that dynamically switches between:
- Global mode (no storefront_slug)
- Storefront mode (storefront_slug present)
- Product mode (storefront_slug + product_slug present)
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .gemini_client import get_gemini_response, is_gemini_configured
from .context_builders import (
    build_global_context,
    build_storefront_context,
    build_product_context,
)
from .rate_limiter import check_rate_limit, record_request

logger = logging.getLogger(__name__)


@require_POST
def chat_message(request):
    """
    Main chatbot endpoint.

    Expects JSON body:
    {
        "message": "user's question",
        "storefront_slug": "optional-vendor-slug",   // null for global mode
        "product_slug": "optional-product-slug",      // null unless on product page
    }

    Returns JSON:
    {
        "reply": "AI response text",
        "mode": "global" | "storefront" | "product",
        "error": false
    }
    """
    # Check if Gemini is configured
    if not is_gemini_configured():
        return JsonResponse({
            "reply": "AI assistant is not available. The API key has not been configured.",
            "mode": "global",
            "error": True,
        })

    # Parse request body
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({
            "reply": "Invalid request format.",
            "mode": "global",
            "error": True,
        }, status=400)

    user_message = data.get("message", "").strip()
    storefront_slug = data.get("storefront_slug") or None
    product_slug = data.get("product_slug") or None

    if not user_message:
        return JsonResponse({
            "reply": "Please type a message! 😊",
            "mode": "global",
            "error": False,
        })

    # Truncate excessively long messages (prevent token waste)
    if len(user_message) > 500:
        user_message = user_message[:500]

    # --- Rate Limiting (Safety Net) ---
    allowed, limit_message = check_rate_limit(request.session)
    if not allowed:
        return JsonResponse({
            "reply": limit_message,
            "mode": "global",
            "error": False,
        })

    # --- Determine Mode & Build Context ---
    if storefront_slug and product_slug:
        mode = "product"
        system_prompt = build_product_context(storefront_slug, product_slug, user_message)
    elif storefront_slug:
        mode = "storefront"
        system_prompt = build_storefront_context(storefront_slug, user_message)
    else:
        mode = "global"
        system_prompt = build_global_context(user_message)

    # --- Retrieve Conversation History from Session ---
    # Use separate history keys for different contexts to avoid cross-contamination
    if storefront_slug:
        history_key = f"chat_history_{storefront_slug}"
    else:
        history_key = "chat_history_global"

    history = request.session.get(history_key, [])

    # --- Call Gemini API ---
    reply = get_gemini_response(system_prompt, user_message, history)

    # --- Record the API call (for rate limiting) ---
    record_request(request.session)

    # --- Save Conversation History ---
    history.append({"role": "user", "text": user_message})
    history.append({"role": "model", "text": reply})
    # Keep only last 10 messages (5 turns) to save session space & tokens
    request.session[history_key] = history[-10:]
    request.session.modified = True

    return JsonResponse({
        "reply": reply,
        "mode": mode,
        "error": False,
    })


def chat_status(request):
    """
    Simple GET endpoint to check if the chatbot is available.
    Used by the frontend to decide whether to show the chatbot widget.
    """
    return JsonResponse({
        "available": is_gemini_configured(),
    })

"""
Rate limiter and free-tier safety net for VendorVerse AI chatbot.

THREE LAYERS OF PROTECTION:
1. Per-session rate limit: Max 20 messages/hour per user
2. Global daily counter: Hard stops at 1,400 requests/day (free limit is 1,500)
3. Graceful fallback: Returns friendly message instead of making API call

This ensures you NEVER get charged — the free tier can't auto-bill anyway,
but this prevents even hitting the API rate limits.
"""

import time
from django.core.cache import cache

# ----- Configuration -----
MAX_MESSAGES_PER_HOUR = 20        # Per user/session
MAX_DAILY_REQUESTS = 1400         # Global daily limit (free tier = 1,500 RPD)
DAILY_COUNTER_KEY = "ai_daily_request_count"
DAILY_COUNTER_DATE_KEY = "ai_daily_request_date"


def _get_session_key(session):
    """Get a unique key for rate-limiting this session."""
    if not session.session_key:
        session.create()
    return f"ai_rate_{session.session_key}"


def check_rate_limit(session):
    """
    Check if this session is allowed to make another AI request.

    Returns:
        tuple: (allowed: bool, error_message: str or None)
    """
    # --- Layer 1: Per-session rate limit ---
    session_key = _get_session_key(session)
    session_data = cache.get(session_key)

    if session_data is None:
        session_data = {"count": 0, "window_start": time.time()}

    # Reset window if an hour has passed
    elapsed = time.time() - session_data["window_start"]
    if elapsed > 3600:  # 1 hour
        session_data = {"count": 0, "window_start": time.time()}

    if session_data["count"] >= MAX_MESSAGES_PER_HOUR:
        minutes_left = int((3600 - elapsed) / 60)
        return False, (
            f"You've sent a lot of messages! 😊 "
            f"Please wait about {minutes_left} minute{'s' if minutes_left != 1 else ''} "
            f"before sending more. This helps keep the AI free for everyone."
        )

    # --- Layer 2: Global daily counter ---
    from datetime import date
    today = date.today().isoformat()
    stored_date = cache.get(DAILY_COUNTER_DATE_KEY)
    daily_count = cache.get(DAILY_COUNTER_KEY, 0)

    # Reset counter if it's a new day
    if stored_date != today:
        daily_count = 0
        cache.set(DAILY_COUNTER_DATE_KEY, today, timeout=86400)
        cache.set(DAILY_COUNTER_KEY, 0, timeout=86400)

    if daily_count >= MAX_DAILY_REQUESTS:
        return False, (
            "I've reached my daily limit 😅 The AI assistant has a free-tier usage "
            "cap to keep costs at zero. Please try again tomorrow!"
        )

    return True, None


def record_request(session):
    """
    Record that a request was made (call AFTER successful API response).
    """
    # Update session counter
    session_key = _get_session_key(session)
    session_data = cache.get(session_key)
    if session_data is None:
        session_data = {"count": 0, "window_start": time.time()}

    elapsed = time.time() - session_data["window_start"]
    if elapsed > 3600:
        session_data = {"count": 1, "window_start": time.time()}
    else:
        session_data["count"] += 1

    cache.set(session_key, session_data, timeout=3600)

    # Update global daily counter
    daily_count = cache.get(DAILY_COUNTER_KEY, 0)
    cache.set(DAILY_COUNTER_KEY, daily_count + 1, timeout=86400)

"""
Rate limiter and free-tier safety net for VendorVerse AI chatbot.

MULTI-TIER PROTECTION FOR GOOGLE GEMINI FREE TIER:
1. Per-Minute Throttle (RPM Protection):
   - Google free tier limit: 15 Requests Per Minute (RPM)
   - Safety cap: 10 requests / minute globally across all users.
   - Prevents spike traffic or rapid double-clicks from triggering 429 errors.

2. Global Daily Hard Cap (RPD Protection):
   - Google free tier limit: 1,500 Requests Per Day (RPD)
   - Safety cap: Default 500 requests / day (or configurable via GEMINI_DAILY_LIMIT in .env).
   - Keeps a massive safety buffer (1,000 requests) so you never risk exceeding limits or unexpected charges.

3. Persistent Tracking Across Server Restarts:
   - Daily counter is stored in both cache and a persistent JSON state file (`.ai_quota_state.json`).
   - Server reloads, background workers, or restarts will NEVER reset today's count back to 0.

4. Emergency Circuit Breaker:
   - If Google ever returns a 429 / Quota / Resource Exhausted error, the breaker trips instantly.
   - All subsequent calls are blocked immediately until the next calendar day or cooldown period,
     preventing failed retry storms and protecting the API key from suspension.

5. Per-Session Rate Limiting:
   - Max 15 messages/hour per user session so no single visitor monopolizes the platform quota.
"""

import os
import json
import time
import logging
from datetime import date, datetime
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# ----- Limits & Configuration -----
# Per user session hourly limit
MAX_MESSAGES_PER_HOUR = getattr(settings, "GEMINI_USER_HOURLY_LIMIT", 15)

# Global daily limit (Free tier is 1,500/day. Default safety net is 500/day to stay 100% safe)
MAX_DAILY_REQUESTS = int(getattr(settings, "GEMINI_DAILY_LIMIT", 500))

# Global requests per minute limit (Free tier is 15 RPM. Safety cap is 10 RPM)
MAX_RPM = int(getattr(settings, "GEMINI_RPM_LIMIT", 10))

# Storage keys
DAILY_COUNTER_KEY = "ai_daily_request_count"
DAILY_COUNTER_DATE_KEY = "ai_daily_request_date"
RPM_TIMESTAMPS_KEY = "ai_rpm_timestamps"
CIRCUIT_BREAKER_KEY = "ai_circuit_breaker_tripped"

STATE_FILE_PATH = os.path.join(getattr(settings, "BASE_DIR", "."), ".ai_quota_state.json")


def _load_state_file():
    """Load persistent quota state from disk."""
    today = date.today().isoformat()
    default_state = {
        "date": today,
        "daily_count": 0,
        "circuit_breaker_tripped": False,
        "trip_reason": None,
        "last_trip_time": None,
    }
    if not os.path.exists(STATE_FILE_PATH):
        return default_state

    try:
        with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # If the file is from a previous day, roll over to today
            if data.get("date") != today:
                default_state["date"] = today
                _save_state_file(default_state)
                return default_state
            return data
    except Exception as e:
        logger.warning("Could not read AI quota state file: %s", str(e))
        return default_state


def _save_state_file(state):
    """Save persistent quota state to disk atomically."""
    try:
        tmp_path = STATE_FILE_PATH + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        if os.path.exists(tmp_path):
            os.replace(tmp_path, STATE_FILE_PATH)
    except Exception as e:
        logger.warning("Could not save AI quota state file: %s", str(e))


def _get_session_key(session):
    """Get a unique key for rate-limiting this session."""
    if not session.session_key:
        session.create()
    return f"ai_rate_{session.session_key}"


def check_rate_limit(session):
    """
    Check if this session is allowed to make another AI request.
    Evaluates:
    1. Circuit breaker status
    2. Global daily limit
    3. Global requests-per-minute (RPM) throttle
    4. Per-user session hourly limit

    Returns:
        tuple: (allowed: bool, message: str or None)
    """
    today = date.today().isoformat()
    state = _load_state_file()

    # 1. Circuit Breaker Check
    if state.get("circuit_breaker_tripped") and state.get("date") == today:
        return False, (
            "I've reached my daily limit 😅 The AI assistant is on a free-tier usage cap "
            "to ensure zero unexpected charges. Please check back tomorrow! 🙏"
        )

    # 2. Global Daily Limit Check
    daily_count = state.get("daily_count", 0)
    if daily_count >= MAX_DAILY_REQUESTS:
        return False, (
            f"Daily AI safety cap reached ({MAX_DAILY_REQUESTS} requests today) 🛡️. "
            "To prevent over-quota charges on the free tier, the assistant is taking a break until tomorrow!"
        )

    # 3. Global Requests-Per-Minute (RPM) Throttle (buffer against Google's 15 RPM limit)
    now = time.time()
    rpm_timestamps = cache.get(RPM_TIMESTAMPS_KEY, [])
    valid_timestamps = [t for t in rpm_timestamps if now - t < 60]
    if len(valid_timestamps) >= MAX_RPM:
        return False, (
            "The AI assistant is receiving a lot of questions right now! ⏳ "
            "Please wait about 15-20 seconds and try again."
        )

    # 4. Per-User Session Hourly Limit
    session_key = _get_session_key(session)
    session_data = cache.get(session_key)
    if session_data is None:
        session_data = {"count": 0, "window_start": now}

    elapsed = now - session_data["window_start"]
    if elapsed > 3600:
        session_data = {"count": 0, "window_start": now}

    if session_data["count"] >= MAX_MESSAGES_PER_HOUR:
        minutes_left = max(1, int((3600 - elapsed) / 60))
        return False, (
            f"You've sent quite a few messages! 😊 "
            f"Please wait about {minutes_left} minute{'s' if minutes_left != 1 else ''} "
            f"before sending more so everyone can use the free AI assistant."
        )

    return True, None


def record_request(session):
    """
    Record that a request was successfully completed.
    Updates session counter, global RPM timestamps, and persistent daily state.
    """
    now = time.time()
    today = date.today().isoformat()

    # 1. Update session counter
    session_key = _get_session_key(session)
    session_data = cache.get(session_key)
    if session_data is None:
        session_data = {"count": 0, "window_start": now}

    elapsed = now - session_data["window_start"]
    if elapsed > 3600:
        session_data = {"count": 1, "window_start": now}
    else:
        session_data["count"] += 1
    cache.set(session_key, session_data, timeout=3600)

    # 2. Update RPM timestamps
    rpm_timestamps = cache.get(RPM_TIMESTAMPS_KEY, [])
    valid_timestamps = [t for t in rpm_timestamps if now - t < 60]
    valid_timestamps.append(now)
    cache.set(RPM_TIMESTAMPS_KEY, valid_timestamps, timeout=120)

    # 3. Update persistent global daily state
    state = _load_state_file()
    if state.get("date") != today:
        state["date"] = today
        state["daily_count"] = 0
        state["circuit_breaker_tripped"] = False
        state["trip_reason"] = None

    state["daily_count"] = state.get("daily_count", 0) + 1
    _save_state_file(state)
    cache.set(DAILY_COUNTER_KEY, state["daily_count"], timeout=86400)


def trip_circuit_breaker(reason="Google Free Tier quota limit reached"):
    """
    Immediately trips the circuit breaker to block all subsequent API requests.
    Prevents repeated 429 errors or account suspension.
    """
    today = date.today().isoformat()
    state = _load_state_file()
    state["date"] = today
    state["circuit_breaker_tripped"] = True
    state["trip_reason"] = reason
    state["last_trip_time"] = datetime.now().isoformat()
    _save_state_file(state)
    cache.set(CIRCUIT_BREAKER_KEY, True, timeout=86400)
    logger.error("AI Circuit Breaker TRIPPED: %s", reason)


def reset_daily_quota():
    """Admin/testing utility to reset daily quota and reset circuit breaker."""
    today = date.today().isoformat()
    state = {
        "date": today,
        "daily_count": 0,
        "circuit_breaker_tripped": False,
        "trip_reason": None,
        "last_trip_time": None,
    }
    _save_state_file(state)
    cache.set(DAILY_COUNTER_KEY, 0, timeout=86400)
    cache.set(CIRCUIT_BREAKER_KEY, False, timeout=86400)
    cache.delete(RPM_TIMESTAMPS_KEY)


def get_quota_status():
    """
    Returns current live status of the AI free-tier quota and safety nets.
    """
    now = time.time()
    state = _load_state_file()
    daily_count = state.get("daily_count", 0)
    rpm_timestamps = cache.get(RPM_TIMESTAMPS_KEY, [])
    rpm_count = len([t for t in rpm_timestamps if now - t < 60])

    return {
        "date": state.get("date"),
        "daily_count": daily_count,
        "daily_limit": MAX_DAILY_REQUESTS,
        "daily_remaining": max(0, MAX_DAILY_REQUESTS - daily_count),
        "rpm_count": rpm_count,
        "rpm_limit": MAX_RPM,
        "circuit_breaker_tripped": state.get("circuit_breaker_tripped", False),
        "trip_reason": state.get("trip_reason"),
    }


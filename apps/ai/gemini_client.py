"""
Gemini API client wrapper for Vendora.

Uses the newer `google-genai` package (lighter, faster install).
Install: pip install google-genai

SECURITY:
- API key is read from settings.GEMINI_API_KEY (which reads from .env)
- The key NEVER appears in source code or templates
- All API calls happen server-side only — the browser never sees the key
"""

import logging

from google import genai
from google.genai import types
from django.conf import settings

logger = logging.getLogger(__name__)

# Primary model and fallbacks for high availability
GEMINI_MODELS = ["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.8-flash"]


def is_gemini_configured():
    """Check if the Gemini API key is set. Used to hide the chatbot if not configured."""
    return bool(getattr(settings, "GEMINI_API_KEY", ""))


def get_gemini_response(system_prompt, user_message, conversation_history=None):
    """
    Send a message to Gemini with a system prompt and conversation history.

    Args:
        system_prompt: The system-level instructions (global vs storefront context)
        user_message: The latest user message
        conversation_history: List of {"role": "user"/"model", "text": "..."} dicts

    Returns:
        str: The AI response text, or an error message if something goes wrong
    """
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key:
        return "AI assistant is not configured. Please set up the Gemini API key."

    try:
        client = genai.Client(api_key=api_key)

        # Build conversation contents for multi-turn chat
        contents = []
        if conversation_history:
            for msg in conversation_history:
                contents.append({
                    "role": msg["role"],
                    "parts": [{"text": msg["text"]}]
                })

        # Add the current user message
        contents.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })

        last_error = None
        for model_name in GEMINI_MODELS:
            try:
                config_kwargs = {
                    "system_instruction": system_prompt,
                    "max_output_tokens": 2048,
                    "temperature": 0.7,
                }
                # thinking_config is only valid for reasoning models (e.g., gemini-3.6-flash, gemini-3.8-flash)
                if "flash-lite" not in model_name:
                    try:
                        config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
                    except Exception:
                        pass

                config = types.GenerateContentConfig(**config_kwargs)

                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )

                reply_text = ""
                if hasattr(response, "text") and response.text:
                    reply_text = response.text.strip()
                elif getattr(response, "candidates", None):
                    cand = response.candidates[0]
                    parts = getattr(cand.content, "parts", [])
                    text_parts = [
                        p.text for p in parts
                        if getattr(p, "text", None) and not getattr(p, "thought", False)
                    ]
                    reply_text = "".join(text_parts).strip()

                if reply_text:
                    return reply_text

            except Exception as model_err:
                last_error = model_err
                logger.warning("Gemini model %s encountered error: %s. Trying fallback model...", model_name, str(model_err))
                continue

        if last_error:
            raise last_error

        return "I'm here to help! Could you please ask that in another way?"

    except Exception as e:
        logger.error("Gemini API error: %s", str(e))

        # User-friendly error messages and circuit breaker tripping
        error_str = str(e).lower()
        if "quota" in error_str or "429" in error_str or "resource_exhausted" in error_str:
            try:
                from .rate_limiter import trip_circuit_breaker
                trip_circuit_breaker(reason="Google Free Tier quota limit reached")
            except Exception:
                pass
            return (
                "I've reached my daily limit 😅 The AI assistant is on a free-tier usage cap "
                "to keep costs at zero. Please check back tomorrow! 🙏"
            )
        if "api_key" in error_str or "invalid" in error_str:
            return "AI assistant is temporarily unavailable. Please try again later."

        return "Sorry, I ran into an issue. Please try again in a moment! 🙏"

"""
Gemini API client wrapper for VendorVerse.

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

# The model to use — Gemini 3.6 Flash is the latest fast, free-tier friendly model
GEMINI_MODEL = "gemini-3.6-flash"


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

        # Send to Gemini
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=500,
                temperature=0.7,
            ),
        )

        return response.text

    except Exception as e:
        logger.error("Gemini API error: %s", str(e))

        # User-friendly error messages
        error_str = str(e).lower()
        if "quota" in error_str or "429" in error_str:
            return (
                "I've reached my daily limit 😅 Please try again tomorrow! "
                "The AI assistant has a free-tier usage cap to keep costs at zero."
            )
        if "api_key" in error_str or "invalid" in error_str:
            return "AI assistant is temporarily unavailable. Please try again later."

        return "Sorry, I ran into an issue. Please try again in a moment! 🙏"

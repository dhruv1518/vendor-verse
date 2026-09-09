import os
import sys

# setup django
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()

from apps.ai.gemini_client import get_gemini_response

try:
    print("Testing gemini response...")
    response = get_gemini_response("You are a helpful assistant.", "info about the product")
    print("Response:", response)
except Exception as e:
    print("Test failed with exception:", str(e))

"""
AgriSentinel Configuration & Environment Loader
===============================================
Loads environment variables safely from .env if present without hardcoding
credentials in source code or committing secrets to version control.
"""

import os
from typing import Optional

def load_env_file(filepath: str = ".env"):
    """Lightweight, zero-dependency .env parser and environment populator."""
    if not os.path.exists(filepath):
        # Also check parent directory if run from subfolder
        parent_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        if os.path.exists(parent_env):
            filepath = parent_env
        else:
            return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k and k not in os.environ:
                        os.environ[k] = v
    except Exception:
        pass

# Automatically load on import
load_env_file()

def get_config_summary() -> dict:
    """Returns a non-sensitive configuration audit status."""
    return {
        "twilio_configured": bool(os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN")),
        "groq_configured": bool(os.getenv("GROQ_API_KEY") and not os.getenv("GROQ_API_KEY").startswith("mock")),
        "weather_api_configured": bool(os.getenv("OPENWEATHER_API_KEY") and not os.getenv("OPENWEATHER_API_KEY").startswith("mock")),
        "farmer_test_phone": os.getenv("FARMER_TEST_PHONE", "+919363849952")
    }

"""
Configuration settings for the Mumzworld Shopping List Parser.
Loads environment variables and defines model/threshold constants.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Groq API ────────────────────────────────────────────────────
GROK_API_KEY = os.getenv("GROK_API_KEY", "") # Keeping the variable name same since it's already in .env
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# ── Model selection ─────────────────────────────────────────────
# Primary: Llama 3.3 70B on Groq — extremely fast and smart
PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"

# ── Generation parameters ───────────────────────────────────────
TEMPERATURE = 0.1          # Low temp for consistent structured output
MAX_TOKENS = 1500          # Reduced to avoid Groq TPM limits

# ── Confidence thresholds ───────────────────────────────────────
# Items with confidence below this are flagged as uncertain
CONFIDENCE_THRESHOLD = 0.6

# ── App settings ────────────────────────────────────────────────
APP_HOST = "0.0.0.0"
APP_PORT = 8000

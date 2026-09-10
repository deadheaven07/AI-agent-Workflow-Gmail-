"""
Centralized Configuration Module for the 3-Agent Personal Executive Suite.
Reads environment variables with sensible defaults and provides typed helpers.
"""

import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load .env file from project root if present
load_dotenv()

# --- Google Gemini API Configuration ---
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
# Default to current generation fast multimodal model if empty or unset
gemini_model_raw = os.getenv("GEMINI_MODEL", "").strip()
GEMINI_MODEL: str = gemini_model_raw if gemini_model_raw else "gemini-2.5-flash"

# --- Telegram Bot Configuration ---
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# --- Email IMAP Configuration ---
imap_server_raw = os.getenv("IMAP_SERVER", "").strip()
IMAP_SERVER: str = imap_server_raw if imap_server_raw else "imap.gmail.com"

imap_port_raw = os.getenv("IMAP_PORT", "").strip()
IMAP_PORT: int = int(imap_port_raw) if imap_port_raw.isdigit() else 993

IMAP_USER: str = os.getenv("IMAP_USER", "").strip()
IMAP_PASSWORD: str = os.getenv("IMAP_PASSWORD", "").strip()

# --- Freelance Job Feeds & Skills ---
DEFAULT_SKILLS: List[str] = ["Python", "React", "FastAPI", "Web Scraping", "AI Agents", "Streamlit"]
user_skills_raw = os.getenv("USER_SKILLS", "").strip()
USER_SKILLS: List[str] = (
    [skill.strip() for skill in user_skills_raw.split(",") if skill.strip()]
    if user_skills_raw
    else DEFAULT_SKILLS
)

FREELANCE_RSS_FEEDS: List[str] = [
    "https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss",
    "https://weworkremotely.com/categories/remote-programming-jobs.rss",
    "https://www.remoteok.com/remote-jobs.rss",
]

# --- Stock Portfolio Holdings ---
DEFAULT_HOLDINGS: List[Dict[str, Any]] = [
    {"ticker": "AAPL", "buy_price": 170.0, "qty": 10},
    {"ticker": "NVDA", "buy_price": 110.0, "qty": 15},
    {"ticker": "MSFT", "buy_price": 400.0, "qty": 5},
    {"ticker": "GOOGL", "buy_price": 165.0, "qty": 8},
]

stock_holdings_raw = os.getenv("STOCK_HOLDINGS", "").strip()
if stock_holdings_raw:
    try:
        parsed_holdings = json.loads(stock_holdings_raw)
        STOCK_HOLDINGS: List[Dict[str, Any]] = parsed_holdings if isinstance(parsed_holdings, list) and len(parsed_holdings) > 0 else DEFAULT_HOLDINGS
    except Exception:
        STOCK_HOLDINGS = DEFAULT_HOLDINGS
else:
    STOCK_HOLDINGS = DEFAULT_HOLDINGS


def is_gemini_configured() -> bool:
    """Check if a valid Gemini API key is configured."""
    return bool(GEMINI_API_KEY and not GEMINI_API_KEY.startswith("your_"))


def is_telegram_configured() -> bool:
    """Check if Telegram Bot credentials are configured."""
    return bool(
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
        and not TELEGRAM_BOT_TOKEN.startswith("your_")
        and not TELEGRAM_CHAT_ID.startswith("your_")
    )


def is_email_configured() -> bool:
    """Check if IMAP credentials are configured."""
    return bool(
        IMAP_USER
        and IMAP_PASSWORD
        and not IMAP_USER.startswith("your_")
        and not IMAP_PASSWORD.startswith("your_")
    )


def get_active_holdings() -> List[Dict[str, Any]]:
    """Retrieves holdings from SQLite persistence layer or defaults to config."""
    try:
        from data.storage import get_saved_holdings
        saved = get_saved_holdings()
        if saved:
            return saved
    except Exception:
        pass
    return STOCK_HOLDINGS


def get_active_skills() -> List[str]:
    """Retrieves candidate skills from SQLite persistence layer or defaults to config."""
    try:
        from data.storage import get_saved_skills
        saved = get_saved_skills()
        if saved:
            return saved
    except Exception:
        pass
    return USER_SKILLS


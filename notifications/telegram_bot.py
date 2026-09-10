"""
Telegram Alert Dispatcher Module.
Formats structured Markdown alerts and sends them to TELEGRAM_CHAT_ID via requests.post.
Includes safe mock fallback when credentials are not configured.
"""

import logging
from typing import List, Dict, Any, Optional
import requests
import config

logger = logging.getLogger("telegram_bot")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def escape_markdown(text: str) -> str:
    """Safely sanitize text for Telegram Markdown v1/v2 where needed."""
    if not text:
        return ""
    # For standard Markdown, keep basic text clean
    return text.replace("*", "").replace("_", "").replace("`", "'")


def send_telegram_message(message: str, parse_mode: str = "HTML") -> bool:
    """
    Sends a formatted message to the configured Telegram Chat.
    
    Args:
        message: The text/HTML content to send.
        parse_mode: 'HTML' or 'Markdown'. HTML is usually safer against formatting errors.
        
    Returns:
        bool: True if sent successfully or handled cleanly via mock fallback, False otherwise.
    """
    if not config.is_telegram_configured():
        logger.info("[TELEGRAM MOCK] Credentials not configured. Simulated Telegram message:\n%s", message)
        return True

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info("Telegram message successfully sent to chat %s", config.TELEGRAM_CHAT_ID)
            return True
        else:
            logger.error("Telegram API error (%s): %s", response.status_code, response.text)
            # Fallback retry without parse_mode if HTML syntax had an issue
            fallback_payload = {
                "chat_id": config.TELEGRAM_CHAT_ID,
                "text": message,
                "disable_web_page_preview": True,
            }
            fallback_resp = requests.post(url, json=fallback_payload, timeout=10)
            return fallback_resp.status_code == 200
    except requests.RequestException as exc:
        logger.error("Failed to connect to Telegram API: %s", exc)
        return False


def send_executive_alert(
    email_alerts: Optional[List[Dict[str, Any]]] = None,
    stock_alerts: Optional[List[Dict[str, Any]]] = None,
    job_alerts: Optional[List[Dict[str, Any]]] = None,
) -> bool:
    """
    Formats a consolidated executive digest from all 3 agents and dispatches it to Telegram.
    
    Args:
        email_alerts: List of urgent or important email summaries.
        stock_alerts: List of stock action triggers (profit-taking, stop-loss, dividend dates).
        job_alerts: List of high-ROI freelance opportunities.
        
    Returns:
        bool: Success status.
    """
    lines = [
        "👑 <b>Executive Briefing: 3-Agent Suite Alert</b>",
        "────────────────────────────",
    ]

    has_content = False

    # 1. Stock Signals
    if stock_alerts:
        has_content = True
        lines.append("\n📈 <b>PORTFOLIO & STOCK SIGNALS:</b>")
        for alert in stock_alerts:
            ticker = alert.get("ticker", "N/A")
            signal = alert.get("signal", "ALERT")
            action = alert.get("action", "")
            pnl = alert.get("pnl_pct", 0.0)
            sign = "+" if pnl > 0 else ""
            lines.append(f"• <b>{ticker}</b> ({sign}{pnl:.1f}%): {signal} — <i>{action}</i>")

    # 2. Email Triage
    if email_alerts:
        has_content = True
        lines.append("\n📩 <b>URGENT / IMPORTANT EMAILS:</b>")
        for em in email_alerts:
            sender = em.get("sender", "Unknown")
            subject = em.get("subject", "No subject")
            priority = em.get("priority", "URGENT")
            summary = em.get("summary", "")[:120]
            lines.append(f"• [{priority}] <b>{sender}</b>: {subject}")
            if summary:
                lines.append(f"  <i>Summary:</i> {summary}...")

    # 3. High-ROI Freelance Jobs
    if job_alerts:
        has_content = True
        lines.append("\n💼 <b>TOP FREELANCE OPPORTUNITIES:</b>")
        for job in job_alerts:
            title = job.get("title", "Remote Project")
            roi = job.get("roi_score", 0.0)
            budget = job.get("budget", "Competitive")
            link = job.get("link", "#")
            lines.append(f"• <b>ROI {roi}/10</b> | {title}")
            lines.append(f"  Budget: {budget} | <a href='{link}'>Apply Here</a>")

    if not has_content:
        lines.append("\n✅ All systems normal. No critical alerts triggered during this hourly scan.")

    lines.append("\n────────────────────────────")
    lines.append("🤖 <i>Sent automatically by Personal Executive Suite</i>")

    full_message = "\n".join(lines)
    return send_telegram_message(full_message, parse_mode="HTML")

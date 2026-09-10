"""
Consolidated CLI Orchestrator for the 3-Agent Personal Executive Suite.
Can be executed directly via:
    python -m agents.runner
or scheduled via GitHub Actions cron.
Scans all 3 agents, filters critical triggers, and sends an executive alert via Telegram.
"""

import sys
import logging
from datetime import datetime

from agents.email_agent import EmailAgent
from agents.stock_agent import StockAgent
from agents.freelance_agent import FreelanceAgent
from notifications.telegram_bot import send_executive_alert

# Configure clear stdout logging for GitHub Actions logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("executive_runner")


def run_all_agents() -> int:
    """
    Executes all 3 agents, filters high-priority action items,
    and dispatches a consolidated Telegram briefing.
    
    Returns:
        int: Exit status code (0 for success).
    """
    start_time = datetime.now()
    logger.info("==================================================")
    logger.info("Starting Personal Executive Suite Hourly Run: %s", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("==================================================")

    # 1. Run Email Triage Agent
    logger.info("--> [1/3] Running Email Triage Agent...")
    email_agent = EmailAgent()
    triaged_emails = email_agent.get_triaged_emails()
    urgent_emails = [
        e for e in triaged_emails if e.get("priority") in ("URGENT", "IMPORTANT")
    ]
    logger.info("Parsed %d unread emails (%d marked URGENT/IMPORTANT)", len(triaged_emails), len(urgent_emails))

    # 2. Run Stock & Portfolio Agent
    logger.info("--> [2/3] Running Stock & Portfolio Agent...")
    stock_agent = StockAgent()
    portfolio_data = stock_agent.fetch_portfolio_data()
    stock_alerts = portfolio_data.get("alerts", [])
    total_val = portfolio_data.get("total_value", 0.0)
    total_pnl = portfolio_data.get("total_pnl_dollar", 0.0)
    total_pnl_pct = portfolio_data.get("total_pnl_pct", 0.0)
    logger.info(
        "Analyzed portfolio: Total Value $%.2f | P&L: %s$%.2f (%.2f%%) | %d Active Alerts",
        total_val,
        "+" if total_pnl > 0 else "",
        total_pnl,
        total_pnl_pct,
        len(stock_alerts),
    )

    # 3. Run Freelance Job Hunter Agent
    logger.info("--> [3/3] Running Freelance Job Hunter Agent...")
    freelance_agent = FreelanceAgent()
    evaluated_jobs = freelance_agent.get_evaluated_jobs()
    high_roi_jobs = [j for j in evaluated_jobs if j.get("roi_score", 0) >= 8.0]
    logger.info("Evaluated %d opportunities (%d High-ROI >= 8.0)", len(evaluated_jobs), len(high_roi_jobs))

    # 4. Data Persistence & Deduplication
    logger.info("--> [Persistence] Storing snapshots & deduplicating alerts...")
    try:
        from data.storage import (
            save_emails,
            save_jobs,
            log_portfolio_snapshot,
            filter_and_mark_unnotified,
        )
        save_emails(triaged_emails)
        save_jobs(evaluated_jobs)
        log_portfolio_snapshot(portfolio_data)

        # Deduplicate alerts
        new_emails, new_stocks, new_jobs = filter_and_mark_unnotified(
            urgent_emails, stock_alerts, high_roi_jobs
        )
        logger.info(
            "Deduplication: %d new email alerts, %d stock alerts, %d new job alerts",
            len(new_emails),
            len(new_stocks),
            len(new_jobs),
        )
    except Exception as db_err:
        logger.warning("Storage/deduplication exception (%s); proceeding with all alerts.", db_err)
        new_emails, new_stocks, new_jobs = urgent_emails, stock_alerts, high_roi_jobs

    # 5. Dispatch Consolidated Telegram Briefing
    logger.info("--> Dispatching Executive Briefing via Telegram...")
    success = send_executive_alert(
        email_alerts=new_emails,
        stock_alerts=new_stocks,
        job_alerts=new_jobs,
    )

    duration = (datetime.now() - start_time).total_seconds()
    logger.info("==================================================")
    logger.info("Scan completed successfully in %.2f seconds (Dispatch: %s)", duration, "OK" if success else "FAILED")
    logger.info("==================================================")
    return 0


if __name__ == "__main__":
    sys.exit(run_all_agents())

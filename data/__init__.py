"""Data persistence package for 3-Agent Executive Suite."""
from .storage import (
    init_db,
    save_emails,
    update_email_status,
    save_jobs,
    update_job_status,
    log_portfolio_snapshot,
    get_portfolio_history,
    get_saved_holdings,
    save_holdings,
    get_saved_skills,
    save_skills,
    filter_and_mark_unnotified,
)

__all__ = [
    "init_db",
    "save_emails",
    "update_email_status",
    "save_jobs",
    "update_job_status",
    "log_portfolio_snapshot",
    "get_portfolio_history",
    "get_saved_holdings",
    "save_holdings",
    "get_saved_skills",
    "save_skills",
    "filter_and_mark_unnotified",
]

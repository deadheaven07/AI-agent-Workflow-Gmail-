"""
Local SQLite Persistence and Deduplication Layer for 3-Agent Executive Suite.
Stores email triage history, freelance job pipeline states, portfolio historical snapshots,
and custom portfolio/skill settings across sessions.
"""

import json
import logging
import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger("storage")

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "executive_suite.db")


def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes SQLite schema if tables do not exist."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Emails Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                sender TEXT,
                sender_name TEXT,
                subject TEXT,
                date_str TEXT,
                body TEXT,
                priority TEXT,
                summary TEXT,
                action_items_json TEXT,
                draft_reply TEXT,
                status TEXT DEFAULT 'new', -- 'new', 'handled', 'archived'
                notified INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Jobs Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT,
                company TEXT,
                source TEXT,
                link TEXT,
                budget TEXT,
                summary TEXT,
                skills_detected_json TEXT,
                skill_match_pct INTEGER,
                roi_score REAL,
                proposal TEXT,
                status TEXT DEFAULT 'discovered', -- 'discovered', 'saved', 'applied', 'declined'
                notified INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. Portfolio Snapshots Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_cost REAL,
                total_value REAL,
                pnl_dollar REAL,
                pnl_pct REAL,
                positions_json TEXT
            )
        """)

        # 4. App Settings Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value_json TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()


# Ensure DB is created on first import
init_db()


def save_emails(emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Upserts emails into the database while preserving existing user action status.
    Returns the enriched list of emails.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        for em in emails:
            eid = str(em.get("id") or em.get("subject") or "em_" + str(hash(em.get("body", ""))))
            cursor.execute("SELECT status, notified FROM emails WHERE id = ?", (eid,))
            existing = cursor.fetchone()

            status = existing["status"] if existing else em.get("status", "new")
            notified = existing["notified"] if existing else 0

            cursor.execute("""
                INSERT INTO emails (
                    id, sender, sender_name, subject, date_str, body,
                    priority, summary, action_items_json, draft_reply, status, notified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    summary=excluded.summary,
                    priority=excluded.priority,
                    action_items_json=excluded.action_items_json,
                    draft_reply=excluded.draft_reply
            """, (
                eid,
                em.get("sender", ""),
                em.get("sender_name", ""),
                em.get("subject", ""),
                em.get("date", ""),
                em.get("body", ""),
                em.get("priority", "IMPORTANT"),
                em.get("summary", ""),
                json.dumps(em.get("action_items", [])),
                em.get("draft_reply", ""),
                status,
                notified,
            ))
            em["id"] = eid
            em["status"] = status
        conn.commit()
    return emails


def update_email_status(email_id: str, new_status: str) -> None:
    """Updates the action status of an email ('new', 'handled', 'archived')."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE emails SET status = ? WHERE id = ?", (new_status, email_id))
        conn.commit()


def save_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Upserts jobs into the database while preserving user application pipeline status.
    Returns the updated list of jobs.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        for j in jobs:
            jid = str(j.get("id") or j.get("link") or str(hash(j.get("title", ""))))
            cursor.execute("SELECT status, notified FROM jobs WHERE id = ?", (jid,))
            existing = cursor.fetchone()

            status = existing["status"] if existing else j.get("status", "discovered")
            notified = existing["notified"] if existing else 0

            cursor.execute("""
                INSERT INTO jobs (
                    id, title, company, source, link, budget, summary,
                    skills_detected_json, skill_match_pct, roi_score, proposal, status, notified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    roi_score=excluded.roi_score,
                    skill_match_pct=excluded.skill_match_pct,
                    proposal=excluded.proposal
            """, (
                jid,
                j.get("title", ""),
                j.get("company", ""),
                j.get("source", ""),
                j.get("link", ""),
                j.get("budget", ""),
                j.get("summary", ""),
                json.dumps(j.get("skills_detected", [])),
                j.get("skill_match_pct", 0),
                j.get("roi_score", 0.0),
                j.get("proposal", ""),
                status,
                notified,
            ))
            j["id"] = jid
            j["status"] = status
        conn.commit()
    return jobs


def update_job_status(job_id: str, new_status: str) -> None:
    """Updates job pipeline status ('discovered', 'saved', 'applied', 'declined')."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE jobs SET status = ? WHERE id = ?", (new_status, job_id))
        conn.commit()


def log_portfolio_snapshot(portfolio_data: Dict[str, Any]) -> None:
    """Logs an hourly snapshot of portfolio equity curve to SQLite."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO portfolio_snapshots (
                total_cost, total_value, pnl_dollar, pnl_pct, positions_json
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            portfolio_data.get("total_cost", 0.0),
            portfolio_data.get("total_value", 0.0),
            portfolio_data.get("total_pnl_dollar", 0.0),
            portfolio_data.get("total_pnl_pct", 0.0),
            json.dumps(portfolio_data.get("positions", [])),
        ))
        conn.commit()


def get_portfolio_history(limit: int = 48) -> List[Dict[str, Any]]:
    """Retrieves chronological portfolio snapshots for charting equity curves."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, total_cost, total_value, pnl_dollar, pnl_pct
            FROM portfolio_snapshots
            ORDER BY timestamp ASC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def filter_and_mark_unnotified(
    email_alerts: List[Dict[str, Any]],
    stock_alerts: List[Dict[str, Any]],
    job_alerts: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Deduplication filter: only returns items that have NOT yet been notified via Telegram.
    Marks notified items as notified=1 to avoid spamming the user on subsequent hourly scans.
    """
    new_emails = []
    new_jobs = []

    with get_connection() as conn:
        cursor = conn.cursor()

        # Check emails
        for em in email_alerts:
            eid = em.get("id")
            if eid:
                cursor.execute("SELECT notified FROM emails WHERE id = ?", (eid,))
                row = cursor.fetchone()
                if not row or row["notified"] == 0:
                    new_emails.append(em)
                    cursor.execute("UPDATE emails SET notified = 1 WHERE id = ?", (eid,))
            else:
                new_emails.append(em)

        # Check jobs
        for jb in job_alerts:
            jid = jb.get("id")
            if jid:
                cursor.execute("SELECT notified FROM jobs WHERE id = ?", (jid,))
                row = cursor.fetchone()
                if not row or row["notified"] == 0:
                    new_jobs.append(jb)
                    cursor.execute("UPDATE jobs SET notified = 1 WHERE id = ?", (jid,))
            else:
                new_jobs.append(jb)

        conn.commit()

    # Stock alerts are dynamic market signals; we always pass them if active
    return new_emails, stock_alerts, new_jobs


def get_saved_holdings() -> Optional[List[Dict[str, Any]]]:
    """Retrieves custom holdings stored in DB if configured, else None."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value_json FROM app_settings WHERE key = 'stock_holdings'")
        row = cursor.fetchone()
        if row and row["value_json"]:
            try:
                return json.loads(row["value_json"])
            except Exception:
                return None
    return None


def save_holdings(holdings: List[Dict[str, Any]]) -> None:
    """Saves customized portfolio holdings into DB."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO app_settings (key, value_json, updated_at)
            VALUES ('stock_holdings', ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET
                value_json=excluded.value_json,
                updated_at=CURRENT_TIMESTAMP
        """, (json.dumps(holdings),))
        conn.commit()


def get_saved_skills() -> Optional[List[str]]:
    """Retrieves customized user skills stored in DB."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value_json FROM app_settings WHERE key = 'user_skills'")
        row = cursor.fetchone()
        if row and row["value_json"]:
            try:
                return json.loads(row["value_json"])
            except Exception:
                return None
    return None


def save_skills(skills: List[str]) -> None:
    """Saves customized user skills into DB."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO app_settings (key, value_json, updated_at)
            VALUES ('user_skills', ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET
                value_json=excluded.value_json,
                updated_at=CURRENT_TIMESTAMP
        """, (json.dumps(skills),))
        conn.commit()

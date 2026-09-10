"""
Main Streamlit Dashboard for the 3-Agent Personal Executive Suite.
Modern, high-end Light Mode UI with animated glowing agent indicators,
glassmorphic stat cards, interactive filters, and one-click execution.
"""

from datetime import datetime
import streamlit as st
import pandas as pd

import config
from agents.email_agent import EmailAgent
from agents.stock_agent import StockAgent
from agents.freelance_agent import FreelanceAgent
from notifications.telegram_bot import send_executive_alert

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Executive Suite | Autonomous 3-Agent AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Modern, High-End Light Mode CSS Design System ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700&display=swap');

    /* Clean Streamlit Overrides */
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent !important; }

    /* Global Typography & Light Palette */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1340px !important;
    }

    /* Top Executive Banner */
    .hero-banner {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 50%, #F1F5F9 100%);
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 24px 30px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04), 0 2px 6px -1px rgba(15, 23, 42, 0.02);
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        overflow: hidden;
    }
    .hero-banner::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background: linear-gradient(180deg, #2563EB 0%, #38BDF8 100%);
    }
    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 27px;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hero-desc {
        color: #64748B;
        font-size: 14px;
        margin-top: 5px;
        margin-bottom: 0;
        font-weight: 400;
    }
    .hero-badge-container {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 6px;
    }
    .system-badge {
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        color: #065F46;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.3px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 2px 6px rgba(16, 185, 129, 0.12);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.02) !important;
        padding-top: 1rem !important;
    }

    /* Sidebar Brand Box */
    .sidebar-brand {
        padding: 12px 14px;
        background: linear-gradient(135deg, #EFF6FF 0%, #F8FAFC 100%);
        border: 1px solid #DBEAFE;
        border-radius: 14px;
        margin-bottom: 22px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-icon {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: 700;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
    }

    /* Animated Sidebar Agent Status Cards */
    .agent-nav-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
    }
    .agent-nav-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px -4px rgba(15, 23, 42, 0.08);
        border-color: #CBD5E1;
    }
    .agent-nav-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .agent-nav-title {
        font-weight: 700;
        font-size: 14px;
        color: #0F172A;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .agent-nav-desc {
        font-size: 11.5px;
        color: #64748B;
        line-height: 1.4;
    }

    /* Radar Pulsing Rings */
    .radar-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        display: inline-block;
        position: relative;
    }
    .radar-blue {
        background: #2563EB;
        box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.7);
        animation: radar-pulse-blue 2.2s infinite;
    }
    .radar-green {
        background: #10B981;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: radar-pulse-green 2.2s infinite;
    }
    .radar-amber {
        background: #F59E0B;
        box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7);
        animation: radar-pulse-amber 2.2s infinite;
    }

    @keyframes radar-pulse-blue {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.6); }
        70% { transform: scale(1); box-shadow: 0 0 0 9px rgba(37, 99, 235, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); }
    }
    @keyframes radar-pulse-green {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.6); }
        70% { transform: scale(1); box-shadow: 0 0 0 9px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    @keyframes radar-pulse-amber {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.6); }
        70% { transform: scale(1); box-shadow: 0 0 0 9px rgba(245, 158, 11, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
    }

    /* Status Badges */
    .badge-pill {
        font-size: 11px;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 9999px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .badge-blue { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
    .badge-green { background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }
    .badge-amber { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }

    /* Executive KPI Metric Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.06);
    }
    .kpi-accent-blue::after { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: #3B82F6; }
    .kpi-accent-green::after { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: #10B981; }
    .kpi-accent-purple::after { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: #8B5CF6; }
    .kpi-accent-amber::after { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: #F59E0B; }

    .kpi-label {
        font-size: 12px;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .kpi-number {
        font-family: 'Outfit', sans-serif;
        font-size: 28px;
        font-weight: 700;
        color: #0F172A;
        margin-top: 6px;
        letter-spacing: -0.5px;
    }
    .kpi-subtext {
        font-size: 12.5px;
        margin-top: 6px;
        color: #64748B;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .kpi-gain { color: #059669; font-weight: 700; }
    .kpi-loss { color: #DC2626; font-weight: 700; }

    /* Modern Card Layouts */
    .dashboard-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 22px 24px;
        margin-bottom: 18px;
        box-shadow: 0 2px 12px rgba(15, 23, 42, 0.03);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .dashboard-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 6px 20px -2px rgba(15, 23, 42, 0.06);
    }

    /* Tag Pills */
    .pill-badge {
        display: inline-flex;
        align-items: center;
        padding: 3px 10px;
        font-size: 11.5px;
        font-weight: 600;
        border-radius: 8px;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .pill-urgent { background: #FEF2F2; color: #991B1B; border: 1px solid #FCA5A5; }
    .pill-important { background: #FFFBEB; color: #92400E; border: 1px solid #FCD34D; }
    .pill-low { background: #F1F5F9; color: #475569; border: 1px solid #E2E8F0; }
    .pill-roi-top { background: #ECFDF5; color: #065F46; border: 1px solid #6EE7B7; font-weight: 800; }
    .pill-roi-good { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; font-weight: 700; }
    .pill-skill { background: #F0FDF4; color: #15803D; border: 1px solid #BBF7D0; }
    .pill-budget { background: #F0FDF4; color: #166534; font-weight: 700; border: 1px solid #86EFAC; }

    /* Progress bar for skill match */
    .match-bar-bg {
        width: 100px;
        height: 7px;
        background-color: #E2E8F0;
        border-radius: 9999px;
        overflow: hidden;
        display: inline-block;
        vertical-align: middle;
        margin-left: 6px;
    }
    .match-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #3B82F6 0%, #10B981 100%);
        border-radius: 9999px;
    }

    /* Action Checklist Box */
    .action-checklist {
        background: #F8FAFC;
        border-left: 4px solid #2563EB;
        border-radius: 0 10px 10px 0;
        padding: 12px 18px;
        margin: 14px 0 10px 0;
        font-size: 13px;
        color: #1E293B;
    }

    /* Signal Callout Boxes */
    .signal-box-profit {
        background: linear-gradient(135deg, #F0FDF4 0%, #FFFFFF 100%);
        border: 1px solid #BBF7D0;
        border-left: 5px solid #10B981;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    .signal-box-risk {
        background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 100%);
        border: 1px solid #FDE68A;
        border-left: 5px solid #F59E0B;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }

    /* Streamlit Tab Buttons Enhancement */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: #F1F5F9;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        margin-bottom: 22px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 10px 22px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        color: #64748B !important;
        background-color: transparent !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [aria-selected="true"] {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08) !important;
    }

    /* Primary Action Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.28) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- State Management ---
if "emails" not in st.session_state:
    st.session_state.emails = None
if "portfolio" not in st.session_state:
    st.session_state.portfolio = None
if "jobs" not in st.session_state:
    st.session_state.jobs = None
if "last_scanned" not in st.session_state:
    st.session_state.last_scanned = datetime.now().strftime("%I:%M %p")


def trigger_agent_scan():
    """Executes all 3 background agents and caches results."""
    with st.spinner("⚡ Autonomous Agents synchronizing market data, RSS feeds, and inbox..."):
        email_agent = EmailAgent()
        stock_agent = StockAgent()
        freelance_agent = FreelanceAgent()

        st.session_state.emails = email_agent.get_triaged_emails()
        st.session_state.portfolio = stock_agent.fetch_portfolio_data()
        st.session_state.jobs = freelance_agent.get_evaluated_jobs()
        st.session_state.last_scanned = datetime.now().strftime("%I:%M %p")

        # Telegram notification
        urgent = [e for e in st.session_state.emails if e.get("priority") in ("URGENT", "IMPORTANT")]
        stk_alerts = st.session_state.portfolio.get("alerts", [])
        top_gigs = [j for j in st.session_state.jobs if j.get("roi_score", 0) >= 8.0]

        send_executive_alert(
            email_alerts=urgent,
            stock_alerts=stk_alerts,
            job_alerts=top_gigs,
        )


# Initial load
if st.session_state.emails is None:
    trigger_agent_scan()


# ====================================================
# 📌 SIDEBAR: Animated Agent Status & Controls
# ====================================================
with st.sidebar:
    # Sidebar Header
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-icon">⚡</div>
            <div>
                <div style="font-weight: 800; font-size: 15px; color: #0F172A; letter-spacing: -0.3px;">EXECUTIVE SUITE</div>
                <div style="font-size: 11px; color: #64748B; font-weight: 500;">Multi-Agent AI Controller</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<p style='font-size: 11.5px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: #94A3B8; margin-bottom: 10px;'>Live Autonomous Agents</p>", unsafe_allow_html=True)

    # 1. Email Agent Nav Card
    st.markdown(
        """
        <div class="agent-nav-card">
            <div class="agent-nav-header">
                <div class="agent-nav-title">
                    <span>📩</span> Email Triage
                </div>
                <span class="badge-pill badge-blue">
                    <span class="radar-dot radar-blue"></span> SCANNING
                </span>
            </div>
            <div class="agent-nav-desc">
                Gmail IMAP • Gemini AI Priority Categorization & Auto-Drafter
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Stock Agent Nav Card
    st.markdown(
        """
        <div class="agent-nav-card">
            <div class="agent-nav-header">
                <div class="agent-nav-title">
                    <span>📈</span> Stock & Portfolio
                </div>
                <span class="badge-pill badge-green">
                    <span class="radar-dot radar-green"></span> MONITORING
                </span>
            </div>
            <div class="agent-nav-desc">
                yfinance Live Data • +15% Take-Profit & Gemini Risk Signals
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Freelance Agent Nav Card
    st.markdown(
        """
        <div class="agent-nav-card">
            <div class="agent-nav-header">
                <div class="agent-nav-title">
                    <span>💼</span> Job Hunter
                </div>
                <span class="badge-pill badge-amber">
                    <span class="radar-dot radar-amber"></span> SEARCHING
                </span>
            </div>
            <div class="agent-nav-desc">
                RemoteOK & WWR • Gemini ROI Scorer (1-10) & Proposal Writer
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Main Action Button
    if st.button("🚀 Run All Agents Now", use_container_width=True):
        trigger_agent_scan()
        st.toast("All 3 agents successfully scanned and updated!", icon="⚡")

    st.markdown(f"<p style='text-align: center; font-size: 11px; color: #94A3B8; margin-top: 10px;'>Last cycle: <b>{st.session_state.last_scanned}</b></p>", unsafe_allow_html=True)

    # Sidebar Expandable Settings
    with st.expander("🛠️ Connection Telemetry", expanded=False):
        g_badge = "🟢 Configured" if config.is_gemini_configured() else "🟡 Mock Sandbox"
        t_badge = "🟢 Connected" if config.is_telegram_configured() else "🟡 Mock Sandbox"
        m_badge = "🟢 Connected" if config.is_email_configured() else "🟡 Mock Sandbox"

        st.markdown(f"**Gemini Model:** `{config.GEMINI_MODEL}` ({g_badge})")
        st.markdown(f"**Telegram Bot:** {t_badge}")
        st.markdown(f"**Gmail IMAP:** {m_badge}")
        st.caption("Edit `.env` to switch from Sandbox mocks to your personal live credentials.")


# ====================================================
# 👑 MAIN CONTENT: Executive Dashboard
# ====================================================

# Top Hero Header
st.markdown(
    f"""
    <div class="hero-banner">
        <div>
            <h1 class="hero-title">Personal Executive Suite</h1>
            <p class="hero-desc">Continuous intelligence across freelance job markets, portfolio risk, and inbox triage.</p>
        </div>
        <div class="hero-badge-container">
            <div class="system-badge">
                <span class="radar-dot radar-green"></span> 3 / 3 AGENTS OPERATIONAL
            </div>
            <span style="font-size: 11.5px; color: #94A3B8;">Cron Interval: Hourly (GitHub Actions)</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Navigation Tabs
tab_jobs, tab_stocks, tab_emails = st.tabs([
    "💼  Freelance Opportunities",
    "📈  Stock & Portfolio Intelligence",
    "📩  Email Triage & Digest",
])


# ====================================================
# 💼 TAB 1: Freelance Opportunities
# ====================================================
with tab_jobs:
    jobs = st.session_state.jobs or []
    high_roi_jobs = [j for j in jobs if j.get("roi_score", 0) >= 8.0]
    avg_match = int(sum(j.get("skill_match_pct", 0) for j in jobs) / max(1, len(jobs)))

    # KPI Top Bar
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-blue">
                <div class="kpi-label">Discovered Leads</div>
                <div class="kpi-number">{len(jobs)}</div>
                <div class="kpi-subtext">Across RemoteOK & WWR</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-purple">
                <div class="kpi-label">High-ROI Gigs (≥ 8.0)</div>
                <div class="kpi-number" style="color: #7C3AED;">{len(high_roi_jobs)}</div>
                <div class="kpi-subtext"><span class="kpi-gain">● Proposals Auto-Drafted</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-green">
                <div class="kpi-label">Average Match</div>
                <div class="kpi-number" style="color: #059669;">{avg_match}%</div>
                <div class="kpi-subtext">Target: {len(config.USER_SKILLS)} Core Competencies</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-amber">
                <div class="kpi-label">Top Skill Demand</div>
                <div class="kpi-number" style="font-size: 22px; margin-top: 10px;">Python / AI</div>
                <div class="kpi-subtext">High Hourly Rate Premium</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Job Cards Listing
    for job in jobs:
        roi = job.get("roi_score", 0.0)
        match_pct = job.get("skill_match_pct", 0)
        title = job.get("title", "Job Title")
        source = job.get("source", "Remote")
        budget = job.get("budget", "Competitive / Inquire")
        summary = job.get("summary", "")
        link = job.get("link", "#")
        proposal = job.get("proposal", "")
        detected_skills = job.get("skills_detected", [])

        # Pill styling
        roi_badge = f'<span class="pill-badge pill-roi-top">⚡ ROI {roi}/10 • HIGH PRIORITY</span>' if roi >= 8.0 else f'<span class="pill-badge pill-roi-good">ROI {roi}/10</span>'
        skills_html = "".join([f'<span class="pill-badge pill-skill">{s}</span>' for s in detected_skills])

        st.markdown(
            f"""
            <div class="dashboard-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 8px;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 8px;">
                            {roi_badge}
                            <span class="pill-badge pill-low">{source}</span>
                            <span class="pill-badge" style="background: #EFF6FF; color: #1E40AF; border: 1px solid #BFDBFE;">
                                Match {match_pct}%
                                <span class="match-bar-bg"><span class="match-bar-fill" style="width: {match_pct}%;"></span></span>
                            </span>
                            <span class="pill-badge pill-budget">💰 {budget}</span>
                        </div>
                        <h3 style="margin: 0 0 8px 0; font-size: 18px; font-weight: 700; color: #0F172A; line-height: 1.35;">{title}</h3>
                    </div>
                    <a href="{link}" target="_blank" style="text-decoration: none;">
                        <button style="background: #FFFFFF; color: #0F172A; border: 1px solid #CBD5E1; padding: 7px 16px; border-radius: 8px; font-size: 12.5px; font-weight: 700; cursor: pointer; white-space: nowrap;">
                            Apply on {source} ↗
                        </button>
                    </a>
                </div>
                <p style="font-size: 13.5px; color: #475569; line-height: 1.55; margin-bottom: 12px;">{summary}</p>
                <div>{skills_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if proposal:
            with st.expander(f"✨ View Gemini AI Tailored Proposal (ROI {roi}/10)", expanded=False):
                st.code(proposal, language="markdown")
                st.caption("Click the copy icon on the top right of the proposal block to paste directly into your proposal!")


# ====================================================
# 📈 TAB 2: Stock & Portfolio Intelligence
# ====================================================
with tab_stocks:
    portfolio = st.session_state.portfolio or {}
    positions = portfolio.get("positions", [])
    alerts = portfolio.get("alerts", [])
    total_val = portfolio.get("total_value", 0.0)
    total_cost = portfolio.get("total_cost", 0.0)
    pnl_dollar = portfolio.get("total_pnl_dollar", 0.0)
    pnl_pct = portfolio.get("total_pnl_pct", 0.0)

    # Top KPI Metrics
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-blue">
                <div class="kpi-label">Portfolio Value</div>
                <div class="kpi-number">${total_val:,.2f}</div>
                <div class="kpi-subtext">Real-time Market Valuation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-purple">
                <div class="kpi-label">Total Cost Basis</div>
                <div class="kpi-number">${total_cost:,.2f}</div>
                <div class="kpi-subtext">Principal Capital Invested</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s3:
        is_positive = pnl_dollar >= 0
        gain_cls = "kpi-gain" if is_positive else "kpi-loss"
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-green">
                <div class="kpi-label">Unrealized P&L</div>
                <div class="kpi-number {gain_cls}">{pnl_dollar:+,.2f}</div>
                <div class="kpi-subtext"><span class="{gain_cls}">● {pnl_pct:+.2f}% Overall Return</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s4:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-amber">
                <div class="kpi-label">Active Triggers</div>
                <div class="kpi-number" style="color: #2563EB;">{len(alerts)}</div>
                <div class="kpi-subtext">Take-Profit & Risk Signals</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Active Triggers Section
    if alerts:
        st.markdown("#### 🚨 **Active Signals & Risk Recommendations**")
        for alt in alerts:
            ticker = alt.get("ticker", "N/A")
            signal = alt.get("signal", "ALERT")
            action = alt.get("action", "")
            alt_pnl = alt.get("pnl_pct", 0.0)
            is_profit = "PROFIT" in signal
            box_cls = "signal-box-profit" if is_profit else "signal-box-risk"
            badge_color = "#059669" if is_profit else "#D97706"

            st.markdown(
                f"""
                <div class="{box_cls}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="font-weight: 800; font-size: 16px; color: #0F172A;">{ticker} ({alt_pnl:+.2f}%)</span>
                        <span style="font-size: 12px; font-weight: 800; color: {badge_color}; text-transform: uppercase;">● {signal}</span>
                    </div>
                    <div style="font-size: 13.5px; color: #334155; line-height: 1.45;">
                        <b>Executive Directive:</b> {action}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Holdings Table
    st.markdown("#### 📊 **Current Holdings Overview**")
    if positions:
        df = pd.DataFrame([
            {
                "Ticker": p["ticker"],
                "Company": p["company_name"],
                "Quantity": p["qty"],
                "Buy Price": f"${p['buy_price']:.2f}",
                "Market Price": f"${p['current_price']:.2f}",
                "Total Value": f"${p['position_value']:,.2f}",
                "P&L ($)": f"{p['pnl_dollar']:+,.2f}",
                "Return (%)": f"{p['pnl_pct']:+.2f}%",
                "Div Yield": f"{p['dividend_yield']}%",
                "Signal": p["signal"],
            }
            for p in positions
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

    # High Dividend Radar
    st.markdown("#### 💵 **High-Dividend Radar & Ex-Date Schedule**")
    high_divs = portfolio.get("high_dividends", [])
    if high_divs:
        div_cols = st.columns(len(high_divs))
        for idx, d in enumerate(high_divs):
            with div_cols[idx]:
                st.markdown(
                    f"""
                    <div class="dashboard-card" style="padding: 16px; text-align: center;">
                        <div style="font-size: 18px; font-weight: 800; color: #0F172A;">{d['ticker']}</div>
                        <div style="font-size: 11px; color: #64748B; margin-bottom: 8px;">{d['name']}</div>
                        <div style="font-size: 24px; font-weight: 800; color: #059669;">{d['yield_pct']}%</div>
                        <div style="font-size: 11.5px; color: #475569; margin-top: 6px;">Ex-Dividend: <b>{d['ex_date']}</b></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ====================================================
# 📩 TAB 3: Email Triage & Digest
# ====================================================
with tab_emails:
    emails = st.session_state.emails or []
    urgent_items = [e for e in emails if e.get("priority") == "URGENT"]
    important_items = [e for e in emails if e.get("priority") == "IMPORTANT"]
    low_items = [e for e in emails if e.get("priority") == "LOW_PRIORITY"]

    e1, e2, e3, e4 = st.columns(4)
    with e1:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-blue">
                <div class="kpi-label">Unread Inbox</div>
                <div class="kpi-number">{len(emails)}</div>
                <div class="kpi-subtext">Scanned via IMAP</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with e2:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-purple" style="border-top-color: #EF4444;">
                <div class="kpi-label">Urgent Escalations</div>
                <div class="kpi-number" style="color: #DC2626;">{len(urgent_items)}</div>
                <div class="kpi-subtext"><span class="kpi-loss">● Immediate Attention</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with e3:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-amber">
                <div class="kpi-label">Important Inquiries</div>
                <div class="kpi-number" style="color: #D97706;">{len(important_items)}</div>
                <div class="kpi-subtext">Meeting & Contract Requests</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with e4:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-green">
                <div class="kpi-label">Low Priority</div>
                <div class="kpi-number" style="color: #64748B;">{len(low_items)}</div>
                <div class="kpi-subtext">Newsletters & Automated Logs</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Priority Filter
    filter_val = st.radio(
        "Filter by Priority:",
        ["All Messages", "URGENT Only", "IMPORTANT Only", "LOW_PRIORITY Only"],
        horizontal=True,
    )

    filtered = emails
    if filter_val == "URGENT Only":
        filtered = urgent_items
    elif filter_val == "IMPORTANT Only":
        filtered = important_items
    elif filter_val == "LOW_PRIORITY Only":
        filtered = low_items

    for em in filtered:
        priority = em.get("priority", "IMPORTANT")
        sender = em.get("sender_name") or em.get("sender", "Unknown Sender")
        subject = em.get("subject", "No subject")
        date_val = em.get("date", "")
        summary = em.get("summary", "")
        actions = em.get("action_items", [])
        draft = em.get("draft_reply", "")

        pill_cls = "pill-urgent" if priority == "URGENT" else ("pill-important" if priority == "IMPORTANT" else "pill-low")
        avatar_letter = sender[0].upper() if sender else "M"

        checklist_html = ""
        if actions:
            li_tags = "".join([f"<li style='margin-bottom: 3px;'>{a}</li>" for a in actions])
            checklist_html = f"""
            <div class="action-checklist">
                <b>📌 Action Items Required:</b>
                <ul style="margin: 6px 0 0 0; padding-left: 18px;">{li_tags}</ul>
            </div>
            """

        st.markdown(
            f"""
            <div class="dashboard-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="pill-badge {pill_cls}">● {priority}</span>
                        <span style="font-size: 12px; color: #64748B;">{date_val}</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="width: 24px; height: 24px; border-radius: 50%; background: #E2E8F0; color: #334155; font-size: 11px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center;">{avatar_letter}</span>
                        <span style="font-size: 13.5px; font-weight: 700; color: #1E293B;">{sender}</span>
                    </div>
                </div>
                <h4 style="margin: 6px 0 10px 0; font-size: 17px; font-weight: 700; color: #0F172A;">{subject}</h4>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 12px 16px; font-size: 13.5px; color: #334155; line-height: 1.5;">
                    <b>Executive Summary:</b> {summary}
                </div>
                {checklist_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if draft and draft != "N/A":
            with st.expander(f"✉️ View AI Auto-Drafted Reply to {sender}", expanded=False):
                st.code(draft, language="markdown")
                st.caption("Click the copy icon on the top right to copy into your email client.")

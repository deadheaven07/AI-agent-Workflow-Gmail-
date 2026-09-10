"""
Main Streamlit Dashboard for the 3-Agent Personal Executive Suite (V2).
Upgraded with:
- SQLite persistence & deduplication
- In-App Portfolio & Skills Editor
- Interactive Plotly Candlestick Charts & Technical Indicators
- Stock News & Sentiment Analysis
- Multi-tone AI Proposal Generator
- Interactive Job Pipeline & Email Status Trackers
"""

from datetime import datetime
import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import config
from agents.email_agent import EmailAgent
from agents.stock_agent import StockAgent
from agents.freelance_agent import FreelanceAgent
from notifications.telegram_bot import send_executive_alert
from data.storage import (
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
)

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Executive Suite 2.0 | Autonomous 3-Agent AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Modern Light Mode CSS Design System ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700&display=swap');

    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent !important; }

    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }

    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1340px !important;
    }

    /* Hero Banner */
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
    }
    .system-badge {
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        color: #065F46;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
        padding-top: 1rem !important;
    }
    .sidebar-brand {
        padding: 12px 14px;
        background: linear-gradient(135deg, #EFF6FF 0%, #F8FAFC 100%);
        border: 1px solid #DBEAFE;
        border-radius: 14px;
        margin-bottom: 20px;
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
    .agent-nav-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
        transition: all 0.2s ease;
    }
    .agent-nav-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px -4px rgba(15, 23, 42, 0.08);
    }
    .radar-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        display: inline-block;
    }
    .radar-blue {
        background: #2563EB;
        animation: pulse-blue 2.2s infinite;
    }
    .radar-green {
        background: #10B981;
        animation: pulse-green 2.2s infinite;
    }
    .radar-amber {
        background: #F59E0B;
        animation: pulse-amber 2.2s infinite;
    }
    @keyframes pulse-blue { 0% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.6); } 70% { box-shadow: 0 0 0 9px rgba(37, 99, 235, 0); } 100% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); } }
    @keyframes pulse-green { 0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.6); } 70% { box-shadow: 0 0 0 9px rgba(16, 185, 129, 0); } 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); } }
    @keyframes pulse-amber { 0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.6); } 70% { box-shadow: 0 0 0 9px rgba(245, 158, 11, 0); } 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); } }

    /* KPI Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
        position: relative;
        overflow: hidden;
    }
    .kpi-accent-blue::after { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: #3B82F6; }
    .kpi-accent-green::after { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: #10B981; }
    .kpi-accent-purple::after { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: #8B5CF6; }
    .kpi-accent-amber::after { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: #F59E0B; }
    .kpi-label { font-size: 11.5px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.6px; }
    .kpi-number { font-family: 'Outfit', sans-serif; font-size: 26px; font-weight: 700; color: #0F172A; margin-top: 4px; }
    .kpi-gain { color: #059669; font-weight: 700; }
    .kpi-loss { color: #DC2626; font-weight: 700; }

    /* Content Cards */
    .dashboard-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px 22px;
        margin-bottom: 18px;
        box-shadow: 0 2px 12px rgba(15, 23, 42, 0.03);
    }
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
    .pill-status { background: #EFF6FF; color: #1D4ED8; font-weight: 600; border: 1px solid #BFDBFE; text-transform: uppercase; }

    .signal-box-profit {
        background: linear-gradient(135deg, #F0FDF4 0%, #FFFFFF 100%);
        border: 1px solid #BBF7D0;
        border-left: 5px solid #10B981;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .signal-box-risk {
        background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 100%);
        border: 1px solid #FDE68A;
        border-left: 5px solid #F59E0B;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: #F1F5F9;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        color: #64748B !important;
        background-color: transparent !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08) !important;
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
    """Runs all 3 agents, stores snapshots in SQLite, and sends Telegram alert."""
    with st.spinner("⚡ Autonomous Agents scanning markets, feeds, and inbox..."):
        email_agent = EmailAgent()
        stock_agent = StockAgent()
        freelance_agent = FreelanceAgent()

        raw_emails = email_agent.get_triaged_emails()
        st.session_state.emails = save_emails(raw_emails)

        portfolio_data = stock_agent.fetch_portfolio_data()
        st.session_state.portfolio = portfolio_data
        log_portfolio_snapshot(portfolio_data)

        raw_jobs = freelance_agent.get_evaluated_jobs()
        st.session_state.jobs = save_jobs(raw_jobs)
        st.session_state.last_scanned = datetime.now().strftime("%I:%M %p")

        urgent = [e for e in st.session_state.emails if e.get("priority") in ("URGENT", "IMPORTANT")]
        stk_alerts = st.session_state.portfolio.get("alerts", [])
        top_gigs = [j for j in st.session_state.jobs if j.get("roi_score", 0) >= 8.0]

        send_executive_alert(
            email_alerts=urgent,
            stock_alerts=stk_alerts,
            job_alerts=top_gigs,
        )


if st.session_state.emails is None:
    trigger_agent_scan()


# ====================================================
# 📌 SIDEBAR: Radar Badges, Controls & Editors
# ====================================================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-icon">⚡</div>
            <div>
                <div style="font-weight: 800; font-size: 15px; color: #0F172A;">EXECUTIVE SUITE 2.0</div>
                <div style="font-size: 11px; color: #64748B;">Autonomous Multi-Agent AI</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<p style='font-size: 11px; font-weight: 800; text-transform: uppercase; color: #94A3B8; margin-bottom: 8px;'>Active Agents</p>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="agent-nav-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; font-size: 13.5px; color: #0F172A;">📩 Email Triage</span>
                <span style="font-size: 11px; font-weight: 700; background: #EFF6FF; color: #1D4ED8; padding: 2px 8px; border-radius: 9999px;">
                    <span class="radar-dot radar-blue"></span> SCANNING
                </span>
            </div>
            <div style="font-size: 11.5px; color: #64748B; margin-top: 4px;">IMAP • Gemini Priority & Reply Drafter</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="agent-nav-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; font-size: 13.5px; color: #0F172A;">📈 Stock Intelligence</span>
                <span style="font-size: 11px; font-weight: 700; background: #ECFDF5; color: #065F46; padding: 2px 8px; border-radius: 9999px;">
                    <span class="radar-dot radar-green"></span> MONITORING
                </span>
            </div>
            <div style="font-size: 11.5px; color: #64748B; margin-top: 4px;">yfinance • +15% Take-Profit & Rebound Signals</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="agent-nav-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; font-size: 13.5px; color: #0F172A;">💼 Freelance Hunter</span>
                <span style="font-size: 11px; font-weight: 700; background: #FFFBEB; color: #92400E; padding: 2px 8px; border-radius: 9999px;">
                    <span class="radar-dot radar-amber"></span> SEARCHING
                </span>
            </div>
            <div style="font-size: 11.5px; color: #64748B; margin-top: 4px;">RemoteOK & WWR • Gemini ROI (1-10)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🚀 Run All Agents Now", use_container_width=True):
        trigger_agent_scan()
        st.toast("All 3 agents successfully executed and refreshed!", icon="⚡")

    st.markdown(f"<p style='text-align: center; font-size: 11px; color: #94A3B8; margin-top: 8px;'>Last scanned: <b>{st.session_state.last_scanned}</b></p>", unsafe_allow_html=True)

    # --- In-App Settings & Skill Editor ---
    with st.expander("⚙️ Customize Skills & Portfolio", expanded=False):
        st.markdown("##### **Target Skills**")
        current_skills = config.get_active_skills()
        skills_input = st.text_area(
            "Comma-separated skills:",
            value=", ".join(current_skills),
            height=75,
        )
        if st.button("Save Skills", key="save_skills_btn"):
            new_skills = [s.strip() for s in skills_input.split(",") if s.strip()]
            save_skills(new_skills)
            st.toast("Skills updated in SQLite! Re-running agents...", icon="✅")
            trigger_agent_scan()

        st.markdown("---")
        st.markdown("##### **Connection Status**")
        g_badge = "🟢 Configured" if config.is_gemini_configured() else "🟡 Mock Sandbox"
        t_badge = "🟢 Active" if config.is_telegram_configured() else "🟡 Mock Sandbox"
        m_badge = "🟢 Connected" if config.is_email_configured() else "🟡 Mock Sandbox"
        st.caption(f"**Gemini Model:** `{config.GEMINI_MODEL}` ({g_badge})")
        st.caption(f"**Telegram Alerts:** {t_badge}")
        st.caption(f"**Gmail IMAP:** {m_badge}")


# ====================================================
# 👑 HERO HEADER
# ====================================================
st.markdown(
    f"""
    <div class="hero-banner">
        <div>
            <h1 class="hero-title">Personal Executive Suite 2.0</h1>
            <p class="hero-desc">Persistent intelligence across freelance markets, stock equity, and inbound communications.</p>
        </div>
        <div style="text-align: right;">
            <div class="system-badge">
                <span class="radar-dot radar-green"></span> 3 / 3 AGENTS ONLINE
            </div>
            <div style="font-size: 11.5px; color: #94A3B8; margin-top: 6px;">SQLite Database: <b>Active & Persisted</b></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Navigation Tabs
tab_jobs, tab_stocks, tab_emails = st.tabs([
    "💼  Freelance Opportunities & Pipeline",
    "📈  Stock Intelligence & Technical Charts",
    "📩  Email Triage & Action Inbox",
])


# ====================================================
# 💼 TAB 1: Freelance Opportunities & Pipeline
# ====================================================
with tab_jobs:
    jobs = st.session_state.jobs or []
    high_roi_jobs = [j for j in jobs if float(j.get("roi_score", 0)) >= 8.0]
    applied_count = len([j for j in jobs if j.get("status") == "applied"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-blue">
                <div class="kpi-label">Discovered Leads</div>
                <div class="kpi-number">{len(jobs)}</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Remote Feeds</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-purple">
                <div class="kpi-label">High-ROI Gigs (≥ 8.0)</div>
                <div class="kpi-number" style="color: #7C3AED;">{len(high_roi_jobs)}</div>
                <div style="font-size: 12px; color: #059669; margin-top: 4px;">● Proposals Ready</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-green">
                <div class="kpi-label">Applications Submitted</div>
                <div class="kpi-number" style="color: #059669;">{applied_count}</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Tracked in SQLite</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        skills_summary = ", ".join(config.get_active_skills()[:3]) + "..."
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-amber">
                <div class="kpi-label">Active Stack Match</div>
                <div class="kpi-number" style="font-size: 20px; margin-top: 6px;">{skills_summary}</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Configurable in Sidebar</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Job Filtering
    filter_col1, filter_col2 = st.columns([2, 2])
    with filter_col1:
        stage_filter = st.radio(
            "Filter Pipeline Stage:",
            ["All Stages", "Discovered", "Applied", "Saved"],
            horizontal=True,
            key="job_stage_filter",
        )
    with filter_col2:
        proposal_tone = st.selectbox(
            "AI Proposal Tone Preference:",
            ["Executive Consultant", "Ultra-Concise & Direct", "High-Impact Pitch"],
            key="proposal_tone_select",
        )

    filtered_jobs = jobs
    if stage_filter == "Discovered":
        filtered_jobs = [j for j in jobs if j.get("status") in ("discovered", None)]
    elif stage_filter == "Applied":
        filtered_jobs = [j for j in jobs if j.get("status") == "applied"]
    elif stage_filter == "Saved":
        filtered_jobs = [j for j in jobs if j.get("status") == "saved"]

    for j_idx, job in enumerate(filtered_jobs):
        jid = job.get("id", f"job_{j_idx}")
        roi = float(job.get("roi_score", 0.0))
        match_pct = int(job.get("skill_match_pct", 0))
        title = job.get("title", "Job Title")
        source = job.get("source", "Remote")
        budget = job.get("budget", "Competitive / Inquire")
        summary = job.get("summary", "")
        link = job.get("link", "#")
        current_status = job.get("status", "discovered")
        proposal = job.get("proposal", "")

        roi_badge = f'<span class="pill-badge pill-roi-top">⚡ ROI {roi}/10 • TOP MATCH</span>' if roi >= 8.0 else f'<span class="pill-badge pill-roi-good">ROI {roi}/10</span>'

        st.markdown(
            f"""
            <div class="dashboard-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 14px;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 6px;">
                            {roi_badge}
                            <span class="pill-badge pill-low">{source}</span>
                            <span class="pill-badge pill-status">Status: {current_status}</span>
                            <span class="pill-badge pill-budget">💰 {budget}</span>
                            <span style="font-size: 12px; color: #1D4ED8; font-weight: 700;">Match: {match_pct}%</span>
                        </div>
                        <h3 style="margin: 0 0 6px 0; font-size: 18px; font-weight: 700; color: #0F172A;">{title}</h3>
                    </div>
                    <a href="{link}" target="_blank" style="text-decoration: none;">
                        <button style="background: #FFFFFF; color: #0F172A; border: 1px solid #CBD5E1; padding: 7px 16px; border-radius: 8px; font-size: 12px; font-weight: 700; cursor: pointer;">
                            Apply on {source} ↗
                        </button>
                    </a>
                </div>
                <p style="font-size: 13.5px; color: #475569; line-height: 1.5; margin: 10px 0;">{summary}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Pipeline Quick Actions
        b_col1, b_col2, b_col3, b_col4 = st.columns([1.2, 1.2, 1.2, 3])
        with b_col1:
            if st.button("Mark Applied ✅", key=f"app_{jid}"):
                update_job_status(jid, "applied")
                job["status"] = "applied"
                st.toast(f"Marked '{title[:30]}...' as Applied!", icon="🚀")
                st.rerun()
        with b_col2:
            if st.button("Save for Later 🔖", key=f"save_{jid}"):
                update_job_status(jid, "saved")
                job["status"] = "saved"
                st.toast(f"Saved '{title[:30]}...' to your pipeline!", icon="📌")
                st.rerun()
        with b_col3:
            if st.button("Archive ✕", key=f"arch_{jid}"):
                update_job_status(jid, "declined")
                job["status"] = "declined"
                st.rerun()

        if proposal:
            with st.expander(f"📝 Tailored Pitch Proposal (Tone: {proposal_tone})", expanded=False):
                st.code(proposal, language="markdown")
                if st.button(f"🔄 Re-craft with '{proposal_tone}' Tone", key=f"re_tone_{jid}"):
                    with st.spinner("AI drafting proposal in new tone..."):
                        f_agent = FreelanceAgent()
                        new_pitch = f_agent.generate_proposal_with_tone(job, tone=proposal_tone)
                        job["proposal"] = new_pitch
                        save_jobs([job])
                        st.toast("Proposal re-crafted!", icon="✨")
                        st.rerun()


# ====================================================
# 📈 TAB 2: Stock Intelligence & Technical Charts
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
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Live Market Value</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-purple">
                <div class="kpi-label">Cost Basis</div>
                <div class="kpi-number">${total_cost:,.2f}</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Principal Invested</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s3:
        is_pos = pnl_dollar >= 0
        gain_cls = "kpi-gain" if is_pos else "kpi-loss"
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-green">
                <div class="kpi-label">Unrealized Return</div>
                <div class="kpi-number {gain_cls}">{pnl_dollar:+,.2f}</div>
                <div class="{gain_cls}" style="font-size: 12.5px; margin-top: 4px;">● {pnl_pct:+.2f}% ROI</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s4:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-amber">
                <div class="kpi-label">Active Signals</div>
                <div class="kpi-number" style="color: #2563EB;">{len(alerts)}</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Take-Profit / Risk Alerts</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Active Triggers
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
                    <div style="font-size: 13.5px; color: #334155;">
                        <b>Executive Directive:</b> {action}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Holdings Table
    st.markdown("#### 📊 **Portfolio Holdings Table**")
    if positions:
        df = pd.DataFrame([
            {
                "Ticker": p["ticker"],
                "Company": p["company_name"],
                "Quantity": p["qty"],
                "Buy Price": f"${p['buy_price']:.2f}",
                "Market Price": f"${p['current_price']:.2f}",
                "Position Value": f"${p['position_value']:,.2f}",
                "P&L ($)": f"{p['pnl_dollar']:+,.2f}",
                "Return (%)": f"{p['pnl_pct']:+.2f}%",
                "Div Yield": f"{p['dividend_yield']}%",
                "Signal": p["signal"],
            }
            for p in positions
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

    # --- In-App Portfolio Position Editor ---
    with st.expander("➕ Add / Edit Stock Positions", expanded=False):
        h_col1, h_col2, h_col3, h_col4 = st.columns([2, 2, 2, 2])
        with h_col1:
            new_ticker = st.text_input("Ticker (e.g. TSLA)", key="add_t").upper().strip()
        with h_col2:
            new_price = st.number_input("Buy Price ($)", min_value=0.1, value=100.0, step=5.0, key="add_p")
        with h_col3:
            new_qty = st.number_input("Shares Qty", min_value=1.0, value=10.0, step=1.0, key="add_q")
        with h_col4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Add to Portfolio", key="add_pos_btn", use_container_width=True):
                if new_ticker:
                    current_h = list(config.get_active_holdings())
                    # Check if already exists
                    updated = False
                    for pos in current_h:
                        if pos["ticker"] == new_ticker:
                            pos["buy_price"] = new_price
                            pos["qty"] = new_qty
                            updated = True
                            break
                    if not updated:
                        current_h.append({"ticker": new_ticker, "buy_price": new_price, "qty": new_qty})
                    save_holdings(current_h)
                    st.toast(f"Saved {new_ticker} to SQLite portfolio!", icon="📈")
                    trigger_agent_scan()

    st.markdown("---")

    # --- Interactive Plotly Candlestick Chart & Technical Indicators ---
    st.markdown("#### 🕯️ **Interactive Technical Terminal**")
    ticker_list = [p["ticker"] for p in positions] if positions else ["AAPL", "NVDA", "MSFT"]
    c_col1, c_col2 = st.columns([2, 4])
    with c_col1:
        selected_ticker = st.selectbox("Select Ticker to Chart:", ticker_list, index=0)
        time_period = st.selectbox("Timeframe:", ["1mo", "3mo", "6mo", "1y"], index=1)

    s_agent = StockAgent()
    hist_df = s_agent.fetch_stock_history(selected_ticker, period=time_period)

    if hist_df is not None and not hist_df.empty:
        # Calculate 20-day and 50-day Simple Moving Average
        hist_df["SMA20"] = hist_df["Close"].rolling(window=20).mean()
        hist_df["SMA50"] = hist_df["Close"].rolling(window=50).mean()

        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            row_heights=[0.7, 0.3],
            subplot_titles=(f"{selected_ticker} Price & Moving Averages", "Trading Volume")
        )

        # Candlestick
        fig.add_trace(
            go.Candlestick(
                x=hist_df["Date"],
                open=hist_df["Open"],
                high=hist_df["High"],
                low=hist_df["Low"],
                close=hist_df["Close"],
                name="OHLC",
                increasing_line_color="#10B981",
                decreasing_line_color="#EF4444",
            ),
            row=1, col=1,
        )

        # SMA lines
        fig.add_trace(
            go.Scatter(x=hist_df["Date"], y=hist_df["SMA20"], mode="lines", name="SMA 20", line=dict(color="#3B82F6", width=1.5)),
            row=1, col=1,
        )
        fig.add_trace(
            go.Scatter(x=hist_df["Date"], y=hist_df["SMA50"], mode="lines", name="SMA 50", line=dict(color="#F59E0B", width=1.5)),
            row=1, col=1,
        )

        # Volume bars
        colors = ["#10B981" if c >= o else "#EF4444" for c, o in zip(hist_df["Close"], hist_df["Open"])]
        fig.add_trace(
            go.Bar(x=hist_df["Date"], y=hist_df["Volume"], name="Volume", marker_color=colors),
            row=2, col=1,
        )

        fig.update_layout(
            height=480,
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"Historical chart data for {selected_ticker} is loading or market quote was cached.")

    # --- Live News & Sentiment Scanner ---
    st.markdown(f"#### 📰 **Market News & Sentiment Radar for {selected_ticker}**")
    news_items = s_agent.fetch_stock_news(selected_ticker, limit=4)
    if news_items:
        n_cols = st.columns(len(news_items))
        for idx, news in enumerate(news_items):
            with n_cols[idx]:
                sent = news["sentiment"]
                sent_color = "#10B981" if sent == "BULLISH" else ("#EF4444" if sent == "BEARISH" else "#64748B")
                st.markdown(
                    f"""
                    <div class="dashboard-card" style="padding: 14px; min-height: 170px;">
                        <span style="font-size: 11px; font-weight: 800; color: {sent_color}; border: 1px solid {sent_color}33; background: {sent_color}15; padding: 2px 8px; border-radius: 6px;">● {sent}</span>
                        <div style="font-size: 11px; color: #94A3B8; margin-top: 6px;">{news['publisher']} • {news['date']}</div>
                        <h5 style="margin: 8px 0 0 0; font-size: 13.5px; font-weight: 700; color: #0F172A; line-height: 1.4;">
                            <a href="{news['link']}" target="_blank" style="text-decoration: none; color: #0F172A;">{news['title'][:70]}... ↗</a>
                        </h5>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # --- Historical Portfolio Equity Curve ---
    st.markdown("#### 📈 **Portfolio Historical Equity Curve**")
    hist_snapshots = get_portfolio_history(limit=30)
    if len(hist_snapshots) >= 2:
        snap_df = pd.DataFrame(hist_snapshots)
        snap_fig = go.Figure()
        snap_fig.add_trace(go.Scatter(
            x=snap_df["timestamp"], y=snap_df["total_value"],
            mode="lines+markers", name="Portfolio Value ($)",
            line=dict(color="#2563EB", width=3),
            fill="tozeroy", fillcolor="rgba(37, 99, 235, 0.08)"
        ))
        snap_fig.add_trace(go.Scatter(
            x=snap_df["timestamp"], y=snap_df["total_cost"],
            mode="lines", name="Cost Basis ($)",
            line=dict(color="#64748B", dash="dash", width=2)
        ))
        snap_fig.update_layout(
            height=280,
            template="plotly_white",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(snap_fig, use_container_width=True)
    else:
        st.caption("Historical performance equity curve will render as hourly snapshots are logged into SQLite.")


# ====================================================
# 📩 TAB 3: Email Triage & Action Inbox
# ====================================================
with tab_emails:
    emails = st.session_state.emails or []
    urgent_items = [e for e in emails if e.get("priority") == "URGENT"]
    important_items = [e for e in emails if e.get("priority") == "IMPORTANT"]
    handled_count = len([e for e in emails if e.get("status") == "handled"])

    e1, e2, e3, e4 = st.columns(4)
    with e1:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-blue">
                <div class="kpi-label">Unread Inbox</div>
                <div class="kpi-number">{len(emails)}</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Scanned via IMAP</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with e2:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-purple">
                <div class="kpi-label">Urgent Escalations</div>
                <div class="kpi-number" style="color: #DC2626;">{len(urgent_items)}</div>
                <div style="font-size: 12px; color: #DC2626; margin-top: 4px;">● Requires Immediate Response</div>
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
                <div style="font-size: 12px; color: #D97706; margin-top: 4px;">Contracts & Proposals</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with e4:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-green">
                <div class="kpi-label">Handled Messages</div>
                <div class="kpi-number" style="color: #059669;">{handled_count}</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Persisted in SQLite</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Priority Filter
    filter_val = st.radio(
        "Filter by Priority:",
        ["All Messages", "URGENT Only", "IMPORTANT Only", "LOW_PRIORITY Only", "Handled Messages"],
        horizontal=True,
        key="email_filter_radio",
    )

    filtered = emails
    if filter_val == "URGENT Only":
        filtered = urgent_items
    elif filter_val == "IMPORTANT Only":
        filtered = important_items
    elif filter_val == "LOW_PRIORITY Only":
        filtered = [e for e in emails if e.get("priority") == "LOW_PRIORITY"]
    elif filter_val == "Handled Messages":
        filtered = [e for e in emails if e.get("status") == "handled"]

    for em in filtered:
        eid = em.get("id", "msg_id")
        priority = em.get("priority", "IMPORTANT")
        sender = em.get("sender_name") or em.get("sender", "Unknown")
        subject = em.get("subject", "No subject")
        date_val = em.get("date_str") or em.get("date", "")
        summary = em.get("summary", "")
        actions = em.get("action_items", [])
        if isinstance(actions, str):
            try:
                actions = json.loads(actions)
            except Exception:
                actions = []
        draft = em.get("draft_reply", "")
        em_status = em.get("status", "new")

        pill_cls = "pill-urgent" if priority == "URGENT" else ("pill-important" if priority == "IMPORTANT" else "pill-low")
        avatar_letter = sender[0].upper() if sender else "M"

        actions_html = ""
        if actions:
            li_tags = "".join([f"<li style='margin-bottom: 3px;'>{a}</li>" for a in actions])
            actions_html = f"""
            <div style="background: #F8FAFC; border-left: 4px solid #2563EB; padding: 10px 14px; margin: 10px 0; border-radius: 0 8px 8px 0; font-size: 13px;">
                <b>📌 Action Items:</b>
                <ul style="margin: 4px 0 0 0; padding-left: 18px;">{li_tags}</ul>
            </div>
            """

        st.markdown(
            f"""
            <div class="dashboard-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div>
                        <span class="pill-badge {pill_cls}">● {priority}</span>
                        <span class="pill-badge pill-status">Status: {em_status}</span>
                        <span style="font-size: 12px; color: #64748B;">{date_val}</span>
                    </div>
                    <span style="font-size: 13px; font-weight: 700; color: #1E293B;">{sender}</span>
                </div>
                <h4 style="margin: 4px 0 8px 0; font-size: 16px; font-weight: 700; color: #0F172A;">{subject}</h4>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; font-size: 13px; color: #334155;">
                    <b>Executive Summary:</b> {summary}
                </div>
                {actions_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

        em_col1, em_col2 = st.columns([2, 5])
        with em_col1:
            if em_status != "handled":
                if st.button("Mark Handled ✅", key=f"hnd_{eid}"):
                    update_email_status(eid, "handled")
                    em["status"] = "handled"
                    st.toast("Email marked as handled in SQLite!", icon="✅")
                    st.rerun()
            else:
                if st.button("Re-open to Inbox", key=f"reop_{eid}"):
                    update_email_status(eid, "new")
                    em["status"] = "new"
                    st.rerun()

        if draft and draft != "N/A":
            with st.expander(f"✉️ View AI Auto-Drafted Reply to {sender}", expanded=False):
                st.code(draft, language="markdown")
                st.caption("Click the copy button on the code box to paste directly into your email client.")

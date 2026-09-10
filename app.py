"""
Main Streamlit Dashboard for the 3-Agent Personal Executive Suite.
Light Mode UI with animated agent status badges, real-time analytics, and 1-click execution.
"""

from datetime import datetime
import streamlit as st
import pandas as pd

import config
from agents.email_agent import EmailAgent
from agents.stock_agent import StockAgent
from agents.freelance_agent import FreelanceAgent
from notifications.telegram_bot import send_executive_alert

# --- Page Configuration ---
st.set_page_config(
    page_title="Executive Suite | 3-Agent AI Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Light Mode CSS & Animation Styles ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Light Theme Overrides */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #F8F9FA !important;
        color: #212529 !important;
    }

    /* Main container padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }

    /* Top Header */
    .executive-header {
        background: linear-gradient(135deg, #FFFFFF 0%, #F1F5F9 100%);
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .executive-title {
        font-size: 26px;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .executive-subtitle {
        color: #64748B;
        font-size: 14px;
        margin-top: 4px;
        margin-bottom: 0;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
        padding-top: 1.5rem;
    }

    /* Animated Agent Status Cards in Sidebar */
    .agent-status-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .agent-status-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
    }
    .agent-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 6px;
    }
    .agent-name {
        font-weight: 600;
        font-size: 14px;
        color: #1E293B;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .agent-meta {
        font-size: 11px;
        color: #64748B;
        margin-top: 4px;
    }

    /* Glowing Pulse Animations */
    .pulse-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        position: relative;
    }
    .pulse-green {
        background-color: #10B981;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse-green-anim 2s infinite cubic-bezier(0.45, 0, 0.55, 1);
    }
    .pulse-blue {
        background-color: #3B82F6;
        box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7);
        animation: pulse-blue-anim 2s infinite cubic-bezier(0.45, 0, 0.55, 1);
    }
    .pulse-amber {
        background-color: #F59E0B;
        box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7);
        animation: pulse-amber-anim 2s infinite cubic-bezier(0.45, 0, 0.55, 1);
    }

    @keyframes pulse-green-anim {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    @keyframes pulse-blue-anim {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(59, 130, 246, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
    }
    @keyframes pulse-amber-anim {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(245, 158, 11, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
    }

    /* Badges */
    .status-badge {
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 9999px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .badge-active-green {
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
    }
    .badge-active-blue {
        background-color: #EFF6FF;
        color: #1E40AF;
        border: 1px solid #BFDBFE;
    }
    .badge-active-amber {
        background-color: #FFFBEB;
        color: #92400E;
        border: 1px solid #FDE68A;
    }

    /* Content Cards */
    .content-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
        transition: border-color 0.2s ease;
    }
    .content-card:hover {
        border-color: #CBD5E1;
    }

    /* Stat Cards */
    .metric-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
    }
    .metric-label {
        font-size: 12px;
        color: #64748B;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #0F172A;
        margin-top: 4px;
    }
    .metric-delta-pos {
        color: #10B981;
        font-size: 13px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .metric-delta-neg {
        color: #EF4444;
        font-size: 13px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }

    /* Tag Pills */
    .pill {
        display: inline-block;
        padding: 2px 9px;
        font-size: 11px;
        font-weight: 500;
        border-radius: 6px;
        margin-right: 6px;
        margin-top: 4px;
    }
    .pill-urgent { background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }
    .pill-important { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
    .pill-low { background: #F1F5F9; color: #475569; border: 1px solid #E2E8F0; }
    .pill-skill { background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }
    .pill-score { background: #EDE9FE; color: #5B21B6; font-weight: 700; border: 1px solid #DDD6FE; }

    /* Action Box */
    .action-box {
        background: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 12px 0;
        font-size: 13px;
    }

    /* Proposal Box */
    .proposal-box {
        background: #FAF5FF;
        border: 1px solid #E9D5FF;
        border-radius: 10px;
        padding: 14px;
        font-size: 13px;
        color: #3B0764;
        margin-top: 10px;
        line-height: 1.5;
        white-space: pre-wrap;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 18px;
        font-weight: 600;
        color: #64748B;
        background-color: transparent;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        color: #1E293B !important;
        border-bottom: 2px solid #2563EB !important;
        background-color: #FFFFFF !important;
    }

    /* Streamlit Button Styling */
    div.stButton > button:first-child {
        background-color: #2563EB;
        color: white;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #1D4ED8;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Initialize Session State Data ---
if "emails" not in st.session_state:
    st.session_state.emails = None
if "portfolio" not in st.session_state:
    st.session_state.portfolio = None
if "jobs" not in st.session_state:
    st.session_state.jobs = None
if "last_scanned" not in st.session_state:
    st.session_state.last_scanned = datetime.now().strftime("%I:%M %p")


def run_agents():
    """Trigger all agents and update state."""
    with st.spinner("🤖 Autonomous Agents scanning emails, market data, and job feeds..."):
        email_agent = EmailAgent()
        stock_agent = StockAgent()
        freelance_agent = FreelanceAgent()

        st.session_state.emails = email_agent.get_triaged_emails()
        st.session_state.portfolio = stock_agent.fetch_portfolio_data()
        st.session_state.jobs = freelance_agent.get_evaluated_jobs()
        st.session_state.last_scanned = datetime.now().strftime("%I:%M %p")

        # Also trigger telegram alert
        urgent_emails = [e for e in st.session_state.emails if e.get("priority") in ("URGENT", "IMPORTANT")]
        stock_alerts = st.session_state.portfolio.get("alerts", [])
        top_jobs = [j for j in st.session_state.jobs if j.get("roi_score", 0) >= 8.0]

        send_executive_alert(
            email_alerts=urgent_emails,
            stock_alerts=stock_alerts,
            job_alerts=top_jobs,
        )


# Run automatically once on first boot if unpopulated
if st.session_state.emails is None:
    run_agents()


# ==========================================
# 📌 SIDEBAR: Animated Agent Status Panel
# ==========================================
with st.sidebar:
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 24px;">⚡</span>
                <div>
                    <h3 style="margin: 0; font-size: 17px; font-weight: 700; color: #0F172A;">Personal Executive</h3>
                    <p style="margin: 0; font-size: 11px; color: #64748B;">Multi-Agent AI Suite (100% Free)</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### **Active AI Agents**")

    # Agent 1: Email Triage
    st.markdown(
        """
        <div class="agent-status-card">
            <div class="agent-card-header">
                <div class="agent-name">
                    <span>📩</span> Email Triage Agent
                </div>
                <div class="status-badge badge-active-blue">
                    <span class="pulse-dot pulse-blue"></span> Scanning
                </div>
            </div>
            <div class="agent-meta">Provider: Gmail IMAP + Gemini AI</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Agent 2: Stock & Portfolio
    st.markdown(
        """
        <div class="agent-status-card">
            <div class="agent-card-header">
                <div class="agent-name">
                    <span>📈</span> Stock & Portfolio Agent
                </div>
                <div class="status-badge badge-active-green">
                    <span class="pulse-dot pulse-green"></span> Monitoring
                </div>
            </div>
            <div class="agent-meta">Provider: yfinance + Gemini Signals</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Agent 3: Freelance Job Hunter
    st.markdown(
        """
        <div class="agent-status-card">
            <div class="agent-card-header">
                <div class="agent-name">
                    <span>💼</span> Freelance Job Hunter
                </div>
                <div class="status-badge badge-active-amber">
                    <span class="pulse-dot pulse-amber"></span> Searching
                </div>
            </div>
            <div class="agent-meta">Provider: RemoteOK, WWR + Gemini ROI</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr style='border: 0; border-top: 1px solid #E2E8F0; margin: 18px 0;'>", unsafe_allow_html=True)

    # Manual Run Button
    if st.button("🚀 Run All Agents Now", use_container_width=True):
        run_agents()
        st.toast("All 3 agents successfully executed and refreshed!", icon="✅")

    st.markdown(f"<p style='text-align: center; font-size: 11px; color: #94A3B8; margin-top: 10px;'>Last scanned: {st.session_state.last_scanned}</p>", unsafe_allow_html=True)

    # Integration Status Pill Box
    with st.expander("⚙️ System Status & Secrets", expanded=False):
        g_status = "🟢 Connected" if config.is_gemini_configured() else "🟡 Mock / Demo"
        t_status = "🟢 Active" if config.is_telegram_configured() else "🟡 Mock / Demo"
        m_status = "🟢 Connected" if config.is_email_configured() else "🟡 Mock / Demo"

        st.markdown(f"**Gemini LLM:** {g_status}")
        st.caption(f"Model: `{config.GEMINI_MODEL}`")
        st.markdown(f"**Telegram Alerts:** {t_status}")
        st.markdown(f"**Gmail IMAP:** {m_status}")


# ==========================================
# 👑 MAIN CONTENT: Executive Dashboard
# ==========================================

# Top Greeting Header
st.markdown(
    f"""
    <div class="executive-header">
        <div>
            <h1 class="executive-title">Personal Executive Suite</h1>
            <p class="executive-subtitle">Autonomous multi-agent intelligence for high-value freelance bids, equity positions, and inbox triage.</p>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 12px; color: #64748B; font-weight: 500;">AUTONOMOUS STATUS</div>
            <div style="font-size: 14px; font-weight: 700; color: #10B981; display: flex; align-items: center; justify-content: flex-end; gap: 6px;">
                <span class="pulse-dot pulse-green"></span> 3 / 3 AGENTS ONLINE
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Main Navigation Tabs
tab_freelance, tab_stocks, tab_emails = st.tabs([
    "💼  Freelance Opportunities",
    "📈  Stock & Portfolio Intelligence",
    "📩  Email Triage & Digest",
])


# ==========================================
# 💼 TAB 1: Freelance Opportunities
# ==========================================
with tab_freelance:
    jobs = st.session_state.jobs or []
    high_roi_count = len([j for j in jobs if j.get("roi_score", 0) >= 8.0])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-label">Discovered Opportunities</div>
                <div class="metric-value">{len(jobs)}</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Across RemoteOK & WeWorkRemotely</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-label">High-ROI Leads (≥ 8.0)</div>
                <div class="metric-value" style="color: #7C3AED;">{high_roi_count}</div>
                <div style="font-size: 12px; color: #10B981; margin-top: 4px;">⚡ Ready-to-Send Proposals Drafted</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        skills_summary = ", ".join(config.USER_SKILLS[:3]) + "..."
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-label">Target Skillset</div>
                <div class="metric-value" style="font-size: 16px; margin-top: 8px; font-weight: 600;">{skills_summary}</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 6px;">Configured in <code>.env</code></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Render each job card
    for job in jobs:
        roi = job.get("roi_score", 0.0)
        match_pct = job.get("skill_match_pct", 0)
        title = job.get("title", "Job Posting")
        budget = job.get("budget", "Competitive")
        source = job.get("source", "Remote")
        link = job.get("link", "#")
        summary = job.get("summary", "")
        proposal = job.get("proposal", "")
        skills_detected = job.get("skills_detected", [])

        # Color-code ROI badge
        roi_style = "background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0;" if roi >= 8.0 else "background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A;"

        skills_pills_html = "".join([f'<span class="pill pill-skill">{s}</span>' for s in skills_detected])

        st.markdown(
            f"""
            <div class="content-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 16px;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                            <span class="pill pill-score" style="{roi_style}">⚡ ROI {roi}/10</span>
                            <span class="pill pill-low">{source}</span>
                            <span class="pill" style="background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE;">Match {match_pct}%</span>
                        </div>
                        <h3 style="margin: 0 0 6px 0; font-size: 18px; font-weight: 700; color: #0F172A;">{title}</h3>
                        <div style="font-size: 13px; font-weight: 600; color: #059669; margin-bottom: 10px;">💰 Budget: {budget}</div>
                    </div>
                    <a href="{link}" target="_blank" style="text-decoration: none;">
                        <button style="background-color: #F1F5F9; color: #0F172A; border: 1px solid #CBD5E1; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer;">
                            Apply on {source} ↗
                        </button>
                    </a>
                </div>
                <p style="font-size: 13px; color: #475569; line-height: 1.5; margin-bottom: 10px;">{summary}</p>
                <div>{skills_pills_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if proposal:
            with st.expander(f"📝 View Gemini AI Tailored Proposal (ROI {roi}/10)", expanded=False):
                st.code(proposal, language="markdown")
                st.caption("Tip: You can copy this custom pitch directly into your application!")


# ==========================================
# 📈 TAB 2: Stock & Portfolio Intelligence
# ==========================================
with tab_stocks:
    portfolio = st.session_state.portfolio or {}
    positions = portfolio.get("positions", [])
    alerts = portfolio.get("alerts", [])
    total_val = portfolio.get("total_value", 0.0)
    total_cost = portfolio.get("total_cost", 0.0)
    pnl_dollar = portfolio.get("total_pnl_dollar", 0.0)
    pnl_pct = portfolio.get("total_pnl_pct", 0.0)

    # P&L Top Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-label">Portfolio Value</div>
                <div class="metric-value">${total_val:,.2f}</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Live Market Value</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-label">Total Cost Basis</div>
                <div class="metric-value">${total_cost:,.2f}</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Principal Invested</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        is_pos = pnl_dollar >= 0
        delta_class = "metric-delta-pos" if is_pos else "metric-delta-neg"
        sign = "+" if is_pos else ""
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-label">Unrealized P&L ($)</div>
                <div class="metric-value {delta_class}">{sign}${pnl_dollar:,.2f}</div>
                <div class="{delta_class}" style="margin-top: 4px;">{sign}{pnl_pct:.2f}% Return</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-label">Active Signals</div>
                <div class="metric-value" style="color: #2563EB;">{len(alerts)}</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Take-Profit / Stop-Loss Triggers</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Active Triggers & Recommendations Section
    if alerts:
        st.markdown("#### 🚨 **Active Portfolio Signals & Recommendations**")
        for alert in alerts:
            ticker = alert.get("ticker", "N/A")
            signal = alert.get("signal", "ALERT")
            action = alert.get("action", "")
            alert_pnl = alert.get("pnl_pct", 0.0)
            is_profit = "PROFIT" in signal
            border_color = "#10B981" if is_profit else "#F59E0B"
            badge_bg = "#ECFDF5" if is_profit else "#FFFBEB"
            badge_fg = "#065F46" if is_profit else "#92400E"

            st.markdown(
                f"""
                <div style="background: #FFFFFF; border-left: 5px solid {border_color}; border: 1px solid #E2E8F0; border-left-width: 5px; border-radius: 10px; padding: 14px 18px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; font-size: 15px; color: #0F172A;">{ticker} ({alert_pnl:+.2f}%)</span>
                        <span style="font-size: 11px; font-weight: 700; background: {badge_bg}; color: {badge_fg}; padding: 3px 8px; border-radius: 6px;">{signal}</span>
                    </div>
                    <div style="margin-top: 6px; font-size: 13px; color: #334155;">
                        <b>Recommendation:</b> {action}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Holdings Table
    st.markdown("#### 📊 **Current Holdings Overview**")
    if positions:
        df_display = pd.DataFrame([
            {
                "Ticker": p["ticker"],
                "Company": p["company_name"],
                "Qty": p["qty"],
                "Buy Price": f"${p['buy_price']:.2f}",
                "Current": f"${p['current_price']:.2f}",
                "Position Value": f"${p['position_value']:,.2f}",
                "P&L ($)": f"{p['pnl_dollar']:+,.2f}",
                "P&L (%)": f"{p['pnl_pct']:+.2f}%",
                "Div Yield": f"{p['dividend_yield']}%",
                "Signal": p["signal"],
            }
            for p in positions
        ])
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Dividend Scanner Section
    st.markdown("#### 💵 **High-Dividend Yield & Ex-Date Scanner**")
    high_divs = portfolio.get("high_dividends", [])
    if high_divs:
        div_cols = st.columns(len(high_divs))
        for idx, div_item in enumerate(high_divs):
            with div_cols[idx]:
                st.markdown(
                    f"""
                    <div class="content-card" style="padding: 14px;">
                        <div style="font-size: 15px; font-weight: 700; color: #0F172A;">{div_item['ticker']}</div>
                        <div style="font-size: 11px; color: #64748B; margin-bottom: 8px;">{div_item['name']}</div>
                        <div style="font-size: 20px; font-weight: 700; color: #059669;">{div_item['yield_pct']}%</div>
                        <div style="font-size: 11px; color: #475569; margin-top: 4px;">Ex-Date: <b>{div_item['ex_date']}</b></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ==========================================
# 📩 TAB 3: Email Triage & Digest
# ==========================================
with tab_emails:
    emails = st.session_state.emails or []
    urgent_count = len([e for e in emails if e.get("priority") == "URGENT"])
    important_count = len([e for e in emails if e.get("priority") == "IMPORTANT"])
    low_count = len([e for e in emails if e.get("priority") == "LOW_PRIORITY"])

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-label">Unread Inbox</div>
                <div class="metric-value">{len(emails)}</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Triaged Messages</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-label">Urgent Escalations</div>
                <div class="metric-value" style="color: #DC2626;">{urgent_count}</div>
                <div style="font-size: 12px; color: #DC2626; margin-top: 4px;">Immediate Attention</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-label">Important Inquiries</div>
                <div class="metric-value" style="color: #D97706;">{important_count}</div>
                <div style="font-size: 12px; color: #D97706; margin-top: 4px;">Follow-ups Required</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-label">Low Priority / News</div>
                <div class="metric-value" style="color: #64748B;">{low_count}</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Automated / Newsletters</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Filter Controls
    filter_choice = st.radio(
        "Filter Messages by Priority:",
        ["All Priorities", "URGENT Only", "IMPORTANT Only", "LOW_PRIORITY Only"],
        horizontal=True,
    )

    filtered_emails = emails
    if filter_choice == "URGENT Only":
        filtered_emails = [e for e in emails if e.get("priority") == "URGENT"]
    elif filter_choice == "IMPORTANT Only":
        filtered_emails = [e for e in emails if e.get("priority") == "IMPORTANT"]
    elif filter_choice == "LOW_PRIORITY Only":
        filtered_emails = [e for e in emails if e.get("priority") == "LOW_PRIORITY"]

    for email_item in filtered_emails:
        priority = email_item.get("priority", "IMPORTANT")
        sender = email_item.get("sender_name") or email_item.get("sender", "Unknown")
        subject = email_item.get("subject", "No subject")
        date_str = email_item.get("date", "")
        summary = email_item.get("summary", "")
        actions = email_item.get("action_items", [])
        draft_reply = email_item.get("draft_reply", "")

        pill_class = "pill-urgent" if priority == "URGENT" else ("pill-important" if priority == "IMPORTANT" else "pill-low")

        actions_html = ""
        if actions:
            items_li = "".join([f"<li>{act}</li>" for act in actions])
            actions_html = f"""
            <div class="action-box">
                <b>📌 Action Items:</b>
                <ul style="margin: 4px 0 0 0; padding-left: 20px;">{items_li}</ul>
            </div>
            """

        st.markdown(
            f"""
            <div class="content-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div>
                        <span class="pill {pill_class}">● {priority}</span>
                        <span style="font-size: 12px; color: #64748B;">{date_str}</span>
                    </div>
                    <span style="font-size: 13px; font-weight: 600; color: #334155;">{sender}</span>
                </div>
                <h4 style="margin: 4px 0 8px 0; font-size: 16px; font-weight: 700; color: #0F172A;">{subject}</h4>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; font-size: 13px; color: #334155; margin-bottom: 8px;">
                    <b>Executive Summary:</b> {summary}
                </div>
                {actions_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if draft_reply and draft_reply != "N/A":
            with st.expander(f"✉️ View AI Auto-Drafted Reply to {sender}", expanded=False):
                st.code(draft_reply, language="markdown")
                st.caption("Click the copy icon on the top-right of the code box to paste into your email client!")

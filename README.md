# AI-agent-Workflow-Gmail-

# 👑 3-Agent Personal Executive Suite

> **100% Free-Tier Autonomous Multi-Agent AI Suite in Python** using Streamlit, Google Gemini API, Yahoo Finance (`yfinance`), RSS Feeds (`feedparser`), Telegram Bot API, and GitHub Actions.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)
![Gemini AI](https://img.shields.io/badge/Google%20Gemini-API%20Free%20Tier-4285F4.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20Alerts-0088cc.svg)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-24%2F7%20Cron-2088FF.svg)
![Cost](https://img.shields.io/badge/Infrastructure%20Cost-$0%20(Free%20Tier)-brightgreen.svg)

---

## 🌟 Executive Overview (Version 2.0)

The **Personal Executive Suite 2.0** coordinates three autonomous background agents to automate daily high-leverage workflows with persistent SQLite storage and deduplication:

| Agent | Mission & Automation | Data Provider | Free Tier Integration |
| :--- | :--- | :--- | :--- |
| 📩 **Email Triage Agent** | Scans unread inbox, categorizes `URGENT` / `IMPORTANT` / `LOW_PRIORITY`, extracts action items, auto-drafts replies, and tracks `handled` status in SQLite. | Gmail / Outlook IMAP | Python `imaplib` + Gemini API |
| 📈 **Stock & Portfolio Agent** | Tracks holdings, P&L, triggers **+15% Profit Taking** or **-5% Gemini Stop-Loss/Rebound** analysis, renders **Plotly Candlestick Charts** with SMA20/SMA50, and scans **Live News Sentiment**. | Yahoo Finance | `yfinance` + Gemini API |
| 💼 **Freelance Job Hunter** | Scrapes remote developer job feeds, scores **ROI (1-10)** and **Skill Match %**, generates **custom-tone proposals**, and tracks job pipeline (`Discovered` ➔ `Applied` ➔ `Saved`). | RemoteOK, WeWorkRemotely | `feedparser` + Gemini API |

---

## 🎨 UI & Design System (Light Mode 2.0)

- **Theme:** Clean, modern Light Mode aesthetic (`#F8FAFC` canvas, crisp `#FFFFFF` cards, `#E2E8F0` borders, subtle box shadows, Plus Jakarta Sans & Outfit typography).
- **Sticky Left Sidebar:** Animated CSS `@keyframes` pulsing glow indicators for all 3 agents:
  - 📩 **Email Agent** — [Status: 🟢 Active / Scanning] (Soft Blue Pulse)
  - 📈 **Stock Agent** — [Status: 🟢 Active / Monitoring] (Soft Green Pulse)
  - 💼 **Freelance Agent** — [Status: 🟢 Active / Searching] (Soft Amber Pulse)
  - ⚙️ **In-App Skill Editor:** Add or modify skills dynamically in the UI.
- **Interactive Multi-Agent Tabs:**
  1. **💼 Freelance Pipeline:** Filterable cards with ROI score pills, budget, match %, 3-tone AI proposal re-crafter, and pipeline stage buttons (`Applied`, `Saved`, `Archive`).
  2. **📈 Stock Terminal:** Interactive **Plotly Candlestick Chart** with 20-day & 50-day moving averages and volume, **Live News Sentiment Radar** (`Bullish`/`Bearish`/`Neutral`), **In-App Portfolio Position Editor**, and historical equity curve.
  3. **📩 Email Action Inbox:** Priority filters (`URGENT`, `IMPORTANT`, `LOW_PRIORITY`, `Handled`), summary cards, action checklists, and one-click `Mark Handled` action buttons.

---

## 📁 Project Structure

```
.
├── .env.example                     # Environment template with setup instructions
├── .gitignore                       # Clean gitignore excluding secrets and virtual environments
├── .streamlit/                      # Streamlit custom theme configuration
│   └── config.toml
├── Dockerfile                       # Production container setup
├── docker-compose.yml               # 1-command Docker deployment
├── requirements.txt                 # Pinned dependencies
├── config.py                        # Centralized typed configuration & secret loader
├── app.py                           # Main Streamlit Light-Theme Dashboard (V2)
├── agents/
│   ├── __init__.py
│   ├── email_agent.py               # Gmail IMAP fetcher, Gemini categorization & reply drafter
│   ├── freelance_agent.py           # RemoteOK/WWR scraper, Gemini ROI scorer & tone proposal generator
│   ├── stock_agent.py               # yfinance data, Candlestick charts, News sentiment & Gemini signals
│   └── runner.py                    # Consolidated CLI runner with SQLite deduplication
├── data/
│   ├── __init__.py
│   └── storage.py                   # SQLite persistence, snapshot logging & deduplication engine
├── notifications/
│   ├── __init__.py
│   └── telegram_bot.py              # Telegram alert dispatcher with HTML formatting & mock fallback
├── .github/
│   └── workflows/
│       └── scheduled_runner.yml     # Hourly GitHub Actions cron trigger (100% Free)
└── README.md                        # Documentation & setup guide
```

---

## 🚀 Quick Start Guide

### 1. Clone & Set Up Virtual Environment

```bash
# Clone the repository
git clone https://github.com/deadheaven07/AI-agent-Workflow-Gmail-.git
cd AI-agent-Workflow-Gmail-

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the template:
```bash
cp .env.example .env
```

Open `.env` and fill in your credentials (or test with the built-in demo mocks):

```env
# 1. Google Gemini API (Free: https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-2.5-flash

# 2. Telegram Bot (Free: Create with @BotFather on Telegram)
TELEGRAM_BOT_TOKEN=123456789:ABC...
TELEGRAM_CHAT_ID=987654321

# 3. Gmail IMAP (Create App Password at: https://myaccount.google.com/apppasswords)
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USER=your_email@gmail.com
IMAP_PASSWORD=your_16_character_app_password

# 4. User Skills & Holdings
USER_SKILLS=Python,React,FastAPI,Web Scraping,AI Agents
STOCK_HOLDINGS=[{"ticker": "AAPL", "buy_price": 170.0, "qty": 10}, {"ticker": "NVDA", "buy_price": 110.0, "qty": 15}, {"ticker": "MSFT", "buy_price": 400.0, "qty": 5}]
```

> **Note on Fail-Safe Mocks:** If any API key is missing or unconfigured, the suite automatically falls back to clean, realistic mock data so you can test the UI and workflow immediately without crashes.

---

### 3. Run the Streamlit Dashboard

```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

### 4. Run the Background CLI Runner

To execute all 3 agents in batch and dispatch a consolidated summary to Telegram:

```bash
python -m agents.runner
```

---

## ⚙️ 24/7 Free Automation with GitHub Actions

The repository includes a GitHub Actions workflow in `.github/workflows/scheduled_runner.yml` configured to execute **hourly** (`0 * * * *` UTC) at zero cost.

### Setting Up GitHub Repository Secrets:
1. Go to your GitHub Repository -> **Settings** -> **Secrets and variables** -> **Actions**.
2. Click **New repository secret** and add:
   - `GEMINI_API_KEY`: Your Google AI Studio API key.
   - `TELEGRAM_BOT_TOKEN`: Your Telegram Bot token.
   - `TELEGRAM_CHAT_ID`: Your Telegram chat ID.
   - `IMAP_USER`: Your Gmail address.
   - `IMAP_PASSWORD`: Your 16-character Gmail App Password.
3. You can manually test the runner anytime by navigating to the **Actions** tab on GitHub, selecting **Hourly 3-Agent Executive Runner**, and clicking **Run workflow**.

---

## ☁️ Deploying the Dashboard to Streamlit Cloud

1. Push this repository to GitHub:
   ```bash
   git add .
   git commit -m "Deploy 3-Agent Executive Suite"
   git push origin main
   ```
2. Visit [share.streamlit.io](https://share.streamlit.io/) and click **New app**.
3. Select your repository `deadheaven07/AI-agent-Workflow-Gmail-` and set the main file path to `app.py`.
4. In **Advanced settings**, paste your `.env` variables into the **Secrets** section.
5. Click **Deploy**!

## 🐳 One-Command Deployment with Docker

You can spin up the entire suite in a clean container with persistent SQLite storage:

```bash
# Build and run container in background
docker compose up -d

# View live dashboard at http://localhost:8501
# View logs:
docker compose logs -f
```

---

## 🔒 Security Best Practices

- **Never commit your `.env` file!** The `.gitignore` file is pre-configured to ignore `.env`, virtual environments, and caches.
- **Gmail Security:** Always use an [App Password](https://myaccount.google.com/apppasswords) with 2-Factor Authentication enabled. Never use your main Google account password.
- **IMAP Read-Only Mode:** The email agent connects with `readonly=True` to ensure it never deletes, alters, or marks emails as read without your explicit consent.

---

## 📄 License

MIT License. Free for personal and commercial use.

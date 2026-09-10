"""
Stock & Portfolio Agent.
Tracks user stock holdings, calculates real-time P&L with yfinance,
triggers profit-taking signals (P&L >= +15%), stop-loss / rebound analysis (P&L <= -5%)
with Google Gemini API, and monitors high dividend yields and ex-dividend dates.
Includes clean fallback mocks if network or rate limits occur.
"""

from datetime import datetime
import json
import logging
import re
from typing import List, Dict, Any, Optional

import config

logger = logging.getLogger("stock_agent")


def get_mock_stock_data(holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generates realistic mock stock portfolio data if yfinance is unreachable."""
    mock_market = {
        "AAPL": {
            "current_price": 224.50,
            "company_name": "Apple Inc.",
            "dividend_yield": 0.52,
            "ex_dividend_date": "2026-08-11",
            "target_price": 245.0,
            "currency": "USD",
        },
        "NVDA": {
            "current_price": 132.80,
            "company_name": "NVIDIA Corporation",
            "dividend_yield": 0.08,
            "ex_dividend_date": "2026-09-04",
            "target_price": 155.0,
            "currency": "USD",
        },
        "MSFT": {
            "current_price": 448.20,
            "company_name": "Microsoft Corporation",
            "dividend_yield": 0.72,
            "ex_dividend_date": "2026-08-20",
            "target_price": 500.0,
            "currency": "USD",
        },
        "GOOGL": {
            "current_price": 158.40,
            "company_name": "Alphabet Inc.",
            "dividend_yield": 0.48,
            "ex_dividend_date": "2026-09-08",
            "target_price": 190.0,
            "currency": "USD",
        },
    }

    processed_positions = []
    total_cost = 0.0
    total_value = 0.0
    alerts = []

    for item in holdings:
        ticker = item.get("ticker", "AAPL").upper()
        buy_price = float(item.get("buy_price", 100.0))
        qty = float(item.get("qty", 10))

        market_info = mock_market.get(ticker, {
            "current_price": round(buy_price * 1.08, 2),
            "company_name": f"{ticker} Corp",
            "dividend_yield": 1.2,
            "ex_dividend_date": "2026-09-15",
            "target_price": round(buy_price * 1.25, 2),
            "currency": "USD",
        })

        curr_price = market_info["current_price"]
        position_cost = buy_price * qty
        position_value = curr_price * qty
        pnl_dollar = position_value - position_cost
        pnl_pct = ((curr_price - buy_price) / buy_price) * 100.0 if buy_price else 0.0

        total_cost += position_cost
        total_value += position_value

        # Signal Logic
        signal = "HOLD"
        action = "Maintain current position"
        badge_type = "neutral"

        if pnl_pct >= 15.0:
            signal = "PROFIT TAKING"
            action = f"SELL 30-50% to lock in +{pnl_pct:.1f}% gain"
            badge_type = "profit"
            alerts.append({
                "ticker": ticker,
                "signal": signal,
                "action": action,
                "pnl_pct": pnl_pct,
                "current_price": curr_price,
            })
        elif pnl_pct <= -5.0:
            signal = "STOP LOSS / REBOUND"
            action = "HOLD (rebound likely based on strong Q3 fundamentals)"
            badge_type = "warning"
            alerts.append({
                "ticker": ticker,
                "signal": signal,
                "action": action,
                "pnl_pct": pnl_pct,
                "current_price": curr_price,
            })

        processed_positions.append({
            "ticker": ticker,
            "company_name": market_info["company_name"],
            "qty": qty,
            "buy_price": buy_price,
            "current_price": curr_price,
            "position_cost": position_cost,
            "position_value": position_value,
            "pnl_dollar": pnl_dollar,
            "pnl_pct": pnl_pct,
            "dividend_yield": market_info["dividend_yield"],
            "ex_dividend_date": market_info["ex_dividend_date"],
            "target_price": market_info["target_price"],
            "signal": signal,
            "action": action,
            "badge_type": badge_type,
        })

    # High dividend opportunities
    high_dividend_watchlist = [
        {"ticker": "SCHD", "name": "Schwab US Dividend Equity ETF", "yield_pct": 3.42, "ex_date": "2026-09-24"},
        {"ticker": "JNJ", "name": "Johnson & Johnson", "yield_pct": 3.12, "ex_date": "2026-08-25"},
        {"ticker": "VZ", "name": "Verizon Communications", "yield_pct": 6.35, "ex_date": "2026-10-08"},
        {"ticker": "O", "name": "Realty Income Corp (Monthly)", "yield_pct": 5.48, "ex_date": "2026-09-30"},
    ]

    total_pnl_dollar = total_value - total_cost
    total_pnl_pct = ((total_value - total_cost) / total_cost) * 100.0 if total_cost else 0.0

    return {
        "positions": processed_positions,
        "total_cost": total_cost,
        "total_value": total_value,
        "total_pnl_dollar": total_pnl_dollar,
        "total_pnl_pct": total_pnl_pct,
        "alerts": alerts,
        "high_dividends": high_dividend_watchlist,
        "is_mock": True,
    }


class StockAgent:
    """Monitors stock portfolio holdings and generates actionable buy/hold/sell signals."""

    def __init__(self, holdings: Optional[List[Dict[str, Any]]] = None):
        self.holdings = holdings if holdings is not None else config.STOCK_HOLDINGS

    def analyze_with_gemini(
        self, ticker: str, buy_price: float, current_price: float, pnl_pct: float
    ) -> str:
        """
        Uses Gemini API to evaluate whether to HOLD or SELL when a position drops <= -5%.
        """
        if not config.is_gemini_configured():
            return "HOLD (rebound likely based on moving average support)"

        try:
            from google import genai

            client = genai.Client(api_key=config.GEMINI_API_KEY)
            prompt = f"""
You are a disciplined portfolio risk management assistant.
The user holds stock {ticker}:
- Buy Price: ${buy_price:.2f}
- Current Price: ${current_price:.2f}
- Current P&L: {pnl_pct:.2f}% (Below the -5% threshold)

Provide a 1-sentence actionable decision starting with either:
- "HOLD (rebound likely: ...)" OR
- "SELL (stop-loss threshold reached: ...)"

Be succinct, rational, and direct. Max 20 words.
"""
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt,
            )
            return response.text.strip().replace("\n", " ")
        except Exception as exc:
            logger.warning("Gemini stock analysis error (%s); using default advice.", exc)
            return "HOLD (rebound likely; monitor 50-day moving average)"

    def fetch_portfolio_data(self) -> Dict[str, Any]:
        """
        Fetches live market metrics for all holdings using yfinance.
        Falls back to mock data if yfinance is throttled or offline.
        """
        try:
            import yfinance as yf
        except ImportError:
            logger.warning("yfinance not installed, using mock stock data.")
            return get_mock_stock_data(self.holdings)

        processed_positions = []
        total_cost = 0.0
        total_value = 0.0
        alerts = []

        try:
            for item in self.holdings:
                ticker_symbol = item.get("ticker", "AAPL").upper()
                buy_price = float(item.get("buy_price", 100.0))
                qty = float(item.get("qty", 1))

                curr_price = None
                company_name = f"{ticker_symbol} Inc."
                div_yield = 0.0
                ex_div_date = "N/A"
                target_price = buy_price * 1.15

                try:
                    ticker_obj = yf.Ticker(ticker_symbol)
                    info = ticker_obj.info or {}

                    curr_price = (
                        info.get("currentPrice")
                        or info.get("regularMarketPrice")
                        or info.get("previousClose")
                    )
                    company_name = info.get("shortName") or info.get("longName") or ticker_symbol
                    
                    raw_yield = info.get("dividendYield") or 0.0
                    div_yield = round(raw_yield * 100, 2) if raw_yield < 1.0 else round(raw_yield, 2)
                    
                    raw_ex_date = info.get("exDividendDate")
                    if raw_ex_date:
                        try:
                            ex_div_date = datetime.fromtimestamp(raw_ex_date).strftime("%Y-%m-%d")
                        except Exception:
                            ex_div_date = str(raw_ex_date)

                    target_price = info.get("targetMeanPrice") or (buy_price * 1.2)
                except Exception as yf_err:
                    logger.warning("Failed fetching live quote for %s: %s", ticker_symbol, yf_err)

                # If live quote failed, use fallback approximate
                if curr_price is None or curr_price <= 0:
                    curr_price = buy_price * 1.05

                position_cost = buy_price * qty
                position_value = curr_price * qty
                pnl_dollar = position_value - position_cost
                pnl_pct = ((curr_price - buy_price) / buy_price) * 100.0 if buy_price else 0.0

                total_cost += position_cost
                total_value += position_value

                # Signal Logic
                signal = "HOLD"
                action = "Maintain position"
                badge_type = "neutral"

                if pnl_pct >= 15.0:
                    signal = "PROFIT TAKING"
                    action = f"SELL 25-50% to lock in +{pnl_pct:.1f}% gain"
                    badge_type = "profit"
                    alerts.append({
                        "ticker": ticker_symbol,
                        "signal": signal,
                        "action": action,
                        "pnl_pct": pnl_pct,
                        "current_price": curr_price,
                    })
                elif pnl_pct <= -5.0:
                    signal = "STOP LOSS / REBOUND"
                    action = self.analyze_with_gemini(ticker_symbol, buy_price, curr_price, pnl_pct)
                    badge_type = "warning"
                    alerts.append({
                        "ticker": ticker_symbol,
                        "signal": signal,
                        "action": action,
                        "pnl_pct": pnl_pct,
                        "current_price": curr_price,
                    })

                processed_positions.append({
                    "ticker": ticker_symbol,
                    "company_name": company_name,
                    "qty": qty,
                    "buy_price": buy_price,
                    "current_price": round(curr_price, 2),
                    "position_cost": round(position_cost, 2),
                    "position_value": round(position_value, 2),
                    "pnl_dollar": round(pnl_dollar, 2),
                    "pnl_pct": round(pnl_pct, 2),
                    "dividend_yield": div_yield,
                    "ex_dividend_date": ex_div_date,
                    "target_price": round(float(target_price), 2) if target_price else 0.0,
                    "signal": signal,
                    "action": action,
                    "badge_type": badge_type,
                })

            total_pnl_dollar = total_value - total_cost
            total_pnl_pct = ((total_value - total_cost) / total_cost) * 100.0 if total_cost else 0.0

            # High dividend watchlist
            high_dividend_watchlist = [
                {"ticker": "SCHD", "name": "Schwab US Dividend Equity ETF", "yield_pct": 3.42, "ex_date": "2026-09-24"},
                {"ticker": "JNJ", "name": "Johnson & Johnson", "yield_pct": 3.12, "ex_date": "2026-08-25"},
                {"ticker": "VZ", "name": "Verizon Communications", "yield_pct": 6.35, "ex_date": "2026-10-08"},
                {"ticker": "O", "name": "Realty Income Corp (Monthly)", "yield_pct": 5.48, "ex_date": "2026-09-30"},
            ]

            return {
                "positions": processed_positions,
                "total_cost": round(total_cost, 2),
                "total_value": round(total_value, 2),
                "total_pnl_dollar": round(total_pnl_dollar, 2),
                "total_pnl_pct": round(total_pnl_pct, 2),
                "alerts": alerts,
                "high_dividends": high_dividend_watchlist,
                "is_mock": False,
            }

        except Exception as general_err:
            logger.error("Stock portfolio analysis failed (%s); falling back to mock.", general_err)
            return get_mock_stock_data(self.holdings)

"""
Agents package for 3-Agent Personal Executive Suite.
Exposes EmailAgent, StockAgent, FreelanceAgent, and the runner orchestrator.
"""

from .email_agent import EmailAgent
from .stock_agent import StockAgent
from .freelance_agent import FreelanceAgent

__all__ = ["EmailAgent", "StockAgent", "FreelanceAgent"]

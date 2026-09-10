"""
Freelance Job Hunter & ROI Evaluator Agent.
Fetches live RSS feeds from RemoteOK, WeWorkRemotely, etc.
Uses Google Gemini API to calculate ROI Score (1-10), Skill Match % against
user capabilities (Python, React, FastAPI, Web Scraping), and drafts tailored proposals
for high-ROI opportunities (ROI >= 8.0).
Includes clean fallback mocks if offline or unconfigured.
"""

import json
import logging
import re
from typing import List, Dict, Any, Optional
import requests
import feedparser

import config

logger = logging.getLogger("freelance_agent")


def get_mock_freelance_jobs() -> List[Dict[str, Any]]:
    """Provides high-quality mock freelance opportunities for immediate testing."""
    return [
        {
            "id": "job_mock_1",
            "title": "Senior Python & AI Agent Developer for Automated Lead Generation Pipeline",
            "company": "GrowthScale AI",
            "source": "RemoteOK",
            "link": "https://remoteok.com/remote-jobs/growthscale-ai-lead-pipeline",
            "published": "2 hours ago",
            "budget": "$5,000 - $8,000 (Fixed Price)",
            "summary": "Building an autonomous multi-agent system using Python, Gemini/Claude LLMs, and Web Scraping to scrape business directories, score leads, and trigger automated outreach.",
            "skills_detected": ["Python", "Web Scraping", "AI Agents", "FastAPI"],
            "skill_match_pct": 95,
            "roi_score": 9.2,
            "proposal": (
                "Hi GrowthScale Team,\n\n"
                "I read your project requirements with excitement. I specialize in building autonomous multi-agent systems "
                "in Python leveraging the latest Gemini models, robust Web Scraping pipelines, and FastAPI microservices.\n\n"
                "Here is my proposed approach:\n"
                "1. Architect resilient scrapers with automatic retry and rate-limiting.\n"
                "2. Implement a multi-agent evaluation pipeline with structured JSON outputs.\n"
                "3. Deploy a lightweight monitoring dashboard.\n\n"
                "I have delivered similar autonomous pipelines with high uptime. Let's connect for a quick 10-minute discovery call!"
            ),
        },
        {
            "id": "job_mock_2",
            "title": "FastAPI & React Dashboard for Real-Time Financial Market Analytics",
            "company": "AlphaVault Ventures",
            "source": "WeWorkRemotely",
            "link": "https://weworkremotely.com/jobs/alphavault-fastapi-react-dashboard",
            "published": "4 hours ago",
            "budget": "$80 - $110 / hour",
            "summary": "Looking for a Full-Stack Python developer to build a modern, high-speed financial analytics dashboard connecting to market data streams with FastAPI backend and responsive React frontend.",
            "skills_detected": ["Python", "FastAPI", "React"],
            "skill_match_pct": 88,
            "roi_score": 8.5,
            "proposal": (
                "Hi AlphaVault Team,\n\n"
                "Your project aligns directly with my core stack. I build high-performance data applications with FastAPI "
                "backends, asynchronous websockets, and clean React dashboards with modern light/dark aesthetics.\n\n"
                "I would love to help you build an ultra-responsive analytics portal that feels snappy and reliable.\n"
                "When would be a convenient time to discuss your current data pipeline and sprint milestones?"
            ),
        },
        {
            "id": "job_mock_3",
            "title": "Web Scraping Specialist for Large-Scale E-Commerce Price Intelligence",
            "company": "RetailMetrics Co.",
            "source": "RemoteOK",
            "link": "https://remoteok.com/remote-jobs/retailmetrics-scraping-engineer",
            "published": "6 hours ago",
            "budget": "$3,500 (Milestone-based)",
            "summary": "Need an expert Python scraper to extract product pricing, inventory status, and competitor promotional banners from 20+ e-commerce platforms on a daily schedule.",
            "skills_detected": ["Python", "Web Scraping"],
            "skill_match_pct": 78,
            "roi_score": 7.4,
            "proposal": "",
        },
        {
            "id": "job_mock_4",
            "title": "Mobile App UI Developer (Flutter / React Native)",
            "company": "Orbit Labs",
            "source": "WeWorkRemotely",
            "link": "https://weworkremotely.com/jobs/orbit-mobile-engineer",
            "published": "8 hours ago",
            "budget": "$4,000 / month",
            "summary": "Looking for a mobile engineer experienced with cross-platform frameworks to implement onboarding screens and social authentication flows.",
            "skills_detected": ["Mobile", "UI"],
            "skill_match_pct": 35,
            "roi_score": 5.1,
            "proposal": "",
        },
    ]


class FreelanceAgent:
    """Scrapes RSS feeds, scores freelance jobs with Gemini LLM, and creates proposals."""

    def __init__(self, user_skills: Optional[List[str]] = None):
        self.user_skills = user_skills or config.USER_SKILLS
        self.feeds = config.FREELANCE_RSS_FEEDS

    def fetch_raw_feed_jobs(self, limit_per_feed: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches job listings from RSS feeds using a friendly User-Agent header.
        """
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        all_jobs = []

        for feed_url in self.feeds:
            try:
                logger.info("Fetching RSS feed: %s", feed_url)
                resp = requests.get(feed_url, headers=headers, timeout=10)
                if resp.status_code != 200:
                    logger.warning("Feed %s returned status %s", feed_url, resp.status_code)
                    continue

                parsed = feedparser.parse(resp.content)
                source_name = "RemoteOK" if "remoteok" in feed_url else "WeWorkRemotely"

                for entry in parsed.entries[:limit_per_feed]:
                    title = entry.get("title", "Untitled Job")
                    link = entry.get("link", "#")
                    published = entry.get("published", "Recent")
                    raw_summary = entry.get("summary", "") or entry.get("description", "")
                    # Clean html tags from summary
                    clean_desc = re.sub(r"<[^>]+>", " ", raw_summary)
                    clean_desc = " ".join(clean_desc.split())[:1500]

                    all_jobs.append({
                        "id": link or title,
                        "title": title,
                        "company": source_name,
                        "source": source_name,
                        "link": link,
                        "published": published,
                        "budget": "Competitive / Inquire",
                        "summary": clean_desc,
                    })
            except Exception as exc:
                logger.warning("Failed fetching feed %s: %s", feed_url, exc)
                continue

        return all_jobs

    def evaluate_job_with_gemini(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses Google Gemini to evaluate job ROI, calculate skill match %,
        and generate a high-converting proposal if ROI >= 8.0.
        """
        if not config.is_gemini_configured():
            return self._heuristic_evaluation(job)

        try:
            from google import genai

            client = genai.Client(api_key=config.GEMINI_API_KEY)
            skills_str = ", ".join(self.user_skills)

            prompt = f"""
You are an executive freelance agent evaluating a job opportunity for a senior software developer.

Candidate Skills: {skills_str}

Job Details:
- Title: {job.get('title')}
- Source: {job.get('source')}
- Description:
\"\"\"{job.get('summary')}\"\"\"

Analyze this opportunity and reply ONLY with a valid JSON object matching this schema:
{{
  "roi_score": 8.5,            // Float from 1.0 to 10.0 (evaluating budget/reward vs estimated effort)
  "skill_match_pct": 90,       // Integer from 0 to 100 representing overlap with candidate skills
  "skills_detected": ["Python", "FastAPI"], // Key required technical skills found in the post
  "budget_extracted": "$5,000 - $8,000" or "Hourly rate" or "Competitive",
  "proposal": "If roi_score >= 8.0, write a persuasive, concise 3-paragraph tailored proposal highlighting our skills. If roi_score < 8.0, set this to an empty string."
}}

No markdown fences, no explanatory text, return pure JSON only.
"""
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt,
            )

            raw_text = response.text.strip()
            clean_json = re.sub(r"^```json\s*", "", raw_text)
            clean_json = re.sub(r"^```\s*", "", clean_json)
            clean_json = re.sub(r"\s*```$", "", clean_json).strip()

            data = json.loads(clean_json)

            job["roi_score"] = float(data.get("roi_score", 6.5))
            job["skill_match_pct"] = int(data.get("skill_match_pct", 60))
            job["skills_detected"] = data.get("skills_detected", [])
            if data.get("budget_extracted"):
                job["budget"] = data["budget_extracted"]
            job["proposal"] = data.get("proposal", "")

            return job

        except Exception as exc:
            logger.warning("Gemini job evaluation error (%s); falling back to heuristic.", exc)
            return self._heuristic_evaluation(job)

    def _heuristic_evaluation(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates rough match and ROI when LLM is unavailable."""
        text = f"{job.get('title', '')} {job.get('summary', '')}".lower()
        matched = []
        for skill in self.user_skills:
            if skill.lower() in text:
                matched.append(skill)

        match_count = len(matched)
        match_pct = min(100, int((match_count / max(1, len(self.user_skills))) * 120))
        roi_score = round(min(10.0, 4.0 + (match_count * 1.5)), 1)

        job["roi_score"] = roi_score
        job["skill_match_pct"] = match_pct
        job["skills_detected"] = matched
        
        if roi_score >= 8.0:
            skills_joined = ", ".join(matched) if matched else "Python and Full-Stack Engineering"
            job["proposal"] = (
                f"Hi there,\n\n"
                f"I came across your listing for '{job.get('title')}' and believe my background in {skills_joined} "
                f"is a strong fit. I have built reliable production systems with clean architectures.\n\n"
                f"I'd be glad to discuss your milestones and see how we can collaborate.\n\n"
                f"Best regards."
            )
        else:
            job["proposal"] = ""

        return job

    def get_evaluated_jobs(self, max_jobs: int = 8) -> List[Dict[str, Any]]:
        """
        Full workflow:
        1. Fetches raw jobs from RSS feeds.
        2. Falls back to realistic mock jobs if feeds return empty.
        3. Evaluates with Gemini (or heuristic fallback).
        4. Sorts by ROI Score descending.
        """
        raw_jobs = self.fetch_raw_feed_jobs(limit_per_feed=4)
        if not raw_jobs:
            logger.info("No raw RSS jobs retrieved; serving curated mock opportunities.")
            return get_mock_freelance_jobs()

        evaluated = []
        for job in raw_jobs[:max_jobs]:
            evaluated.append(self.evaluate_job_with_gemini(job))

        # Sort by highest ROI first
        evaluated.sort(key=lambda x: x.get("roi_score", 0), reverse=True)
        return evaluated

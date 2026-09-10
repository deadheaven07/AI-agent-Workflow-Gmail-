"""
Email Triage & Summarizer Agent.
Connects via imaplib to fetch unread emails.
Categorizes into URGENT, IMPORTANT, LOW_PRIORITY, extracts action items,
and drafts concise response recommendations using the Google Gemini API.
Includes clean fallback mocks if credentials are not configured.
"""

import email
from email.header import decode_header
import imaplib
import json
import logging
import re
from typing import List, Dict, Any, Optional

import config

logger = logging.getLogger("email_agent")


def _clean_header(header_val: Any) -> str:
    """Decodes email headers safely handling charset encodings."""
    if not header_val:
        return ""
    decoded_fragments = decode_header(header_val)
    parts = []
    for fragment, charset in decoded_fragments:
        if isinstance(fragment, bytes):
            try:
                parts.append(fragment.decode(charset or "utf-8", errors="replace"))
            except Exception:
                parts.append(fragment.decode("latin-1", errors="replace"))
        else:
            parts.append(str(fragment))
    return " ".join(parts).strip()


def _extract_body_text(msg: email.message.Message) -> str:
    """Extracts plain text body from email payload."""
    body_parts = []
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    body_parts.append(payload.decode("utf-8", errors="replace"))
            elif content_type == "text/html" and not body_parts and "attachment" not in content_disposition:
                # If no plain text yet, strip basic HTML tags as fallback
                payload = part.get_payload(decode=True)
                if payload:
                    html_text = payload.decode("utf-8", errors="replace")
                    cleaned = re.sub(r"<[^>]+>", " ", html_text)
                    body_parts.append(" ".join(cleaned.split()))
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body_parts.append(payload.decode("utf-8", errors="replace"))

    full_body = "\n".join(body_parts).strip()
    return full_body[:2500]  # Limit tokens for fast processing


def get_mock_emails() -> List[Dict[str, Any]]:
    """Provides realistic unread email data for demos and fallback testing."""
    return [
        {
            "id": "mock_1",
            "sender": "sarah.jenkins@acmecorp.com",
            "sender_name": "Sarah Jenkins (Acme Corp VP)",
            "subject": "CRITICAL: Q3 Contract Renewal Sign-Off Required by 5 PM",
            "date": "Today at 09:14 AM",
            "body": "Hi, we are closing the Q3 books today and need your final sign-off on the Master Services Agreement addendum before 5:00 PM EST. Legal has cleared all terms. Please confirm or provide amended terms immediately.",
            "priority": "URGENT",
            "summary": "Urgent sign-off needed for Q3 Master Services Agreement renewal by 5:00 PM EST today. Legal already approved.",
            "action_items": [
                "Review MSA addendum legal terms",
                "Reply with signed approval or amended conditions before 5 PM EST",
            ],
            "draft_reply": "Hi Sarah, thank you for following up. I am reviewing the cleared MSA terms now and will send over the executed sign-off well before the 5 PM EST deadline.",
        },
        {
            "id": "mock_2",
            "sender": "david.chen@fintechpulse.io",
            "sender_name": "David Chen (FinTech Pulse)",
            "subject": "Partnership Proposal: AI Automation Architecture Consultation",
            "date": "Today at 08:30 AM",
            "body": "Hi there! We loved your recent showcase on autonomous multi-agent pipelines. We have an upcoming client project requiring an executive triage setup. Would you be open for a 20-minute intro call this Thursday at 2 PM PST to discuss advisory scope?",
            "priority": "IMPORTANT",
            "summary": "Fintech Pulse requested a 20-minute exploratory advisory call this Thursday at 2 PM PST to discuss AI automation architecture.",
            "action_items": [
                "Check calendar availability for Thursday at 2 PM PST",
                "Respond with confirmation link or alternate time slots",
            ],
            "draft_reply": "Hi David, thanks for reaching out! I'd be glad to discuss the AI architecture advisory scope. Thursday at 2 PM PST works on my end—I will send an invite shortly.",
        },
        {
            "id": "mock_3",
            "sender": "updates@github.com",
            "sender_name": "GitHub Notifications",
            "subject": "[GitHub] 4 security alerts detected in automated dependencies",
            "date": "Yesterday at 11:20 PM",
            "body": "Dependabot detected moderate severity vulnerabilities in 2 repository dependencies. Automated pull requests have been generated for review.",
            "priority": "LOW_PRIORITY",
            "summary": "Dependabot flagged 4 moderate dependency vulnerabilities; automated PRs are ready for merge.",
            "action_items": [
                "Review automated Dependabot PRs during scheduled weekly maintenance",
            ],
            "draft_reply": "N/A - Automated notification.",
        },
        {
            "id": "mock_4",
            "sender": "newsletter@tldr.tech",
            "sender_name": "TLDR Tech Daily",
            "subject": "TLDR Tech: The rise of autonomous local AI agents & LLM benchmarks",
            "date": "Yesterday at 04:00 PM",
            "body": "Today's top tech news covering open-weights model breakthroughs, new developer tools, and semiconductor earnings reports.",
            "priority": "LOW_PRIORITY",
            "summary": "Daily technology briefing covering autonomous agents, LLM benchmarks, and semiconductor news.",
            "action_items": [],
            "draft_reply": "N/A - Newsletter subscription.",
        },
    ]


class EmailAgent:
    """Orchestrates IMAP email fetching and Gemini-powered email triage."""

    def __init__(self):
        self.server = config.IMAP_SERVER
        self.port = config.IMAP_PORT
        self.user = config.IMAP_USER
        self.password = config.IMAP_PASSWORD

    def fetch_raw_unread_emails(self, max_emails: int = 8) -> List[Dict[str, Any]]:
        """
        Connects to IMAP server over SSL and retrieves unread emails.
        Returns a list of raw email dictionaries.
        """
        if not config.is_email_configured():
            logger.info("IMAP credentials not configured; using realistic mock emails.")
            return []

        emails = []
        mail = None
        try:
            logger.info("Connecting to IMAP %s:%s for user %s", self.server, self.port, self.user)
            mail = imaplib.IMAP4_SSL(self.server, self.port, timeout=12)
            mail.login(self.user, self.password)
            mail.select("INBOX", readonly=True)

            status, search_data = mail.search(None, "UNSEEN")
            if status != "OK" or not search_data or not search_data[0]:
                logger.info("No unread emails found in INBOX.")
                return []

            email_ids = search_data[0].split()
            # Fetch the most recent unread emails up to max_emails
            recent_ids = email_ids[-max_emails:]
            recent_ids.reverse()

            for eid in recent_ids:
                try:
                    res, msg_data = mail.fetch(eid, "(RFC822)")
                    if res != "OK" or not msg_data:
                        continue
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    sender = _clean_header(msg.get("From", "Unknown"))
                    subject = _clean_header(msg.get("Subject", "(No Subject)"))
                    date_str = _clean_header(msg.get("Date", ""))
                    body = _extract_body_text(msg)

                    emails.append({
                        "id": eid.decode("utf-8", errors="ignore"),
                        "sender": sender,
                        "sender_name": sender.split("<")[0].strip() or sender,
                        "subject": subject,
                        "date": date_str,
                        "body": body,
                    })
                except Exception as parse_err:
                    logger.warning("Error parsing email ID %s: %s", eid, parse_err)
                    continue

        except Exception as exc:
            logger.error("IMAP connection/authentication failed: %s", exc)
            return []
        finally:
            if mail:
                try:
                    mail.close()
                    mail.logout()
                except Exception:
                    pass

        return emails

    def triage_with_gemini(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes an email using the Google Gemini API to produce:
        - Priority (URGENT, IMPORTANT, LOW_PRIORITY)
        - Brief 1-2 sentence executive summary
        - Key Action Items
        - Auto-drafted concise reply
        """
        if not config.is_gemini_configured():
            return self._heuristic_triage(email_data)

        try:
            from google import genai

            client = genai.Client(api_key=config.GEMINI_API_KEY)
            prompt = f"""
You are an executive assistant AI analyzing an incoming email.

Sender: {email_data.get('sender')}
Subject: {email_data.get('subject')}
Date: {email_data.get('date')}
Body:
\"\"\"{email_data.get('body')}\"\"\"

Analyze this email and respond with ONLY a valid JSON object matching this exact schema:
{{
  "priority": "URGENT" | "IMPORTANT" | "LOW_PRIORITY",
  "summary": "1-2 sentence executive summary of the email",
  "action_items": ["List of clear, actionable tasks required, or empty array if none"],
  "draft_reply": "A concise, professional, ready-to-send draft reply, or 'N/A' if newsletter/automated"
}}

Guidelines:
- "URGENT": Deadlines today/tomorrow, billing/contract issues, emergencies, VIP client escalations.
- "IMPORTANT": Business proposals, meetings, scheduled tasks, meaningful communications.
- "LOW_PRIORITY": Newsletters, automated alerts, promotions, cold outreach.
Return pure JSON only, no markdown backticks, no commentary.
"""
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt,
            )

            response_text = response.text.strip()
            # Clean possible markdown blocks
            clean_json = re.sub(r"^```json\s*", "", response_text)
            clean_json = re.sub(r"^```\s*", "", clean_json)
            clean_json = re.sub(r"\s*```$", "", clean_json).strip()

            parsed = json.loads(clean_json)
            email_data["priority"] = parsed.get("priority", "IMPORTANT").upper()
            email_data["summary"] = parsed.get("summary", email_data.get("subject", ""))
            email_data["action_items"] = parsed.get("action_items", [])
            email_data["draft_reply"] = parsed.get("draft_reply", "")
            return email_data

        except Exception as exc:
            logger.warning("Gemini email triage failed (%s); using heuristic fallback.", exc)
            return self._heuristic_triage(email_data)

    def _heuristic_triage(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based fallback triage when LLM is unavailable."""
        subject = email_data.get("subject", "").lower()
        body = email_data.get("body", "").lower()
        sender = email_data.get("sender", "").lower()
        text = f"{subject} {body} {sender}"

        urgent_triggers = ["urgent", "asap", "deadline", "critical", "action required", "immediate", "today"]
        important_triggers = ["proposal", "meeting", "contract", "invoice", "schedule", "call", "project", "review"]
        low_triggers = ["newsletter", "unsubscribe", "notification", "digest", "no-reply", "marketing", "promotion"]

        if any(w in text for w in urgent_triggers):
            priority = "URGENT"
        elif any(w in text for w in low_triggers):
            priority = "LOW_PRIORITY"
        elif any(w in text for w in important_triggers):
            priority = "IMPORTANT"
        else:
            priority = "IMPORTANT"

        email_data["priority"] = priority
        email_data["summary"] = email_data.get("subject", "")
        email_data["action_items"] = [f"Review message from {email_data.get('sender_name', 'sender')}"]
        email_data["draft_reply"] = (
            "Hi, thank you for reaching out. I received your message and will review it shortly."
            if priority != "LOW_PRIORITY"
            else "N/A"
        )
        return email_data

    def get_triaged_emails(self, max_emails: int = 6) -> List[Dict[str, Any]]:
        """
        Full workflow:
        1. Attempts to fetch real unread emails.
        2. If empty or unconfigured, falls back to realistic mock emails.
        3. Triages through Gemini or fallback logic.
        4. Sorts by priority (URGENT > IMPORTANT > LOW_PRIORITY).
        """
        raw_emails = self.fetch_raw_unread_emails(max_emails=max_emails)
        if not raw_emails:
            # Return pre-triaged mock emails with fresh timestamps
            return get_mock_emails()

        triaged = []
        for item in raw_emails:
            triaged.append(self.triage_with_gemini(item))

        # Sort order
        rank = {"URGENT": 0, "IMPORTANT": 1, "LOW_PRIORITY": 2}
        triaged.sort(key=lambda x: rank.get(x.get("priority", "LOW_PRIORITY"), 3))
        return triaged

"""The LLM client. You don't need to change this file.

Two backends behind one async interface:
- StubLLM (default): offline and deterministic. Most complaints get valid JSON. Three complaints
  get the kinds of bad output real models produce, so you can see your contract catch them.
- LiveLLM: any OpenAI-compatible endpoint, used only when LLM_API_KEY or GEMINI_API_KEY is set
  (as a Codespaces or Colab secret, never in code).

Everything here is fictional: Example Bank, its customers, accounts and teams.
"""

from __future__ import annotations

import asyncio
import json
import os
import time

PROMPT_VERSION = "triage-v1"

# Complaints that get bad model output from the stub, and what goes wrong.
BAD_OUTPUT = {
    "C-013": "wrong_types",   # priority "urgent" instead of 1-4, team "fraud ops" instead of fraud_ops
    "C-014": "missing_field",  # no "team"
    "C-015": "prose_wrapper",  # "Sure! Here is the JSON: {...}"
}

_RULES = [  # (keywords, category, team, priority); first match wins
    (("did not make", "nahi kiya", "unauthorised", "unauthorized", "otp", "scam", "fraud", "never raised", "kyc"),
     "fraud", "fraud_ops", 1),
    (("charged twice", "swiped", "dispute", "refund", "kat gaye"), "card_dispute", "disputes", 2),
    (("locked", "log in", "login", "password", "app crash", "net banking"), "account_access", "digital_support", 3),
    (("fee", "charges", "penalty"), "charges", "branch_services", 3),
]


def _classify(text: str) -> dict:
    t = text.lower()
    for words, category, team, priority in _RULES:
        if any(w in t for w in words):
            break
    else:
        category, team, priority = "other", "branch_services", 4
    summary = text if len(text) <= 120 else text[:117] + "..."
    return {"category": category, "priority": priority, "team": team, "summary": summary}


def _stub_output(complaint_id: str, text: str) -> str:
    out = _classify(text)
    kind = BAD_OUTPUT.get(complaint_id)
    if kind == "wrong_types":
        out.update(priority="urgent", team="fraud ops")
    elif kind == "missing_field":
        out.pop("team")
    if kind == "prose_wrapper":
        return "Sure! Here is the JSON you asked for:\n" + json.dumps(out)
    return json.dumps(out)


class StubLLM:
    """Offline model. `delay` simulates a slow network call (seconds)."""

    name = "stub"
    model = "stub-triage-1"

    def __init__(self, delay: float = 0.0):
        self.delay = delay

    async def complete(self, complaint_id: str, text: str) -> str:
        """Non-blocking: other requests keep running while this one waits."""
        if self.delay:
            await asyncio.sleep(self.delay)
        return _stub_output(complaint_id, text)

    def complete_blocking(self, complaint_id: str, text: str) -> str:
        """Blocking version, like a sync SDK call. Used to show what NOT to do inside async code."""
        if self.delay:
            time.sleep(self.delay)
        return _stub_output(complaint_id, text)


SYSTEM_PROMPT = (
    "You triage bank complaints. Reply with JSON only, with keys: "
    'category (one of "card_dispute", "fraud", "account_access", "charges", "other"), '
    "priority (integer 1-4, 1 = most urgent), "
    'team (one of "disputes", "fraud_ops", "digital_support", "branch_services"), '
    "summary (at most 200 characters, no account numbers)."
)


class LiveLLM:
    """A real model through an OpenAI-compatible endpoint (Gemini by default)."""

    name = "live"

    def __init__(self):
        from openai import AsyncOpenAI  # imported here so the stub works without network

        self.model = os.environ.get("LLM_MODEL", "gemini-3.8-flash")
        self._client = AsyncOpenAI(
            api_key=os.environ.get("LLM_API_KEY") or os.environ["GEMINI_API_KEY"],
            base_url=os.environ.get("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
            timeout=4,  # below the service's own 5 s budget (TRIAGE_TIMEOUT_S), so the SDK gives up first
            max_retries=1,
        )

    async def complete(self, complaint_id: str, text: str) -> str:
        resp = await self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": text}],
            temperature=0,
        )
        return resp.choices[0].message.content or ""


def get_llm():
    """LiveLLM if a key is set (and FORCE_OFFLINE isn't), otherwise StubLLM."""
    has_key = os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if has_key and os.environ.get("FORCE_OFFLINE") != "1":
        return LiveLLM()
    return StubLLM()

"""L3 Observability: one JSON log line per request, with account numbers masked. (Solution.)"""

from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime, timezone

logger = logging.getLogger("triage")

ACCOUNT_RE = re.compile(r"\bEB-\d{10}\b")  # Example Bank account numbers (fictional format)
FIELDS = ("request_id", "route", "status", "latency_ms", "model", "prompt_version", "outcome", "complaint_excerpt")


def mask(text: str) -> str:
    """EB-4418203391 -> EB-******3391"""
    return ACCOUNT_RE.sub(lambda m: "EB-******" + m.group(0)[-4:], text)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "msg": record.getMessage(),
        }
        for field in FIELDS:
            if hasattr(record, field):
                entry[field] = getattr(record, field)
        return mask(json.dumps(entry, ensure_ascii=False))  # mask the whole line: no field can leak


def setup_logging(stream=None, level: str = "INFO") -> logging.Logger:
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.handlers = [handler]
    logger.setLevel(level)
    logger.propagate = False
    return logger

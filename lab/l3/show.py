"""L3 · step 3: read the fix, straight from the files step 4 will copy in."""
from _common import chain, code

chain("""  bash lab.sh l3 show
    └─ python lab/l3/show.py
         └─ prints the finished logging code from lab/l3/logging_done.py and lab/l3/main_done.py,
            with real line numbers. Step 4 copies these over app/logging_setup.py and app/main.py.""")
code("lab/l3/logging_done.py", "ACCOUNT_RE =", "FIELDS =", "What we mask, and which fields a line may carry",
     {"ACCOUNT_RE": "EB- plus 10 digits (fictional account format)", "FIELDS": "the audit fields"})
code("lab/l3/logging_done.py", "def mask(", "return ACCOUNT_RE.sub(", "L3.1  mask()",
     {"return ACCOUNT_RE.sub(": "keep the last 4 digits: EB-******3391"})
code("lab/l3/logging_done.py", "class JsonFormatter", "return mask(json.dumps(", "L3.2  One JSON line per log record",
     {'"ts":': "UTC timestamp", "for field in FIELDS": "copy each audit field the record carries",
      "return mask(json.dumps(": "mask the WHOLE line, so no field can leak"})
code("lab/l3/main_done.py", "setup_logging()", "setup_logging()", "Turn it on, once",
     {"setup_logging()": "the 'triage' logger now writes JSON lines to stdout"})
code("lab/l3/main_done.py", '@app.middleware("http")', "return response", "L3.3  Middleware: one line per request",
     {'@app.middleware("http")': "wraps EVERY request, so nothing depends on remembering to log",
      'request.headers.get("X-Request-ID")': "the caller's ID, or a new one",
      "request.state.log = {}": "triage() fills this in (L3.4)",
      'response.headers["X-Request-ID"]': "echo the ID, so systems can follow it",
      "logger.info(": "the one line: route, status, latency, plus triage's fields"})
code("lab/l3/main_done.py", "request.state.log = {", '"complaint_excerpt"', "L3.4  What only triage() knows",
     {'"model"': "which model decided", '"prompt_version"': "which prompt", '"outcome"': "routed or human_review"})
print("Next: bash lab.sh l3 apply")

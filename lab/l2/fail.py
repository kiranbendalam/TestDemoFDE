"""L2 · step 1: see it fail. The prototype is a script nobody can call, and app/main.py's endpoints are still TODOs."""
from _common import ROOT, chain, client, code, ensure_l1

chain("""  bash lab.sh l2 fail
    └─ python lab/l2/fail.py
         ├─ A. shows how triage_prototype.py starts: as a script, with no web endpoint
         └─ B. sends two requests to the real service, app/main.py, through FastAPI's TestClient
              (no server needed), then shows the lines that answered
  No real LLM: app/llm.py's StubLLM answers offline.""")
ensure_l1()

print("━━ A. The prototype is a script ━━\n")
code("triage_prototype.py", 'if __name__ == "__main__":', "main()", "How it runs: only from a terminal")
print("  There's no URL the case system can call, and nothing the platform can probe. That's the Sr. Platform\n"
      "  Engineer's 'we don't run scripts'.\n")

if "NotImplementedError" not in (ROOT / "app/main.py").read_text():
    print("━━ B. The service, app/main.py ━━\n")
    print("  L2 is already applied in app/main.py, so there's nothing failing to show.\n"
          "  To see it fail again: bash lab.sh reset l2   then   bash lab.sh l2 fail\n")
    raise SystemExit(0)
print("━━ B. The service, app/main.py, before L2 ━━\n")
c = client()
for method, path, body in [("GET", "/healthz", None), ("POST", "/triage", {"id": "C-002", "text": "Two card transactions I did not make"})]:
    r = c.request(method, path, json=body)
    print(f"  {method} {path}" + (f"  body={body}" if body else "") + f"\n    -> {r.status_code} {r.reason_phrase}  {r.text[:80]}\n")
code("app/main.py", '@app.get("/healthz")', 'raise NotImplementedError("L2.1")', "Why /healthz fails")
code("app/main.py", '@app.post("/triage"', 'raise NotImplementedError("L2.2")', "Why /triage fails")
print("""WHAT WENT WRONG
  Both endpoints exist (FastAPI already lists them), but their bodies raise NotImplementedError,
  so every call gets a 500. A platform health check would mark this service as down.
""")

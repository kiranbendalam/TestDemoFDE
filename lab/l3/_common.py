"""Shared bits for L3 steps: view helpers, guards that L1 and L2 are in place, and a client whose logs we capture."""
import io
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE.parent / "l1"))
from _view import chain, code  # noqa: E402,F401


def ensure_l1_l2():
    """L3 builds on L1 (app/models.py) and L2 (app/main.py). Copy their finished files in if they're still TODOs."""
    if "NotImplementedError" in (ROOT / "app/models.py").read_text():
        shutil.copyfile(HERE.parent / "l1/models_done.py", ROOT / "app/models.py")
        print("  NOTE: L3 needs L1's contract: copied lab/l1/models_done.py -> app/models.py")
    if 'NotImplementedError("L2' in (ROOT / "app/main.py").read_text():
        shutil.copyfile(HERE.parent / "l2/main_done.py", ROOT / "app/main.py")
        print("  NOTE: L3 needs L2's endpoints: copied lab/l2/main_done.py -> app/main.py")


def l3_done():
    return "NotImplementedError" not in (ROOT / "app/logging_setup.py").read_text() and "TODO (L3" not in (ROOT / "app/main.py").read_text()


def logged_client():
    """The real app with StubLLM; the 'triage' logger writes into a buffer we can read back (as tests/test_l3.py does)."""
    import app.main as main
    from app.llm import StubLLM
    from app.logging_setup import setup_logging
    from fastapi.testclient import TestClient
    main.llm = StubLLM()
    buf = io.StringIO()
    setup_logging(stream=buf)
    return TestClient(main.app, raise_server_exceptions=False), buf


def lines(buf):
    out = []
    for l in buf.getvalue().splitlines():
        try:
            out.append(json.loads(l))
        except ValueError:
            pass
    return out

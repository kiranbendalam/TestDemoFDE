"""Shared bits for L2 steps: the view helpers from L1, and a guard that L1's contract is in place."""
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE.parent / "l1"))
from _view import chain, code  # noqa: E402,F401


def ensure_l1():
    """L2 builds on L1's contract (app/models.py). If it's still the TODO version, copy L1's finished file in."""
    models = ROOT / "app/models.py"
    if "NotImplementedError" in models.read_text():
        shutil.copyfile(HERE.parent / "l1/models_done.py", models)
        print("  NOTE: L2 needs L1's contract. app/models.py still had the L1 TODOs, so this copied\n"
              "        lab/l1/models_done.py -> app/models.py (the same as `bash lab.sh l1 apply`).\n")


def client(llm=None, timeout=None):
    """The real app (app/main.py) behind FastAPI's TestClient: requests go straight in, no server needed."""
    import app.main as main
    from app.llm import StubLLM
    main.llm = llm or StubLLM()
    if timeout is not None:
        main.TIMEOUT_S = timeout
    from fastapi.testclient import TestClient
    return TestClient(main.app, raise_server_exceptions=False)

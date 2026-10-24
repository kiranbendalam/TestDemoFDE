"""Shared bits for L4 steps: view helpers, the guard that L1-L3 are in place, the repo twin, and a command runner
that prints every git and docker command before it runs it (rule: no black-box steps)."""
import pathlib
import shlex
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LAB = HERE.parent
sys.path.insert(0, str(LAB / "l1"))
from _view import chain, code  # noqa: E402,F401

# The twin: a throwaway clone of your lab folder, so the Git steps never touch your real repo.
TWIN = pathlib.Path(tempfile.gettempdir()) / "fde-s03-l4-twin"
BRANCH = "feat/triage-service"
DEMO_ENV = "LLM_API_KEY=sk-demo-not-a-real-key\n"
BEFORE, AFTER = "s03-before", "s03-triage"


def run(*cmd, cwd=None, show=True, check=False):
    """Run one command; print it as `$ ...` and its output, indented. Returns the CompletedProcess."""
    if show:
        print("    $ " + (cmd[2] if cmd[:2] == ("sh", "-c") else shlex.join(cmd)))
    p = subprocess.run(cmd, cwd=cwd or TWIN, capture_output=True, text=True)
    out = (p.stdout + p.stderr).rstrip()
    if show and out:
        print("\n".join("      " + l for l in out.splitlines()))
    if check and p.returncode:
        sys.exit(f"  ✗ that command failed (exit {p.returncode})")
    return p


def have_docker():
    if shutil.which("docker") and subprocess.run(["docker", "info"], capture_output=True).returncode == 0:
        return True
    print("  ℹ️  Docker isn't available here, so the Docker part is skipped. Run it in your codespace.\n")
    return False


def ensure_l1_l3():
    """L4 ships the whole service, so L1-L3 must be in place. Copy the finished files in if they're still TODOs."""
    for rel, done, why in [("app/models.py", "l1/models_done.py", "L1's contract"),
                           ("app/logging_setup.py", "l3/logging_done.py", "L3's logging"),
                           ("app/main.py", "l3/main_done.py", "L2's endpoints and L3's middleware")]:
        if "NotImplementedError" in (ROOT / rel).read_text() or "TODO (L" in (ROOT / rel).read_text():
            shutil.copyfile(LAB / done, ROOT / rel)
            print(f"  NOTE: L4 needs {why}: copied lab/{done} -> {rel}")


def docker_done():
    return (ROOT / "Dockerfile").read_text() == (HERE / "Dockerfile_done").read_text()


def sync_twin():
    """Copy your current files (app/, Dockerfile, .dockerignore) into the twin's working tree."""
    for rel in ["app", "Dockerfile", ".dockerignore"]:
        src, dst = ROOT / rel, TWIN / rel
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
        elif src.exists():
            shutil.copyfile(src, dst)
        elif dst.exists():
            dst.unlink()


def make_twin():
    """A fresh twin: clone your repo, start on main, add your current files and a demo .env."""
    if subprocess.run(["git", "rev-parse", "--git-dir"], cwd=ROOT, capture_output=True).returncode:
        sys.exit("  ✗ this lab folder isn't a git repo. Open your own copy of the lab repo in a codespace.")
    shutil.rmtree(TWIN, ignore_errors=True)
    subprocess.run(["git", "clone", "-q", str(ROOT), str(TWIN)], check=True)
    for base in ("main", "master"):
        if run("git", "rev-parse", "--verify", "-q", f"origin/{base}", show=False).returncode == 0:
            run("git", "checkout", "-q", "-B", base, f"origin/{base}", show=False)
            break
    if not run("git", "config", "user.email", show=False).stdout.strip():
        run("git", "config", "user.email", "learner@example.com", show=False)
        run("git", "config", "user.name", "FDE Learner", show=False)
    sync_twin()
    (TWIN / ".env").write_text(DEMO_ENV)


def twin():
    """Use the twin from step 1; make it if it's missing. Always refresh it with your current files."""
    if not (TWIN / ".git").exists():
        make_twin()
    else:
        sync_twin()
    return TWIN


def base():
    """The twin's main branch as cloned: origin/main (or origin/master)."""
    for b in ("origin/main", "origin/master"):
        if run("git", "rev-parse", "--verify", "-q", b, show=False).returncode == 0:
            return b
    return "origin/HEAD"


def grade_l4():
    """Run `bash grade.sh l4` inside the twin; return [(mark, text)] for each ✅ / ❌ / ℹ️ line."""
    p = subprocess.run(["bash", "grade.sh", "l4"], cwd=twin(), capture_output=True, text=True)
    out = []
    for l in p.stdout.splitlines():
        s = l.strip()
        for m in ("✅", "❌", "ℹ️"):
            if s.startswith(m):
                out.append((m, s[len(m):].strip()))
    return out

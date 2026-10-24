from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def run(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def show_status(title: str, repo: Path, *, ignored: bool = False) -> None:
    args = ["status", "--short"]
    if ignored:
        args.append("--ignored")
    print(title)
    print(run(repo, *args) or "(clean)")
    print()


with tempfile.TemporaryDirectory(prefix="l4-git-mini-") as tmp:
    repo = Path(tmp)
    run(repo, "init", "-q", "-b", "main")
    run(repo, "config", "user.name", "Session 3 Primer")
    run(repo, "config", "user.email", "primer@example.com")

    write(repo / ".gitignore", "__pycache__/\n")
    write(repo / "app" / "models.py", "MODEL = 'old'\n")
    write(repo / "README.md", "demo repo\n")
    run(repo, "add", ".")
    run(repo, "commit", "-q", "-m", "base")

    run(repo, "switch", "-q", "-c", "feat/triage-service")

    write(repo / "app" / "models.py", "MODEL = 'new'\n")
    write(repo / ".env", "LLM_API_KEY=demo-secret\n")
    write(repo / "notes.txt", "scratch notes\n")

    print("GIT: deliberate staging vs accidental staging")
    print("A throwaway repo starts on a feature branch with one real code change, one secret file and one scratch note.\n")
    print(f"current branch: {run(repo, 'branch', '--show-current')}")
    print()

    show_status("1. Before staging", repo)

    run(repo, "add", "-A")
    show_status("2. After `git add -A`", repo)
    print("WHAT WENT WRONG")
    print("- `.env` is now staged, even though it is a local secret file.")
    print("- `notes.txt` is staged too, even though it is unrelated scratch work.")
    print("- This is why the lab says: never `git add -A` with untracked files around.\n")

    run(repo, "restore", "--staged", ".")
    (repo / ".gitignore").write_text("__pycache__/\n.env\n")
    run(repo, "add", "app", ".gitignore")
    show_status("3. After adding `.env` to `.gitignore` and staging only `app/` + `.gitignore`", repo, ignored=True)

    run(repo, "commit", "-q", "-m", "feat: update app contract")
    ahead = run(repo, "rev-list", "--count", "main..HEAD")
    print("WHAT TO NOTICE")
    print("- You are on a feature branch, not `main`.")
    print("- `.env` is ignored instead of staged.")
    print("- Only the intended code change and `.gitignore` are in the commit.")
    print(f"- The branch is now {ahead} commit(s) ahead of main, ready for a PR.")

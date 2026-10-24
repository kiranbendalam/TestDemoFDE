from __future__ import annotations

import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "docker_context"


def shell(*args: str, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=check)


def docker(*args: str, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return shell("docker", *args, cwd=cwd, check=check)


def show(label: str, value: str) -> None:
    print(f"  {label:<24} {value}")


if shutil.which("docker") is None:
    print("DOCKER: not available here")
    print("Run this primer in Codespaces or another Docker-enabled environment.")
    raise SystemExit(0)


with tempfile.TemporaryDirectory(prefix="l4-docker-mini-") as tmp:
    stage = Path(tmp)
    shutil.copytree(SOURCE, stage / "ctx")
    context = stage / "ctx"

    before_tag = f"l4mini-before-{uuid.uuid4().hex[:8]}"
    after_tag = f"l4mini-after-{uuid.uuid4().hex[:8]}"
    container_id = None

    print("DOCKER: builds that run vs images the platform team accepts\n")
    print("Building the 'before' image...")
    docker("build", "-q", "-f", "Dockerfile.before", "-t", before_tag, ".", cwd=context)

    secret_before = docker("history", "--no-trunc", before_tag).stdout
    before_uid = docker("run", "--rm", "--entrypoint", "id", before_tag, "-u").stdout.strip()
    before_env = docker("run", "--rm", "--entrypoint", "cat", before_tag, "/app/.env").stdout.strip()
    before_size = int(docker("image", "inspect", "-f", "{{.Size}}", before_tag).stdout.strip())

    print("1. BEFORE image")
    show("base image", "python:3.12")
    show("secret in history", "yes" if "demo-key-123" in secret_before else "no")
    show(".env inside image", before_env or "(missing)")
    show("runs as uid", before_uid)
    show("healthcheck", "none")
    show("size", f"{before_size/1_000_000:.0f} MB")
    print()

    print("Building the 'after' image...")
    shutil.copyfile(context / ".dockerignore.after", context / ".dockerignore")
    docker("build", "-q", "-f", "Dockerfile.after", "-t", after_tag, ".", cwd=context)

    secret_after = docker("history", "--no-trunc", after_tag).stdout
    after_uid = docker("run", "--rm", "--entrypoint", "id", after_tag, "-u").stdout.strip()
    env_probe = docker("run", "--rm", "--entrypoint", "sh", after_tag, "-c", "cat /app/.env 2>/dev/null || echo '(none)'").stdout.strip()
    after_size = int(docker("image", "inspect", "-f", "{{.Size}}", after_tag).stdout.strip())

    container_id = docker("run", "-d", after_tag).stdout.strip()
    health = "starting"
    for _ in range(30):
        health = docker("inspect", "-f", "{{.State.Health.Status}}", container_id).stdout.strip()
        if health == "healthy":
            break
        time.sleep(1)

    print("2. AFTER image")
    show("base image", "public.ecr.aws/docker/library/python:3.12.15-slim-bookworm")
    show("secret in history", "yes" if "demo-key-123" in secret_after else "no")
    show(".env inside image", env_probe)
    show("runs as uid", after_uid)
    show("healthcheck", health)
    show("size", f"{after_size/1_000_000:.0f} MB")
    print()

    print("WHAT TO NOTICE")
    print("- The 'before' image builds, but it bakes a secret into history, copies `.env`, runs as root and has no health check.")
    print("- The 'after' image copies only what it needs, runs as a non-root user and reports healthy.")
    print("- L4 is about shipping something a platform team will actually accept, not just something that starts.")

    if container_id:
        docker("rm", "-f", container_id, check=False)
    docker("rmi", "-f", before_tag, after_tag, check=False)

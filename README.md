# Session 3 lab: Python & Production Engineering

**From prototype to a service the platform team will run.**

**AI Forward Deployed Engineering · IIT Delhi × Varsity · Session 3 · Sat 24 Oct 2026**

Example Bank (fictional) has a complaint-triage prototype, `triage_prototype.py`. It works on a laptop.
The Head of Retail Ops wants it live; the Sr. Platform Engineer won't run a script; the CISO wants an
audit trail with no account numbers in the logs. You'll turn it into a typed, logged, containerised service.

## Start here: get your lab ready (5 minutes, before the session)

### Option A (recommended): GitHub Codespaces

Everything works here, including Git and Docker. Nothing to install on your laptop.

1. Sign in to GitHub (a free account is fine): https://github.com
2. On **this repository's** page, click the green **Use this template** button → **Create a new repository**.
   Give it any name and create it. This is **your own copy**: you can push branches and open pull requests in it.
   (Don't open a codespace on this page itself: you couldn't push your work.)
3. **In your copy**, click **Code** → **Codespaces** → **Create codespace on main**. The first start takes 2 to 3
   minutes.
4. In the terminal at the bottom, run:

   ```bash
   bash check_setup.sh
   ```

   You should see **All good. You are ready for the session.**
5. Then stop the codespace to save your free hours: github.com/codespaces → **⋯** → **Stop**. On the day, open it
   again from the same page.

Free allowance: GitHub Free includes 120 core-hours a month. A 2-core codespace uses 2 per hour, so you get about
60 hours. Delete the codespace when you've finished the deep dives and the assignment.

### Option B (if GitHub or Codespaces is blocked, common on company laptops): Google Colab

1. Open the notebook in Colab with a Google account:
   https://colab.research.google.com/github/sendtoshailesh/fde-s03-lab/blob/main/colab/s03_lab.ipynb
   (or download `colab/s03_lab.ipynb` from this repo and use File → Upload notebook in Colab).
2. **Runtime** → **Run all**. The first cells should run without errors.

Colab runs the same lab: the four live primers, then the four deep dives. You write no code. Two parts (Docker,
and opening `/docs` in a browser) need Codespaces, which you can do later from a personal device. Colab's
storage is temporary: File → Save a copy in Drive.

### Good to know

- No API key is needed: the lab has an offline model.
- Everything in the lab is fictional. Never paste real customer or company data into it.
- If `check_setup.sh` shows a ❌, post a screenshot in the session chat and we'll help you fix it.

## How the lab works: three versions of the same four rungs

The lab follows the four gates from the deck: **L1 Contract → L2 Service → L3 Observability → L4 Ship**. You meet
each rung three times, each time a little deeper.

| | **1 · Live lab** | **2 · Deep dive** | **3 · Assignment** |
|---|---|---|---|
| **When** | In the session; the trainer drives on screen | After the session, at your own pace | After the deep dives |
| **What you do** | Run a few commands and read the output | Run one command per step: **fail → check → show → apply → pass → try** | Write the code yourself from the TODOs |
| **You write code?** | No | No | **Yes** |
| **On what** | A small, separate primer per rung (`primer/`) | The real service (`app/`, `Dockerfile`) | The real service (`app/`, `Dockerfile`, `HANDOVER.md`) |
| **Guide** | `lab/L1-live.md` … `lab/L4-live.md` | `lab/L1-deep-dive.md` … `lab/L4-deep-dive.md` | `ASSIGNMENT.md` |
| **Run** | `cd primer/<rung> && bash run.sh <step>` | `bash lab.sh l1 fail` … `bash lab.sh l4 try` | `bash lab.sh reset l1`, edit, `bash grade.sh l1` |
| **Time** | About 8–15 min per rung | About 15 min per rung | About 1.5 hours in total |

### The four rungs

| Rung | Live lab (primer) | Deep dive (real service) | Assignment: you write | Check |
|---|---|---|---|---|
| **L1 Contract** | `primer/l1-pydantic-mini`: bad model replies, with and without a Pydantic contract | `bash lab.sh l1 …` on `app/models.py` | `Complaint`, `TriageResult`, `parse_triage()` | `bash grade.sh l1` |
| **L2 Service** | `primer/l2-async-fastapi-mini`: blocking vs awaited, a timeout, a FastAPI service | `bash lab.sh l2 …` on `app/main.py` | `/healthz`, and `/triage` (async, with a timeout) | `bash grade.sh l2` |
| **L3 Observability** | `primer/l3-observability-mini`: print logs vs one masked JSON line | `bash lab.sh l3 …` on `app/logging_setup.py`, `app/main.py` | `mask()`, the JSON formatter, the request middleware | `bash grade.sh l3` |
| **L4 Ship** | `primer/l4-ship-mini`: `git add -A` vs deliberate staging; a refused vs an accepted image | `bash lab.sh l4 …` (Git in a throwaway copy; Docker on the real `Dockerfile`) | A branch, a commit and a PR; the five Dockerfile fixes | `bash grade.sh l4` |
| **Handover** | — | — | `HANDOVER.md`, half a page for the Sr. Platform Engineer | `bash grade.sh handover` |

L4's Docker parts need a codespace. Everything else also runs in Colab.

## Quick cheat sheet

- **Live lab:** `cd primer/<rung>` then `bash run.sh <step>` (each `lab/L*-live.md` lists the steps). Primers never need a reset.
- **Deep dive:** `bash lab.sh l1|l2|l3|l4 fail|check|show|apply|pass|try`. Every step prints **HOW THIS STEP RUNS** and the real code lines.
- **Assignment:** `bash lab.sh reset l1|l2|l3|l4` puts the TODO version back; check with `bash grade.sh l1|l2|l3|l4|handover|all`.
- **Run the service** (after L2): `bash lab.sh l2 serve`, then **Ports** → 8000 → globe icon → add `/docs`. Keep the port **Private**.

## Optional: a real model

Add a secret named `GEMINI_API_KEY` (Codespaces: github.com/settings/codespaces → Secrets; Colab: the 🔑 panel).
A free key is at https://aistudio.google.com/apikey. On free tiers, providers may use your prompts to improve
their products: use only the fictional data here. The grader always uses the offline stub.

## Files

| Path | What |
|---|---|
| `lab/L1-live.md` … `lab/L4-live.md` | **Live lab** guides: what to run in each primer, and what you'll see |
| `primer/` | The four small primers used in the live lab (`primer/README.md` lists them) |
| `lab/L1-deep-dive.md` … `lab/L4-deep-dive.md` | **Deep dive** guides, one per rung |
| `lab.sh`, `lab/l1/` … `lab/l4/` | The deep-dive runner and its steps |
| `ASSIGNMENT.md` | **Assignment** guide: write L1–L4 and the handover yourself |
| `grade.sh` | Checks the assignment, rung by rung |
| `triage_prototype.py` | The "before": the prototype the lab starts from (`python triage_prototype.py`) |
| `app/models.py` | L1: the contract |
| `app/main.py` | L2: the service; L3: request logging |
| `app/logging_setup.py` | L3: JSON logs and masking |
| `app/llm.py` | The model client (offline stub, plus an optional real model). No changes needed |
| `Dockerfile` | L4: it builds, but the platform team would refuse it |
| `HANDOVER.md` | Your handover note (template) |
| `tests/` | What `grade.sh` checks |
| `colab/s03_lab.ipynb` | The same live lab and deep dives in Colab |
| `GLOSSARY.md` | One-page glossary of the terms used in the lab |
| `check_setup.sh` | Checks your environment is ready |

## Stuck?

- `ModuleNotFoundError`: run `pip install -r requirements.txt`.
- Port 8000 already in use: stop the other server (Ctrl+C), or run `pkill -f uvicorn`.
- `docker` not found in a codespace: Ctrl/Cmd + Shift + P → **Codespaces: Full Rebuild Container**.
- Company laptop blocks github.com: use Option B, or a personal device.
- Still stuck: post in the session chat with the exact error.

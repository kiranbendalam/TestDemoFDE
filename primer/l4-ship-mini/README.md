# Session 3 primer: shipping with Git and Docker (live L4)

A **separate, simplified primer** for Session 3, like the L1, L2 and L3 primers.
Learners run commands and read output; they write no code.

1. **Git:** see why `git add -A` is risky when `.env` and other untracked files are around.
2. **Git:** see the safer pattern — branch first, ignore `.env`, then stage only what you mean.
3. **Docker:** inspect an image that builds but would be rejected by a platform team.
4. **Docker:** compare it with a slimmer, safer image that avoids secrets, runs non-root and has a health check.

```bash
bash run.sh git
bash run.sh docker
```

Or run the full flow:

```bash
bash run.sh all
```

This primer is for **Codespaces or another Docker-enabled dev environment**. It does not need the main lab app.

## Files

- `git_demo.py`: a throwaway temp repo that shows careless vs deliberate staging
- `docker_demo.py`: builds and inspects a before/after image from the tiny demo service
- `docker_context/`: the tiny service and the two Dockerfiles used by the demo

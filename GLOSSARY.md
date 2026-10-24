# Session 3 lab glossary

**A one-page guide to the terms used in the Session 3 lab.**

## Lab rung labels

- **L1 Contract** — the first lab step. You define the input/output schema so the service accepts only valid data and sends uncertain cases to human review.
- **L2 Service** — the second lab step. You turn the prototype into an async FastAPI service with `/triage` and `/healthz`.
- **L3 Observability** — the third lab step. You add structured logs, request IDs and masking so the service can be operated safely.
- **L4a Git** — the first shipping step. You create a branch, commit your changes and open a PR.
- **L4b Docker** — the second shipping step. You fix the container so a platform team would accept it.
- **Handover** — a short note for the platform engineer explaining what you built, how to run it and what to watch.

## Role and business terms

- **FDE** — Forward Deployed Engineer or Forward Deployed Engineering. In this course: getting AI systems running in the customer's environment, under the customer's rules, not just making the model work.
- **CISO** — Chief Information Security Officer. The person responsible for security controls such as safe logging and auditability.
- **Sr. Platform Engineer** — the person who operates the service in production and therefore cares about health checks, logs, containers and safe defaults.
- **Example Bank** — the fictional bank in every exercise. Its people, accounts and data are made up.
- **Retail Ops** — retail operations. Here, the business team that wants complaints routed quickly; the Head of Retail Ops owns the result.
- **Contact-Centre Team Lead** — runs the agents who work the team queues; cares that screens don't freeze.
- **CTO** — Chief Technology Officer. Cares whether the service survives production.
- **Triage** — first-pass routing. In this lab, the system reads a complaint and decides its category, priority and owning team.
- **Human review** — the fallback path when the model's output is invalid or the model is too slow. Instead of guessing, the system sends the case to a person, with the reason.

## Software and API terms

- **Prototype** — an early working version. `triage_prototype.py` shows the “works on my laptop” starting point.
- **Contract** — the formal shape of the data your service accepts and returns.
- **Pydantic** — the Python library used here to define and validate that contract.
- **FastAPI** — the web framework used to expose the service over HTTP.
- **API** — Application Programming Interface. In this lab, the service endpoint other systems call.
- **Async** — short for asynchronous. It lets the service wait on slow work without blocking everything else.
- **Timeout** — a maximum wait limit. If the model call takes too long, the service stops waiting and handles it safely.
- **Endpoint** — a callable URL in the service, such as `/triage` or `/healthz`.
- **`/triage`** — the main endpoint that classifies and routes a complaint.
- **`/healthz`** — a simple health-check endpoint used by platforms and containers to see if the service is alive.
- **`/docs`** — FastAPI’s built-in API documentation UI, generated from your Pydantic models.
- **422** — the HTTP status FastAPI returns when a request doesn't match the contract; it lists the fields that failed.
- **`ValidationError`** — the error Pydantic raises when data doesn't fit the model; it names each field and the reason.
- **Event loop / `await`** — the single thread that runs async code; `await` is where a request pauses so others can run.
- **uvicorn** — the small web server that runs a FastAPI app.

## Data and operations terms

- **LLM** — Large Language Model. In this lab, it suggests category, priority and owning team from complaint text.
- **Stub model** — a fake offline model used for learning and grading. It avoids API keys and external dependencies.
- **Prompt version** — the version label for the instruction sent to the model. It helps with traceability.
- **Request ID** — a unique ID attached to one incoming request so logs can be traced end to end.
- **`X-Request-ID`** — the HTTP header used to carry that request ID.
- **JSON logs** — machine-readable log lines in JSON format.
- **Structured logging** — logging with named fields like `request_id`, `status` and `latency_ms`, not just plain text.
- **Masking** — hiding sensitive data before it reaches logs. Here, all but the last four digits of an account number are hidden: `EB-******6354`.
- **Audit trail** — evidence of what the system did, when it did it and why.
- **Observability** — the ability to understand system behaviour from logs, metrics and traces. In this lab, the focus is mainly logs.

## Delivery and tooling terms

- **Git** — version control used to track and share changes.
- **Branch** — an isolated line of work, such as `feat/triage-service`.
- **Commit** — one saved change in Git, with a message saying what changed and why.
- **PR** — Pull Request. The review step where changes are proposed before merge.
- **Merge** — adding a reviewed branch's commits into `main`.
- **Docker** — container tooling used to package the service consistently.
- **Dockerfile** — the recipe that defines how the container image is built.
- **Image** — the sealed, layered snapshot `docker build` produces; anyone who can pull it can read its layers.
- **Container** — the image running, the same on a laptop and on the bank's platform.
- **`.dockerignore`** — tells Docker which files not to send into the build context.
- **`.gitignore`** — tells Git which files should stay untracked.
- **`grade.sh`** — the local checker script for each lab rung.
- **Codespaces** — GitHub’s cloud development environment. Recommended for the whole lab (Colab has no Docker).
- **Colab** — Google Colab notebook environment. Good fallback for L1–L3, but not for Git or Docker.

## Quick memory aid

- **L1** = define the data
- **L2** = expose the service
- **L3** = make it operable
- **L4a** = ship with Git
- **L4b** = ship with Docker

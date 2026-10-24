# L4b: this Dockerfile works, and the platform team would still refuse it.
# Fix it (see ASSIGNMENT.md), then run: bash grade.sh l4
#
# TODO 1: base image from Docker Hub (anonymous pulls are rate-limited), full size, not pinned to a patch version.
#         Use the pinned slim mirror on ECR Public: public.ecr.aws/docker/library/python:3.12.15-slim-bookworm
# TODO 2: a key baked into the image: anyone with the image can read it in `docker history`. Remove it;
#         pass secrets at run time instead (docker run -e ...).
# TODO 3: `COPY . .` copies everything, including .env and .git. Copy only what the app needs,
#         and add a .dockerignore.
# TODO 4: it runs as root. Create a user and switch to it.
# TODO 5: no health check. Add a HEALTHCHECK with --interval=5s --timeout=3s --start-period=5s that calls /healthz
#         (slim images have no curl; use python).

FROM python:3.12
ENV SERVICE_API_KEY=demo-key-123
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

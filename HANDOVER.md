# Handover: complaint-triage service

To: Sr. Platform Engineer, Example Bank core platform team · From: <your name>, FDE team · Date: <date>

Keep it to half a page. Write for someone who will run this at 2 am, not for a reviewer.

## What it does

TODO: one or two sentences. What goes in, what comes out, and what happens when the model is wrong or slow.

## How to run it

TODO: the commands to build and run the container, the port, and how to check it's healthy.

## What is logged

TODO: the fields in each log line, what is masked, and how to follow one request end to end.

## Known limits

TODO: what this pilot does not do yet (be honest: this is what the CISO will ask about).
TODO (hint, replace with your own words): a 422 response echoes the rejected input; the summary returns the complaint text unmasked; uvicorn's own log lines aren't masked; the stub model, not a real one; no login or rate limiting on the API.

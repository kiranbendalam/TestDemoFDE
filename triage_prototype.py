"""triage_prototype.py: the 'before'. It works on a laptop. Don't ship it.

Handed over by a previous team after a quick, agent-assisted build. Read it and spot what the
Sr. Platform Engineer and the CISO will refuse. (Everything here is fictional.)

Run:  python triage_prototype.py
"""

import json
import time

API_KEY = "demo-key-123"  # a key in the code (fake, but this is how real ones leak)

TEAM_QUEUES = {"disputes": "Q-DISPUTES", "fraud_ops": "Q-FRAUD", "digital_support": "Q-DIGITAL", "branch_services": "Q-BRANCH"}


def call_model(complaint):
    time.sleep(1)  # a blocking network call: nothing else can run while we wait
    text = complaint["text"].lower()
    if complaint["id"] == "C-013":  # the model has a bad day
        return '{"category": "fraud", "priority": "urgent", "team": "fraud ops", "summary": "UPI debit"}'
    if "unauthorised" in text or "did not make" in text:
        return '{"category": "fraud", "priority": 1, "team": "fraud_ops", "summary": "fraud"}'
    if "charged twice" in text:
        return '{"category": "card_dispute", "priority": 2, "team": "disputes", "summary": "double charge"}'
    return '{"category": "other", "priority": 4, "team": "branch_services", "summary": "other"}'


def main():
    with open("data/complaints.jsonl") as f:
        complaints = [json.loads(line) for line in f][:5] + [{"id": "C-013", "text": "Unauthorised UPI debit. Account EB-9081726354."}]
    for c in complaints:
        print("processing", c)  # the full complaint, account number and all, goes to the console
        out = json.loads(call_model(c))  # trusts whatever the model returns
        queue = TEAM_QUEUES.get(out["team"], "Q-GENERAL")  # unknown team? general queue, silently
        print(c["id"], "->", queue, "priority", out["priority"])


if __name__ == "__main__":
    main()

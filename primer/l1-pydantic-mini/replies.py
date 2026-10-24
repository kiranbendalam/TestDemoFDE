from __future__ import annotations

import json

GOOD_REPLY = json.dumps(
    {
        "team": "fraud_ops",
        "priority": 1,
        "summary": "Unauthorised card charge",
    }
)

REPLIES = [
    ("good reply", GOOD_REPLY),
    (
        "wrong team + wrong priority",
        json.dumps(
            {
                "team": "fraud ops",
                "priority": "urgent",
                "summary": "Unauthorised card charge",
            }
        ),
    ),
    (
        "missing team",
        json.dumps(
            {
                "priority": 2,
                "summary": "Card charged twice",
            }
        ),
    ),
    (
        "prose around JSON",
        "Sure! Here is the JSON you asked for:\n" + GOOD_REPLY,
    ),
]

QUEUE_BY_TEAM = {
    "fraud_ops": "Q-FRAUD",
    "disputes": "Q-DISPUTES",
}

"""The three bad replies used in L1 (constructed examples)."""

# Three replies a model can send on a bad day, even when the prompt says "reply with JSON only"
# (constructed examples; the lab's stub model returns the same for C-013, C-014 and C-015).
REPLIES = {
    "C-013 unauthorised UPI debit, 25,000 rupees": '{"category": "fraud", "priority": "urgent", "team": "fraud ops", "summary": "UPI fraud"}',
    "C-014 late payment charges":                  '{"category": "charges", "priority": 3, "summary": "late fee"}',
    "C-015 card swiped twice":                     'Sure! Here is the JSON you asked for:\n{"category": "card_dispute", "priority": 2, "team": "disputes", "summary": "double swipe"}',
}


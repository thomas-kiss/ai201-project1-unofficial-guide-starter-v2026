"""
Decides whether an answer counts as correct.

`run_eval.py` imports this automatically once it exists and calls `judge()`
for every run of every question in questions.py.

The rule: case-insensitive substring match between `expects` and `answer`,
except for "No" — a plain substring check on "no" would false-positive on
any answer containing a word like "north" or "nobody", so that one gets a
whole-word match instead.
"""

import re


def judge(question: str, expects: str, answer: str, results) -> bool:
    expects = expects.strip()
    if not expects:
        return False

    if expects.lower() == "no":
        return re.search(r"\bno\b", answer, re.IGNORECASE) is not None

    return expects.lower() in answer.lower()

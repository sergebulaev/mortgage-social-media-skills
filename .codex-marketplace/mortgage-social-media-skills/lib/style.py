"""Voice lint: the AI tells the family scrubs, enumerated (PLAYBOOK §5: an
enumerated rule holds under pressure, a vague caveat does not).

STRICT findings must be fixed before a draft is shown; SOFT ones are listed.
Platform length limits come from Publora's platform-limits guide.
"""
from __future__ import annotations

import re

STRICT = [
    ("EM_DASH", r"[—–]", "em or en dash: use a period, comma or colon"),
    ("AI_OPENER", r"^(in today's|in the ever|in a world where|let's dive|let's talk about|are you ready to)", "stock AI opener"),
    ("AI_VOCAB", r"\b(delve|leverage|game[- ]changer|unlock(ing)? the|elevate your|seamless(ly)?|robust|tapestry|testament to|navigat(e|ing) the (complex|ever)|in the realm of|embark|harness the power)\b", "AI vocabulary"),
    ("DEAD_CLOSER", r"(what do you think\?|thoughts\?|let us know in the comments|drop a comment below|agree\?)\s*$", "dead closing question"),
    ("NOT_JUST", r"\bit'?s not just (a|an|about)\b[^.]{0,60}\bit'?s\b", "'it's not just X, it's Y' construction"),
]
SOFT = [
    ("RULE_OF_THREE", r"\b(\w+), (\w+),? and (\w+)\b[.!]", "list of three adjectives or nouns closing a sentence"),
    ("EXCLAIM", r"!{2,}", "double exclamation"),
    ("HASHTAG_PILE", r"(#\w+\s*){6,}", "more than five hashtags in a row"),
    ("EMOJI_PILE", r"([\U0001F300-\U0001FAFF]\s*){4,}", "four or more emoji in a row"),
]
LIMITS = {"twitter": 280, "threads": 500, "bluesky": 300, "mastodon": 500, "linkedin": 3000,
          "instagram": 2200, "tiktok": 2200, "facebook": 63206, "telegram": 4096, "youtube": 5000}


def lint(text: str, platform: str = "") -> dict:
    strict, soft = [], []
    for code, rx, why in STRICT:
        for m in re.finditer(rx, text, re.I | re.M):
            strict.append({"code": code, "match": m.group(0), "why": why})
    for code, rx, why in SOFT:
        if re.search(rx, text, re.I | re.M):
            soft.append({"code": code, "why": why})
    limit = LIMITS.get(platform)
    if limit and len(text) > limit and platform not in ("twitter", "threads"):
        strict.append({"code": "TOO_LONG", "match": f"{len(text)} chars",
                       "why": f"{platform} allows {limit} characters"})
    return {"strict": strict, "soft": soft, "ok": not strict}

"""One text per network: fit a post to each network's limit without losing the
lines the rules require.

Limits come from Publora `GET /api/v1/platform-limits` (`limits()` with a
client); `LIMITS` is the same table recorded 2026-11-24 (package
@publora/platform-limits 1.0.0, limits dated 2026-03-11), used when there is
no key or the call fails. The standard limit is treated as hard on every
network: a long X or Threads text is not left to auto-threading (a 705
character X draft was accepted as a draft and would fail to publish, the live
run of 2026-11-24).

How a version is made (`fit`): the post is split into units (sentences inside
lines inside paragraphs). The first unit always stays, so does every line
with a link (the source, the notice, the sermon), then the next units in
order while the result still fits, stopping at the first that does not: a
prefix, never a sentence picked from the middle (a later sentence can lean on
an earlier one, and a rate quoted without its sentence can lose the label the
rules add to it). `finish` is applied to every
candidate: it is the compliance autofix, so the lines the rules append (NMLS,
Equal Housing, license number, the survey label, the 21+ line...) come back
on the short version too and are counted. When even the first unit plus the
required lines do not fit, there is no version for that network, and the
reason says how many characters the required part needs.

The short version of an EVENT is not a cut of the full text (the live dry run
of 2026-11-25 cut a rate post down to "Freddie Mac's weekly survey is out."
plus the required lines: no rate, no change). When the event gives a `short`
text (its main fact: the rate and the change, the hail size and the place, the
recalled product, the cutoff that moved), a network that cannot take the full
text gets `short`, the text's link lines, and the `cta` when it still fits;
`finish` adds the required lines as always. `must` lists the strings every
version has to contain (the main fact): a full text without them is not used
as is. When `short` plus the required lines do not fit, there is no version
for that network: no draft beats a post that says nothing.
"""
from __future__ import annotations

import re
from typing import Callable, Optional

#: Publora platform-limits, characters.standard (2026-11-24).
LIMITS = {"twitter": 280, "threads": 500, "bluesky": 300, "mastodon": 500, "linkedin": 3000,
          "instagram": 2200, "tiktok": 2200, "facebook": 63206, "telegram": 4096, "youtube": 5000,
          "pinterest": 800}
#: Telegram: a caption under media is shorter (characters.botCaption).
CAPTION_LIMITS = {"telegram": 1024}
URL = re.compile(r"https?://\S+")
X_URL_WEIGHT = 23  # X counts every link as 23 characters (t.co)


def limits(client=None) -> dict:
    """{platform: {"text": n, "caption": n}} from Publora when a client is
    given and answers, else from the recorded table."""
    table = {p: {"text": n, "caption": CAPTION_LIMITS.get(p, n)} for p, n in LIMITS.items()}
    if client is None:
        return table
    try:
        live = client.platform_limits()
        for p, info in (live.get("platforms") or {}).items():
            chars = info.get("characters") or {}
            if chars.get("standard"):
                table[p] = {"text": int(chars["standard"]),
                            "caption": int(chars.get("botCaption") or chars["standard"])}
    except Exception:  # a missing endpoint must not stop a draft: the table is the fallback
        pass
    return table


def limit_for(platform: str, has_media: bool = False, table: Optional[dict] = None) -> Optional[int]:
    entry = (table or limits()).get(platform)
    if not entry:
        return None
    return entry["caption"] if has_media else entry["text"]


def count(text: str, platform: str) -> int:
    """Characters as the network counts them (X: a link is 23)."""
    if platform == "twitter":
        return len(URL.sub("x" * X_URL_WEIGHT, text))
    return len(text)


def _units(text: str) -> list[tuple[int, int, str]]:
    """(paragraph, line, sentence) units, in order."""
    out = []
    for p, para in enumerate(re.split(r"\n\s*\n", text.strip())):
        for l, line in enumerate(para.split("\n")):
            line = line.strip()
            if not line:
                continue
            if line.startswith(("-", "•", "*", "✓")) or URL.search(line):
                out.append((p, l, line))  # list items and link lines stay whole
                continue
            for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9¿¡\"(“])", line):
                if s.strip():
                    out.append((p, l, s.strip()))
    return out


def _join(units: list[tuple[int, int, str]]) -> str:
    paras: dict[int, dict[int, list[str]]] = {}
    for p, l, s in units:
        paras.setdefault(p, {}).setdefault(l, []).append(s)
    return "\n\n".join("\n".join(" ".join(ss) for ss in lines.values()) for lines in paras.values())


def has_all(text: str, must) -> bool:
    return all(m in text for m in (must or ()))


def fit(text: str, platform: str, *, finish: Callable[[str], str] = lambda t: t,
        has_media: bool = False, table: Optional[dict] = None, short: Optional[str] = None,
        cta: Optional[str] = None, must=()) -> tuple[Optional[str], str]:
    """(final text, "") when a version fits, else (None, reason).

    `text` is the post BEFORE the autofix; `finish` turns a candidate into the
    final text (autofix), so appended lines are part of the count. `short`,
    `cta` and `must` come from the event (see the module docstring)."""
    lim = limit_for(platform, has_media, table)
    full = finish(text)
    if (lim is None or count(full, platform) <= lim) and has_all(full, must):
        return full, ""
    if short and short.strip():
        short = short.strip()
        links = [u[2] for u in _units(text)
                 if URL.search(u[2]) and not any(x in short for x in URL.findall(u[2]))]
        base = finish("\n\n".join([short] + links))
        if lim is not None and count(base, platform) > lim:
            return None, (f"{platform}: the event's main fact and the required lines need "
                          f"{count(base, platform)} characters, {platform} allows {lim}; no draft for "
                          f"{platform} (a post without the fact would say nothing)")
        if cta and cta.strip():
            trial = finish("\n\n".join([short, cta.strip()] + links))
            if lim is None or count(trial, platform) <= lim:
                base = trial
        return base, ""
    if lim is None or count(full, platform) <= lim:
        return full, ""  # no short text to fall back on; the caller checks `must`
    units = _units(text)
    if not units:
        return None, f"{platform}: empty post"
    required = [u for i, u in enumerate(units) if i == 0 or URL.search(u[2])]
    kept = list(required)
    base = finish(_join(kept))
    if count(base, platform) > lim:
        return None, (f"{platform}: the opening line and the required lines need {count(base, platform)} "
                      f"characters, {platform} allows {lim}; no draft for {platform}")
    for u in units:
        if u in kept:
            continue
        trial = sorted(kept + [u], key=units.index)
        if count(finish(_join(trial)), platform) > lim:
            break
        kept = trial
    # A lead-in that promises a list ("largest first:") goes when no item of
    # the list made it in.
    body = [u for u in kept if not URL.search(u[2])]
    while len(body) > 1 and body[-1][2].endswith(":"):
        kept.remove(body.pop())
    return finish(_join(kept)), ""


def versions(text: str, platforms: list[str], *, finish_for: Callable[[str], Callable[[str], str]],
             platform_of: Callable[[str], str], has_media: bool = False,
             table: Optional[dict] = None, short: Optional[str] = None, cta: Optional[str] = None,
             must=()) -> tuple[list[dict], list[str]]:
    """Group connection ids by their fitted text.

    Returns ([{"text", "platforms"}], [reasons for the connections left out])."""
    groups: dict[str, list[str]] = {}
    skipped = []
    for conn in platforms:
        net = platform_of(conn)
        out, why = fit(text, net, finish=finish_for(net), has_media=has_media, table=table,
                       short=short, cta=cta, must=must)
        if out is None:
            skipped.append(f"{conn}: {why}")
            continue
        groups.setdefault(out, []).append(conn)
    return [{"text": t, "platforms": ps} for t, ps in groups.items()], skipped

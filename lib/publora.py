"""Publora REST client: drafts by default, scheduling only on an explicit go.

Endpoints used (docs.publora.com, read 2026-11-19):
- POST /create-post          no scheduledTime and no publishNow => draft
- PUT  /update-post/<id>     status "scheduled" + scheduledTime => schedule
- GET  /platform-connections the channels this key can post to
- GET  /get-post/<id>
- GET  /platform-limits       characters per network (lib/platforms.py)

Auth header `x-publora-key`. `platforms` is a STRING array of connection ids
(`["instagram-123"]`). `mediaUrls` takes public https URLs (a Pixfaro card URL
goes straight in). `platformSettings` is validated against Publora's strict
allowlist here first, so a typo fails locally and free.

This client never sends `publishNow`. There is no method for it on purpose:
every skill and the autopilot create drafts, and a human schedules them.
"""
from __future__ import annotations

import os
import uuid
from typing import Any, Optional

from . import _http
from ._env import load_env

BASE_URL = "https://api.publora.com/api/v1"

#: Publora's accepted platformSettings tree (create-post, "Unknown
#: platformSettings paths"). Anything else is a 400 PLATFORM_SETTING_UNKNOWN.
ALLOWED_SETTINGS = {
    "tiktok": {"viewerSetting", "allowComments", "allowDuet", "allowStitch", "autoAddMusic",
               "commercialContent", "brandOrganic", "brandedContent", "aiGenerated"},
    "instagram": {"videoType", "shareToFeed", "coverUrl", "cover_url", "aiGenerated"},
    "youtube": {"privacy", "title", "tags", "madeForKids", "aiGenerated", "categoryId",
                "playlist", "thumbnail"},
    "threads": {"replyControl"},
    "twitter": {"replyTo", "quoteTweet", "aiGenerated"},
    "telegram": {"disableNotification", "disableWebPagePreview", "protectContent"},
    "linkedin": {"repostEnabled", "repostParentUrn", "repostVisibility"},
}
#: Networks where Publora forwards the AI-media disclosure flag.
AI_FLAG_PLATFORMS = ("instagram", "tiktok", "youtube", "twitter")
#: Networks that refuse a post without media.
MEDIA_REQUIRED = ("instagram", "tiktok", "youtube")
#: Publora connection prefixes (Pinterest is connect-only, never a target).
PUBLISHABLE = ("linkedin", "twitter", "facebook", "instagram", "threads", "tiktok", "youtube",
               "bluesky", "mastodon", "telegram")


class PubloraError(RuntimeError):
    pass


def platform_of(connection_id: str) -> str:
    return str(connection_id).split("-", 1)[0].lower()


def validate_settings(settings: Optional[dict]) -> None:
    for platform, values in (settings or {}).items():
        if platform not in ALLOWED_SETTINGS:
            raise PubloraError(f"platformSettings.{platform} is not accepted by Publora")
        if not isinstance(values, dict):
            raise PubloraError(f"platformSettings.{platform} must be an object")
        for key in values:
            if key not in ALLOWED_SETTINGS[platform]:
                raise PubloraError(f"platformSettings.{platform}.{key} is not accepted by Publora")


def ai_settings(platforms: list[str], ai_generated: bool) -> dict:
    """`aiGenerated: true` for every target network that carries the flag.

    Typeset data cards are not AI imagery, so they pass `ai_generated=False`
    and no flag is set. A model-generated image passes True."""
    if not ai_generated:
        return {}
    present = {platform_of(p) for p in platforms}
    return {p: {"aiGenerated": True} for p in AI_FLAG_PLATFORMS if p in present}


def check_targets(platforms: list[str], media_urls: Optional[list[str]]) -> list[str]:
    """Problems that would make Publora refuse the post later, found now."""
    problems = []
    if not platforms:
        problems.append("no target channels: list them with list_connections()")
    for p in platforms:
        if platform_of(p) not in PUBLISHABLE:
            problems.append(f"{p}: not a publishable Publora channel")
    if not media_urls:
        for p in platforms:
            if platform_of(p) in MEDIA_REQUIRED:
                problems.append(f"{p}: {platform_of(p)} needs an image or video; a draft is fine, "
                                "scheduling will be refused until media is attached")
    for url in media_urls or []:
        if not str(url).startswith("https://"):
            problems.append(f"media URL must be https: {url}")
    return problems


def draft_key(repo: str, event_id: str, body: dict) -> str:
    """Idempotency-Key for a draft: the event AND the request body.

    The same body sent again maps to the same key, so Publora replays the first
    answer instead of creating a twin. A different body for the same event
    (the draft was deleted and the run now has a card, or another text
    version for another network) gets its own key: with the event id alone,
    Publora answered 422 IDEMPOTENCY_KEY_CONFLICT forever (live run
    2026-11-24)."""
    import hashlib
    import json
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return hashlib.sha256(f"{repo}:{event_id}:{digest}".encode()).hexdigest()[:40]


def draft_body(content: str, platforms: list[str], media_urls: Optional[list[str]] = None,
               platform_settings: Optional[dict] = None) -> dict:
    body: dict[str, Any] = {"content": content, "platforms": list(platforms)}
    if media_urls:
        body["mediaUrls"] = list(media_urls)
    if platform_settings:
        body["platformSettings"] = platform_settings
    return body


class PubloraClient:
    def __init__(self, api_key: Optional[str] = None, timeout: float = 30.0, client_tag: str = ""):
        load_env()
        self.api_key = api_key or os.getenv("PUBLORA_API_KEY")
        if not self.api_key:
            raise PubloraError("PUBLORA_API_KEY is not set (Publora dashboard, Settings, API).")
        self.timeout = timeout
        self.client_tag = client_tag

    def _headers(self, idempotency_key: Optional[str] = None) -> dict:
        h = {"x-publora-key": self.api_key, "Content-Type": "application/json"}
        if self.client_tag:
            h["x-publora-client"] = self.client_tag
        if idempotency_key:
            h["Idempotency-Key"] = idempotency_key
        return h

    def _call(self, method: str, path: str, body: Any = None, idem: Optional[str] = None) -> dict:
        try:
            return _http.request(method, BASE_URL + path, headers=self._headers(idem), body=body,
                                 timeout=self.timeout, authenticated=True)
        except _http.HTTPError as exc:
            raise PubloraError(str(exc)) from None

    # ---- reads
    def list_connections(self) -> list[dict]:
        data = self._call("GET", "/platform-connections")
        rows = data.get("connections") or data.get("data") or []
        return rows if isinstance(rows, list) else []

    def get_post(self, post_group_id: str) -> dict:
        return self._call("GET", f"/get-post/{post_group_id}")

    def platform_limits(self) -> dict:
        return self._call("GET", "/platform-limits")

    # ---- writes
    def create_draft(self, *, content: str, platforms: list[str], media_urls: Optional[list[str]] = None,
                     platform_settings: Optional[dict] = None, idempotency_key: Optional[str] = None) -> dict:
        """Create a DRAFT. Returns {success, postGroupId, scheduledTime: null}.

        Pass a stable `idempotency_key` (`draft_key`) so a retried run replays
        the first response instead of creating a twin."""
        if not content or not content.strip():
            raise PubloraError("content is empty")
        validate_settings(platform_settings)
        body = draft_body(content, platforms, media_urls, platform_settings)
        return self._call("POST", "/create-post", body, idem=idempotency_key or str(uuid.uuid4()))

    def schedule_draft(self, post_group_id: str, scheduled_time_utc: str, *, confirmed: bool) -> dict:
        """Schedule an existing draft. `confirmed` must be True, and only after
        the user said yes to a read-back of text, channels, local time and
        timezone in this conversation. The autopilot never calls this."""
        if confirmed is not True:
            raise PubloraError("refusing to schedule without the user's explicit yes to a read-back")
        if not scheduled_time_utc.endswith("Z") and "+" not in scheduled_time_utc[10:]:
            raise PubloraError("scheduled time must be ISO 8601 UTC (ending in Z) or carry an offset")
        return self._call("PUT", f"/update-post/{post_group_id}",
                          {"status": "scheduled", "scheduledTime": scheduled_time_utc})

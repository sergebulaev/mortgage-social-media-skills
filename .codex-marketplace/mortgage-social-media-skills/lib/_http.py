"""Tiny stdlib HTTP helper shared by the feeds, the Publora and Pixfaro
clients and the autopilot. No third-party dependency, so the GitHub Action
runs on a bare runner with `python3` and nothing else.

Retries 408/429/5xx and network errors with exponential backoff and jitter.
Redirects are followed only for unauthenticated GETs: a request that carries a
key never follows a redirect, so the key cannot leak to another host.
"""
from __future__ import annotations

import json
import random
import time
import urllib.error
import urllib.request
from typing import Any, Optional

USER_AGENT = "social-media-skills/1.0 (+https://github.com/sergebulaev)"
RETRYABLE = {408, 429, 500, 502, 503, 504}


class HTTPError(RuntimeError):
    def __init__(self, message: str, status: Optional[int] = None, body: Any = None):
        super().__init__(message)
        self.status = status
        self.body = body


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):  # noqa: D401
        return None


_NO_REDIRECT = urllib.request.build_opener(_NoRedirect)
_DEFAULT = urllib.request.build_opener()


def request(method: str, url: str, *, headers: Optional[dict] = None, body: Any = None,
            timeout: float = 30.0, attempts: int = 3, authenticated: bool = False,
            raw: bool = False) -> Any:
    """Send one request. Returns parsed JSON (or bytes when raw=True).

    Raises HTTPError with `.status` and the parsed error body on 4xx/5xx.
    """
    hdrs = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    hdrs.update(headers or {})
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    opener = _NO_REDIRECT if authenticated else _DEFAULT
    last: Optional[Exception] = None
    for attempt in range(attempts):
        req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
        try:
            with opener.open(req, timeout=timeout) as resp:
                payload = resp.read()
            if raw:
                return payload
            if not payload:
                return {}
            try:
                return json.loads(payload.decode("utf-8"))
            except ValueError as exc:
                raise HTTPError(f"non-JSON response from {url}: {payload[:200]!r}") from exc
        except urllib.error.HTTPError as exc:
            text = exc.read()[:2000]
            try:
                parsed = json.loads(text.decode("utf-8"))
            except Exception:
                parsed = text.decode("utf-8", "replace")
            if 300 <= exc.code < 400:
                raise HTTPError(f"HTTP {exc.code}: redirect refused for an authenticated request",
                                exc.code, parsed) from None
            err = HTTPError(f"HTTP {exc.code} from {url.split('?')[0]}: {parsed}", exc.code, parsed)
            if exc.code not in RETRYABLE or attempt == attempts - 1:
                raise err from None
            last = err
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            if attempt == attempts - 1:
                raise HTTPError(f"network error for {url.split('?')[0]}: {exc}") from None
            last = exc
        time.sleep(0.6 * (2 ** attempt) + random.uniform(0, 0.3))
    raise HTTPError(str(last))


def get_bytes(url: str, *, headers: Optional[dict] = None, timeout: float = 30.0) -> bytes:
    return request("GET", url, headers=headers, timeout=timeout, raw=True)


def get_json(url: str, *, headers: Optional[dict] = None, timeout: float = 30.0) -> Any:
    return request("GET", url, headers=headers, timeout=timeout)

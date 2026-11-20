"""Pixfaro client for data cards (typeset templates) and, where a vertical
allows it, AI images. Stdlib only.

docs.pixfaro.com/llms.txt (read 2026-11-19):
- POST /v1/renders {template, slots, size?, style?, overlay?} -> {id, url, cost}
  Typeset HTML, not a model drawing: text is always crisp. $0.020 a card.
- GET  /v1/templates (public) -> the live catalog with slots and max lengths.
- POST /v1/images/generations {model, prompt, aspect_ratio, resolution}
- GET  /v1/key -> verifies a key, free.
- PUT  /v1/brand-kit/identity {name, handle, avatar_asset_id, palette} and
  POST /v1/assets {kind, data}: need a FULL-scope key.
Auth: `Authorization: Bearer pf_live_...`. Text past a slot's max is REJECTED
by the server, never truncated, so `cards.py` fits text before calling.
"""
from __future__ import annotations

from typing import Any, Optional

from . import _http
from ._env import pixfaro_key

BASE_URL = "https://api.pixfaro.com/v1"


class PixfaroError(RuntimeError):
    def __init__(self, message: str, status: Optional[int] = None):
        super().__init__(message)
        self.status = status


class PixfaroClient:
    def __init__(self, api_key: Optional[str] = None, timeout: float = 90.0):
        self.api_key = api_key or pixfaro_key()
        if not self.api_key:
            raise PixfaroError("No Pixfaro key (PIXFARO_KEY). Images are optional: the post works without one.")
        self.timeout = timeout

    def _call(self, method: str, path: str, body: Any = None) -> Any:
        try:
            return _http.request(method, BASE_URL + path, body=body, timeout=self.timeout,
                                 headers={"Authorization": f"Bearer {self.api_key}"}, authenticated=True)
        except _http.HTTPError as exc:
            raise PixfaroError(str(exc), exc.status) from None

    def whoami(self) -> dict:
        return self._call("GET", "/key")

    def render(self, template: str, slots: dict, *, size: str = "1:1", style: Any = None,
               overlay: Any = None) -> dict:
        body: dict[str, Any] = {"template": template, "slots": slots, "size": size}
        if style is not None:
            body["style"] = style
        if overlay is not None:
            body["overlay"] = overlay
        return self._call("POST", "/renders", body)

    def generate(self, prompt: str, *, model: str = "nano-banana-2", aspect_ratio: str = "1:1",
                 resolution: str = "1K") -> dict:
        return self._call("POST", "/images/generations",
                          {"model": model, "prompt": prompt, "aspect_ratio": aspect_ratio,
                           "resolution": resolution})

    def set_brand_identity(self, *, name: str, handle: str = "", palette: str = "") -> dict:
        body = {"name": name}
        if handle:
            body["handle"] = handle
        if palette:
            body["palette"] = palette
        return self._call("PUT", "/brand-kit/identity", body)


def list_templates(timeout: float = 20.0) -> list[dict]:
    """The public catalog; no key, no charge."""
    data = _http.get_json(BASE_URL + "/templates", timeout=timeout)
    return data.get("templates", data) if isinstance(data, dict) else data

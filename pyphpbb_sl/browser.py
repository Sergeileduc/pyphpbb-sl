# pyphpbb_sl/browser.py

from __future__ import annotations
from collections import namedtuple
from typing import Any

import httpx
from selectolax.parser import HTMLParser

Cookie = namedtuple("Cookie", ["key", "value"])


class BrowserError(Exception):
    pass


class Browser:
    """Async HTTP browser using httpx + selectolax."""

    def __init__(self, user_agent: str | None = None) -> None:
        self.client = httpx.AsyncClient(
            headers={"User-Agent": user_agent or "Mozilla/5.0 (ForumBot/1.0)"},
            timeout=10.0,
            follow_redirects=True,
        )

    # -----------------------------
    # GET HTML
    # -----------------------------
    async def get_html(self, url: str, **kwargs) -> HTMLParser:
        try:
            r = await self.client.get(url, **kwargs)
            r.raise_for_status()
            return HTMLParser(r.text)
        except httpx.HTTPError as e:
            raise BrowserError(f"GET failed for {url}: {e}") from e

    # -----------------------------
    # PARSE with SELECTOLAX
    # -----------------------------

    @staticmethod
    def html2root(html: str) -> HTMLParser:
        return HTMLParser(html)

    # -----------------------------
    # FORMS
    # -----------------------------

    async def get_form(self, url: str, form_id: str, **kwargs) -> dict[str, Any]:
        root = await self.get_html(url, **kwargs)
        form = root.css_first(f"form#{form_id}")

        if form is None:
            raise BrowserError(f"Form #{form_id} not found at {url}")

        return self._extract_form(form)

    @staticmethod
    def _extract_form(form_node) -> dict[str, Any]:
        values: dict[str, str] = {}

        for inp in form_node.css("input"):
            name = inp.attributes.get("name")
            value = inp.attributes.get("value", "")
            itype = inp.attributes.get("type")

            if itype == "submit":
                continue
            if not name:
                continue

            values[name] = value

        action = form_node.attributes.get("action")
        if not action:
            raise BrowserError("Form has no action attribute")

        return {"action": action, "values": values}

    # -----------------------------
    # SELECT TAGS
    # -----------------------------
    async def select_tag(self, url: str, selector: str) -> dict[str | None, str | None]:
        root = await self.get_html(url)
        items = root.css(selector)
        return {
            i.attributes["name"]: i.attributes.get("value", "")
            for i in items
            if "name" in i.attributes
        }

    # -----------------------------
    # POST
    # -----------------------------
    async def post(self, url: str, **kwargs) -> httpx.Response:
        try:
            r = await self.client.post(url, **kwargs)
            r.raise_for_status()
            return r
        except httpx.HTTPError as e:
            raise BrowserError(f"POST failed for {url}: {e}") from e

    # -----------------------------
    # COOKIES
    # -----------------------------
    def list_cookies(self) -> list[Cookie]:
        return [Cookie(cookie.name, cookie.value) for cookie in self.client.cookies.jar]

    # -----------------------------
    # CLOSE
    # -----------------------------

    async def close(self):
        await self.client.aclose()

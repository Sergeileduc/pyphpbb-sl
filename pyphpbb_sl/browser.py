#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Module to handle HTTP requests (with requests lib)."""

from urllib.error import HTTPError
import aiohttp
from bs4 import BeautifulSoup


class Browser:
    """Class to make HTTP requests."""

    def __init__(self, loop=None, session=None):
        """Initiate browser with given aiohttpsession, or create one.

        Args:
            loop (Event Loop, optional): asyncio event Loop. Defaults to None.
            session (aiohttp.session, optional): session. Defaults to None.
        """
        if session:
            self.session = session
            self._ownsession = False
        else:
            self.session = aiohttp.ClientSession(loop=loop)
            self._ownsession = True

    async def close(self):
        """Close aiohttp session if created by self."""
        if self._ownsession:
            await self.session.close()

    @staticmethod
    def html2soup(html):
        """Convert text to BeautifulSoup."""
        return BeautifulSoup(html, "html.parser")

    async def get_html(self, url):
        """Return HTML soup with Beautiful Soup.

        Args:
            url (str): url

        Returns:
            soup: HMTL soup

        """
        # headers = {}
        # headers['User-Agent'] = self.user_agent
        try:
            r = await self.session.get(url)
            soup = Browser.html2soup(await r.text())
            # print(soup)
            return soup
        except HTTPError as e:  # pragma: no cover
            print("HTTP Error")
            print(e)

    async def get_form(self, url, form_id):
        """Return form found in url as a dict."""
        try:
            soup = await self.get_html(url)
            form = soup.find("form", id=form_id)
            return self._get_form_values(form)
        except HTTPError as e:  # pragma: no cover
            print(e)
            raise

    @staticmethod
    def _get_form_values(soup):
        try:
            inputs = soup.find_all("input")
            values = {}
            for inp in inputs:
                if (inp.get("type") == "submit"
                        or not inp.get("name")
                        or not inp.get("value")):
                    continue
                values[inp["name"]] = inp["value"]
            return {"values": values, "action": soup["action"]}
        except AttributeError as e:  # pragma: no cover
            print("Attribute Error : " + str(e))
            return None
        except KeyError as e:  # pragma: no cover
            print("Key Error code : " + str(e))
            return None

    async def select_tag(self, url, tag):
        """Select tag in soup and return dict (name:value)."""
        soup = await self.get_html(url)
        items = soup.select(tag)
        return {i['name']: i['value'] for i in items if i.has_attr('value')}

    async def post(self, url, **kwargs):
        """Send POST request using requests."""
        return await self.session.post(url, **kwargs)

    def list_cookies(self):
        """List session cookies."""
        return self.session.cookie_jar

#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Module to handle HTTP requests (with requests lib)."""

import aiohttp
from urllib.error import HTTPError
from bs4 import BeautifulSoup


class Browser:
    """Class to make HTTP requests."""

    def __init__(self):
        """Init Browser with a requests.Session()."""
        try:
            self.session = aiohttp.ClientSession()
        except HTTPError as e:
            raise e

    async def close(self):
        await self.session.close()

    @staticmethod
    def html2soup(html):
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
        except HTTPError as e:
            print("HTTP Error")
            print(e)

    async def get_form(self, url, form_id):
        """Return form found in url as a dict."""
        try:
            soup = await self.get_html(url)
            form = soup.find("form", id=form_id)
            return self._get_form_values(form)
        except HTTPError as e:
            print(e)
            raise

    @staticmethod
    def _get_form_values(soup):
        try:
            inputs = soup.find_all("input")
            values = {}
            for input in inputs:
                if (
                    input.get("type") == "submit"
                    or not input.get("name")
                    or not input.get("value")
                ):
                    continue
                values[input["name"]] = input["value"]
            return {"values": values, "action": soup["action"]}
        except AttributeError as e:
            print("Attribute Error : " + str(e))
            return
        except KeyError as e:
            print("Key Error code : " + str(e))
            return

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
        return [cookie for cookie in self.session.cookie_jar]

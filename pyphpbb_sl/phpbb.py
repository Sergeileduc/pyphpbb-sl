#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Module to interract with phpBB forum."""


import asyncio
import logging
import re
import sys
from urllib.parse import urljoin
from urllib.error import HTTPError

from .browser import Browser

logger = logging.getLogger(__name__)

ucp_url = 'ucp.php'
login_mode = {'mode': 'login'}
logout_mode = {'mode': 'logout'}
cookie_u_pattern = r'phpbb\d?_.*_u'  # new cookie regex
cookie_sid_pattern = r'phpbb\d?_.*_sid'  # new cookie regex


class PhpBB(object):
    """Class to interract with phpBB forum."""

    form_id = 'postform'
    private_mess_url = 'ucp.php?i=pm&mode=compose'

    def __init__(self, host):
        """Init object with forum url (host) and Browser object."""
        self.host = host
        try:
            self.browser = Browser()
        except HTTPError as e:  # pragma: no cover
            logger.error(e)
            sys.exit(1)

    def __enter__(self):
        # here we return the object we can use with `as` in a context manager `with`  # noqa: E501
        return self

    def __exit__(self, type, value, traceback):
        if self.is_logged:
            self.logout()
        self.close()

    async def __aenter__(self):
        # here we return the object we can use with `as` in a context manager `async with`  # noqa: E501
        return self

    async def __aexit__(self, type, value, traceback):
        if self.is_logged:
            await self.logout()
        await self.close()

    def is_logged(self):
        """Check if logged in."""
        u = self._get_user_id()
        if u != 1:
            logger.info(f"login OK : {str(u)}")
            return True
        else:
            logger.info(f"login failed : {str(u)}")
            return False

    def is_logged_out(self):
        """Check if logged out."""
        u = self._get_user_id()
        if u != 1:
            logger.info(f"Still logged in : {str(u)}")
            return True
        else:
            logger.info(f"Signed out : {str(u)}")
            return False

    def _get_user_id(self):
        cookies = self.browser.list_cookies()
        for cookie in cookies:
            if re.search(cookie_u_pattern, cookie.key):
                return int(cookie.value)

    def _get_sid(self):
        cookies = self.browser.list_cookies()
        for cookie in cookies:
            if re.search(cookie_sid_pattern, cookie.key):
                sid = cookie.value
                return sid

    async def login(self, username, password):
        """Log in phpBB forum."""
        try:
            forum_ucp = urljoin(self.host, ucp_url)
            payload = await self.browser.select_tag(forum_ucp, "input")
            # for key, value in payload.items():
            #     print(key, value)
            payload['username'] = username
            payload['password'] = password
            await asyncio.sleep(1)
            await self.browser.post(forum_ucp, params=login_mode, data=payload)
            return self.is_logged()

        except HTTPError as e:  # pragma: no cover
            logger.error(e)
            return False

    async def logout(self):
        """Log out of phpBB forum."""
        try:
            # u_logout = Login(self.browser.session, self.host)
            # u_logout.send_logout()
            forum_ucp = urljoin(self.host, ucp_url)
            params = {'mode': 'logout', 'sid': self._get_sid()}
            r = await self.browser.post(forum_ucp,
                                        # headers=headers,
                                        params=params)
            r.close()
            return self.is_logged_out()
        except HTTPError as e:  # pragma: no cover
            logger.error(e)
            return False

    async def close(self):
        """Close request session (HTTP connection)."""
        try:
            await self.browser.close()
            logger.info("Session closed")
        except HTTPError as e:  # pragma: no cover
            logger.error(e)
            sys.exit(1)

    async def _make_add_receiver_payload(self, url, receiver):
        form = await self.browser.get_form(url, self.form_id)
        form['values']['username_list'] = receiver
        form['values']['add_to'] = "Ajouter"
        form['values']['addbbcode20'] = 100
        del form['values']['icon']
        url = urljoin(self.host, form['action'])
        payload = form['values']
        return url, payload

    async def _make_private_message_payload(self, url, receiverid, subject, message):  # noqa: E501
        form = await self.browser.get_form(url, self.form_id)
        form['values']['subject'] = subject
        form['values']['message'] = message
        form['values']['addbbcode20'] = 100
        form['values'][f'address_list[u][{receiverid}]'] = "to"
        form['values']['icon'] = 0
        # del form['values']['icon']
        form['values']['post'] = 'Envoyer'
        url = urljoin(self.host, form['action'])
        payload = form['values']
        return url, payload

    @staticmethod
    def parse_resp_find_receiver_id(html):
        """Parse html response after adding a receiver for private message.

        Return the UID of receiver.
        """
        soup = Browser.html2soup(html)
        user = soup.find('input', {'name': re.compile(r'address_list')})

        # Find receiver ID in the HTML response
        try:
            pattern_uid = r"address_list\[u\]\[(?P<UID>\d+)\]"
            matches = re.search(pattern_uid, user["name"])
            return matches.group("UID")
        except KeyError:
            return None

    async def send_private_message(self, receiver, subject, message):
        """Send private message."""
        logger.info(f"Trying to send private message to {receiver}")
        url = urljoin(self.host, self.private_mess_url)
        urlrep1, payload1 = await self._make_add_receiver_payload(url, receiver)  # noqa: E501
        await asyncio.sleep(2)

        # Add receiver
        r = await self.browser.session.post(urlrep1,
                                            # headers=headers,
                                            # params=self.login_mode,
                                            data=payload1)

        receiverid = PhpBB.parse_resp_find_receiver_id(await r.text())

        if receiverid is None:
            return

        urlrep2, payload2 = await self._make_private_message_payload(url, receiverid, subject, message)  # noqa: E501

        await asyncio.sleep(2)

        # Send message
        await self.browser.session.post(urlrep2,
                                        # headers=headers,
                                        # params=self.login_mode,
                                        data=payload2)

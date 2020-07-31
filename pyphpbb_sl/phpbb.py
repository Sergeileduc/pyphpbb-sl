#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Module to interract with phpBB forum."""


import asyncio
import logging
import re
import sys
from functools import partialmethod
from urllib.parse import urljoin
from urllib.error import HTTPError

from .browser import Browser

logger = logging.getLogger(__name__)

UCP_URL = 'ucp.php'
LOGIN_MODE = {'mode': 'login'}
LOGOUT_MODE = {'mode': 'logout'}
MESSAGE_COMPOSE = {'i': 'pm', 'mode': 'compose'}
INBOX = {'i': 'pm', 'folder': 'inbox'}
SENTBOX = {'i': 'pm', 'folder': 'sentbox'}
SUBMIT = 'Envoyer'
COOKIE_U_PATTERN = r'phpbb\d?_.*_u'  # new cookie regex
COOKIE_SID_PATTERN = r'phpbb\d?_.*_sid'  # new cookie regex
PM_ID_PATTERN = r"f=(?P<F>-?\d+)&p=(?P<P>\d+)"


class PhpBB:
    """Class to interract with phpBB forum."""

    FORM_ID = 'postform'
    # private_mess_url = 'ucp.php?i=pm&mode=compose'

    def __init__(self, host, loop=None, session=None):
        """Init object with host url.

        Args:
            host (str): url of phpbb forum
            loop (Event Loop, optional): event loop. Defaults to None. (asyncio.get_event_loop())
            session (aiohttp.ClientSession, optional). Defaults to None.
        """  # noqa: E501
        self.host = host
        self.unread_messages = []  # Private Messages Inbox unread messages
        try:
            self.browser = Browser(loop=loop, session=session)
        except HTTPError as e:  # pragma: no cover
            logger.error(e)
            sys.exit(1)

    def __enter__(self):
        # here we return the object we can use with `as` in a context manager `with`  # noqa: E501
        return self

    def __exit__(self, type_, value, traceback):
        if self.is_logged():
            self.logout()
        self.close()

    async def __aenter__(self):
        # here we return the object we can use with `as` in a context manager `async with`  # noqa: E501
        return self

    async def __aexit__(self, type_, value, traceback):
        if self.is_logged():
            await self.logout()
        await self.close()

    def is_logged(self):
        """Check if logged in."""
        u = self._get_user_id()
        if u != 1 and u is not None:
            logger.info("user is logged : %s", str(u))
            return True

        logger.info("login failed : %s", str(u))
        return False

    def is_logged_out(self):
        """Check if logged out."""
        u = self._get_user_id()
        if u != 1:
            logger.info("Still logged in : %s", str(u))
            return True

        logger.info("Signed out : %s", str(u))
        return False

    def _get_user_id(self):
        cookies = self.browser.list_cookies()
        for cookie in cookies:
            if re.search(COOKIE_U_PATTERN, cookie.key):
                return int(cookie.value)
        return None

    def _get_sid(self):
        cookies = self.browser.list_cookies()
        for cookie in cookies:
            if re.search(COOKIE_SID_PATTERN, cookie.key):
                sid = cookie.value
                return sid
        return None

    async def login(self, username, password):
        """Log in phpBB forum."""
        try:
            forum_ucp = urljoin(self.host, UCP_URL)
            payload = await self.browser.select_tag(forum_ucp, "input")
            # for key, value in payload.items():
            #     print(key, value)
            payload['username'] = username
            payload['password'] = password
            await asyncio.sleep(1)
            await self.browser.post(forum_ucp, params=LOGIN_MODE, data=payload)
            return self.is_logged()

        except HTTPError as e:  # pragma: no cover
            logger.error(e)
            return False

    async def logout(self):
        """Log out of phpBB forum."""
        try:
            # u_logout = Login(self.browser.session, self.host)
            # u_logout.send_logout()
            forum_ucp = urljoin(self.host, UCP_URL)
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
            logger.info("Browser closed")
        except HTTPError as e:  # pragma: no cover
            logger.error(e)
            sys.exit(1)

    async def _make_add_receiver_payload(self, url, receiver):
        form = await self.browser.get_form(url, PhpBB.FORM_ID, params=MESSAGE_COMPOSE)  # noqa: E501
        form['values']['username_list'] = receiver
        form['values']['add_to'] = "Ajouter"
        form['values']['addbbcode20'] = 100
        del form['values']['icon']
        url = urljoin(self.host, form['action'])
        payload = form['values']
        return url, payload

    async def _make_private_message_payload(self, url, receiverid, subject, message):  # noqa: E501
        form = await self.browser.get_form(url, PhpBB.FORM_ID)
        form['values']['subject'] = subject
        form['values']['message'] = message
        form['values']['addbbcode20'] = 100
        form['values'][f'address_list[u][{receiverid}]'] = "to"
        form['values']['icon'] = 0
        # del form['values']['icon']
        form['values']['post'] = SUBMIT
        url = urljoin(self.host, form['action'])
        payload = form['values']
        return url, payload

    async def _make_delete_mp_payload(self, message):  # noqa: E501
        f, p = PhpBB._extract_mp_number_id(message)
        params = {'i': 'pm', 'mode': 'compose', 'action': 'delete',
                  'f': f, 'p': p}
        url = urljoin(self.host, UCP_URL)
        form = await self.browser.get_form(url, "confirm", params=params)
        form['values']['confirm'] = "Oui"
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
        except (KeyError, TypeError):
            logger.error("Cant't add receiver, probably not a valid pseudonyme")  # noqa: E501
            return None

    async def send_private_message(self, receiver, subject, message):
        """Send private message."""
        logger.info("Trying to send private message to %s", receiver)
        url = urljoin(self.host, UCP_URL)
        urlrep1, payload1 = await self._make_add_receiver_payload(url, receiver)  # noqa: E501
        await asyncio.sleep(2)

        # Add receiver
        resp = await self.browser.session.post(urlrep1,
                                               # headers=headers,
                                               data=payload1)

        receiverid = PhpBB.parse_resp_find_receiver_id(await resp.text())

        if receiverid is None:
            return False

        urlrep2, payload2 = await self._make_private_message_payload(urlrep1, receiverid, subject, message)  # noqa: E501

        await asyncio.sleep(2)

        # Send message
        await self.browser.session.post(urlrep2,
                                        # headers=headers,
                                        data=payload2)
        return True

    @staticmethod
    def _parse_inbox_mess(soup_item):
        raw = soup_item.find("a", class_="topictitle")
        sender = soup_item.find("a", class_=["username", "username-coloured"]).text  # noqa: E501
        return {'subject': raw.text,
                'url': raw["href"],
                'from_': sender,
                'unread': True,
                'content': None}

    async def fetch_box(self, class_, box=INBOX):
        """Fetch private messages inbox and return short descriptions.

        Return list of dicts.
        """
        url = urljoin(self.host, UCP_URL)
        soup = await self.browser.get_html(url, params=box)
        raw_unread_list = soup.find_all("dl", class_=class_)
        self.unread_messages = [PhpBB._parse_inbox_mess(item) for item in raw_unread_list]  # noqa: E501
        return self.unread_messages

    fetch_unread_messages = partialmethod(fetch_box, "pm_unread")
    fetch_read_messages = partialmethod(fetch_box, "pm_read")
    fetch_sent_messages = partialmethod(fetch_box, "pm_read", box=SENTBOX)

    def find_expected_message_by_user(self, sender_name):
        """Find message in unread_messages by sender name. Return first found.
        """
        for message in self.unread_messages:
            if message['from_'] == sender_name:
                return message
        return None

    async def read_private_message(self, message_dict):
        """Read private message."""
        url = urljoin(self.host, message_dict['url'])
        soup = await self.browser.get_html(url)
        content = soup.find("div", class_="content")
        message_dict['unread'] = False
        message_dict['content'] = content.text
        return message_dict

    @staticmethod
    def _extract_mp_number_id(message):
        """Extract f value and p value} in './ucp.php?i=pm&mode=view&f=0&p=11850'."""  # noqa: E501
        match = re.search(PM_ID_PATTERN, message['url'])
        f = int(match.group("F"))
        p = int(match.group("P"))
        return f, p

    async def delete_mp(self, message):
        url, payload = await self._make_delete_mp_payload(message)
        await self.browser.session.post(url,
                                        # headers=headers,
                                        data=payload)
        logging.info("message deleted : %s", message['url'][-7:])
        return True

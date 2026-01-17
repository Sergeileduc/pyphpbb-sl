#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Module to interract with phpBB forum."""

import asyncio
import logging
import re
import sys
from functools import partialmethod
from typing import Tuple
from urllib.error import HTTPError
from urllib.parse import urljoin

from .browser import Browser
from pyphpbb_sl.models import Message

logger = logging.getLogger(__name__)

UCP_URL = "ucp.php"
MEMBERS_URL = "memberlist.php"
LOGIN_MODE = {"mode": "login"}
LOGOUT_MODE = {"mode": "logout"}
VIEW_PROFILE_MODE = {"mode": "viewprofile"}
MESSAGE_COMPOSE = {"i": "pm", "mode": "compose"}
MESSAGE_COMPOSE_DELETE = dict(MESSAGE_COMPOSE, **{"action": "delete"})
INBOX = {"i": "pm", "folder": "inbox"}
SENTBOX = {"i": "pm", "folder": "sentbox"}
SUBMIT = "Envoyer"
COOKIE_U_PATTERN = r"phpbb\d?_.*_u"  # new cookie regex
COOKIE_SID_PATTERN = r"phpbb\d?_.*_sid"  # new cookie regex
PM_ID_PATTERN = re.compile(r"f=(?P<F>-?\d+)&p=(?P<P>\d+)")
USER_ID_PATTERN = re.compile(r"&u=(?P<UID>\d+)")


class PhpBB:
    """Class to interract with phpBB forum."""

    FORM_ID = "postform"
    # private_mess_url = 'ucp.php?i=pm&mode=compose'

    def __init__(self, host):
        """Init object with host url.

        Args:
            host (str): url of phpbb forum
        """  # noqa: E501
        self.host = host
        self.unread_messages = []  # Private Messages Inbox unread messages
        try:
            self.browser = Browser()
        except HTTPError as e:  # pragma: no cover
            logger.error(e)
            sys.exit(1)

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

    def _get_user_id(self) -> int | None:
        cookies = self.browser.list_cookies()

        for cookie in cookies:
            if re.search(COOKIE_U_PATTERN, cookie.key):
                return int(cookie.value) if str(cookie.value).isdigit() else None

        return None

    def _get_sid(self) -> str | None:
        cookies = self.browser.list_cookies()

        for cookie in cookies:
            if cookie.key.endswith("_sid"):
                return str(cookie.value) if cookie.value else None

        return None

    async def login(self, username, password):
        """Log in phpBB forum."""
        try:
            forum_ucp = urljoin(self.host, UCP_URL)
            payload = await self.browser.select_tag(forum_ucp, "input")
            # for key, value in payload.items():
            #     print(key, value)
            payload["username"] = username
            payload["password"] = password
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
            params = dict(LOGOUT_MODE, sid=self._get_sid())
            await self.browser.post(
                forum_ucp,
                # headers=headers,
                params=params,
            )
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
        form["values"]["username_list"] = receiver
        form["values"]["add_to"] = "Ajouter"
        form["values"]["addbbcode20"] = 100
        del form["values"]["icon"]
        url = urljoin(self.host, form["action"])
        payload = form["values"]
        return url, payload

    async def _make_private_message_payload(self, url, receiverid, subject, message):  # noqa: E501
        form = await self.browser.get_form(url, PhpBB.FORM_ID)
        form["values"]["subject"] = subject
        form["values"]["message"] = message
        form["values"]["addbbcode20"] = 100
        form["values"][f"address_list[u][{receiverid}]"] = "to"
        form["values"]["icon"] = 0
        # del form['values']['icon']
        form["values"]["post"] = SUBMIT
        url = urljoin(self.host, form["action"])
        payload = form["values"]
        return url, payload

    async def _make_delete_mp_payload(self, message):  # noqa: E501
        f, p = PhpBB._extract_mp_number_id(message)
        params = dict(MESSAGE_COMPOSE_DELETE, f=f, p=p)
        url = urljoin(self.host, UCP_URL)
        form = await self.browser.get_form(url, "confirm", params=params)
        form["values"]["confirm"] = "Oui"
        url = urljoin(self.host, form["action"])
        payload = form["values"]
        return url, payload

    @staticmethod
    def parse_resp_find_receiver_id(html: str) -> int | None:
        """Parse html response after adding a receiver for private message.

        Return the UID of receiver.
        """
        root = Browser.html2root(html)

        # 1) Trouver l'input dont le name contient "address_list"
        user = None
        for node in root.css("input"):
            name = node.attributes.get("name") or ""
            if "address_list" in name:  # plus simple que regex ici
                user = node
                break

        if user is None:
            logger.error("Receiver not found in HTML response")
            return None

        # 2) Extraire l'UID depuis l'attribut name
        name_attr = user.attributes.get("name") or ""

        pattern_uid = r"address_list\[u\]\[(?P<UID>\d+)\]"
        match = re.search(pattern_uid, name_attr)

        if not match:
            logger.error("Can't extract UID from receiver input")
            return None

        return int(match.group("UID"))

    async def send_private_message(
        self, receiver: str | None, subject: str, message: str
    ) -> bool:  # noqa: E501
        """Send private message."""
        logger.info("Trying to send private message to %s", receiver)
        url = urljoin(self.host, UCP_URL)
        urlrep1, payload1 = await self._make_add_receiver_payload(url, receiver)
        await asyncio.sleep(2)

        # Add receiver
        resp = await self.browser.post(
            urlrep1,
            # headers=headers,
            data=payload1,
        )

        receiverid = PhpBB.parse_resp_find_receiver_id(resp.text)

        if receiverid is None:  # pragma: no cover
            return False

        urlrep2, payload2 = await self._make_private_message_payload(
            urlrep1, receiverid, subject, message
        )  # noqa: E501

        await asyncio.sleep(2)

        # Send message
        await self.browser.post(
            urlrep2,
            # headers=headers,
            data=payload2,
        )
        return True

    @staticmethod
    def _parse_inbox_mess(node) -> Message:
        raw = node.css_first("a.topictitle")
        sender_node = node.css_first("a.username, a.username-coloured")

        subject = raw.text() if raw else ""
        url = raw.attributes.get("href") if raw else ""
        sender = sender_node.text() if sender_node else ""

        # Extract message ID from URL
        match = PM_ID_PATTERN.search(url)
        msg_id = int(match.group("P")) if match else -1

        return Message(
            id=msg_id,
            subject=subject,
            url=url,
            sender=sender,
            receiver=None,  # inbox → receiver = toi
            content=None,
            unread=True,
        )

    async def fetch_box(self, class_: str, box=INBOX):
        """Fetch private messages inbox and return short descriptions."""

        url = urljoin(self.host, UCP_URL)

        # get_html() retourne déjà un HTMLParser
        root = await self.browser.get_html(url, params=box)

        # Sélectionne tous les <dl class="pm_unread"> ou autre class_
        raw_unread_list = root.css(f"dl.{class_}")

        self.unread_messages = [
            PhpBB._parse_inbox_mess(item) for item in raw_unread_list
        ]

        return self.unread_messages

    fetch_unread_messages = partialmethod(fetch_box, "pm_unread")
    fetch_read_messages = partialmethod(fetch_box, "pm_read")
    fetch_sent_messages = partialmethod(fetch_box, "pm_read", box=SENTBOX)

    def find_expected_message_by_user(self, sender_name: str):
        """Find message in unread_messages by sender name. Return first found."""
        return next(
            (
                message
                for message in self.unread_messages
                if message.sender == sender_name
            ),
            None,
        )

    async def read_private_message(self, message: Message) -> Message:
        url = urljoin(self.host, message.url)
        root = await self.browser.get_html(url)

        content_node = root.css_first("div.content")
        content = content_node.text().strip() if content_node else ""

        return Message(
            id=message.id,
            subject=message.subject,
            url=message.url,
            sender=message.sender,
            receiver=message.receiver,
            content=content,
            unread=False,
        )

    @staticmethod
    def _extract_mp_number_id(message: Message) -> Tuple[int, int]:
        """Extract f value and p value} in './ucp.php?i=pm&mode=view&f=0&p=11850'."""  # noqa: E501
        match = PM_ID_PATTERN.search(message.url)
        if not match:
            raise ValueError
        f = int(match["F"])
        p = int(match["P"])
        return f, p

    @staticmethod
    def _parse_age(node) -> int:
        """Extract age from a birthday username node."""
        # Exemple HTML : <a class="username">Foo</a> (45),
        nxt = node.next  # nœud suivant dans le DOM

        if not nxt:
            return 0

        text = nxt.text().strip()  # ex: "(45)," ou "(45)" ou " (45), "

        # Extraire les chiffres
        m = re.search(r"\d+", text)
        return int(m.group(0)) if m else 0

    async def delete_mp(self, message: Message) -> bool:
        """Delete given private message."""
        url, payload = await self._make_delete_mp_payload(message)
        await self.browser.post(
            url,
            # headers=headers,
            data=payload,
        )
        logging.info("message deleted : %s", message.url[-7:])
        return True

    async def get_birthdays(self):
        """Fetch today's birthdays.

        Return list of dicts [{'name': 'Foo', 'age': 26},]
        age is set to '0' if not found.
        """
        root = await self.browser.get_html(self.host)
        raw = root.css_first(
            "div.inner ul.topiclist.forums li.row div.birthday-list p strong"
        )
        if not raw:
            return []
        bdays = raw.css("a.username")

        return [
            {
                "name": b.text().strip(),
                "age": PhpBB._parse_age(b),
            }
            for b in bdays
        ]

    async def get_member_rank(self, member_name: str) -> str:
        """Fetch the forum rank for given member_name."""
        url = urljoin(self.host, MEMBERS_URL)
        params = dict(VIEW_PROFILE_MODE, un=member_name)

        root = await self.browser.get_html(url, params=params)

        # Sélecteur CSS équivalent à soup.find("dd")
        dd = root.css_first("dd")
        if not dd:
            return ""

        return dd.text().strip()

    async def get_member_uid(self, member_name: str) -> int:
        """Fetch the user id number for given member_name."""
        try:
            url = urljoin(self.host, MEMBERS_URL)
            params = dict(VIEW_PROFILE_MODE, un=member_name)
            root = await self.browser.get_html(url, params=params)

            # <link rel="canonical" href="...">
            link = root.css_first("link[rel=canonical]")
            if not link:
                return 0

            href = link.attributes.get("href")
            if not href:
                return 0

            match = USER_ID_PATTERN.search(href)
            if not match:
                return 0

            return int(match.group("UID"))

        except Exception as e:
            print(e)
            return 0

    async def get_member_infos(self, member_name: str) -> Tuple[int, str]:
        """Fetch the user id number AND rank for given member_name."""
        uid = 0
        rank = ""

        try:
            url = urljoin(self.host, MEMBERS_URL)
            params = dict(VIEW_PROFILE_MODE, un=member_name)
            root = await self.browser.get_html(url, params=params)

            # 1) canonical URL
            link = root.css_first("link[rel=canonical]")
            if link and "href" in link.attributes:
                canonical_url: str = link.attributes["href"] or ""
                match = USER_ID_PATTERN.search(canonical_url)
                if match:
                    uid = int(match.group("UID"))

            # 2) rank = premier <dd>
            dd = root.css_first("dd")
            if dd:
                rank = dd.text().strip()

        except Exception as e:
            logger.error(e)

        return uid, rank

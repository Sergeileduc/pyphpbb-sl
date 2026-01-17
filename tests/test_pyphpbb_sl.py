#!/usr/bin/env python

"""Tests for `pyphpbb_sl` package."""

from collections import namedtuple

import pytest
from selectolax.parser import HTMLParser

from pyphpbb_sl import Message, PhpBB


@pytest.fixture
def cookies():
    """Mock session cookies."""
    Cookie = namedtuple("Cookie", ["key", "value"])
    return [
        Cookie("phpbb_pth98_u", 43533),
        Cookie("phpbb_pth98_k", ""),
        Cookie("phpbb_pth98_sid", "ffac899f2ff73"),
    ]


@pytest.fixture
def not_logged_cookies():
    """Mock session cookies."""
    Cookie = namedtuple("Cookie", ["key", "value"])
    return [Cookie("phpbb_pth98_u", 1), Cookie("phpbb_pth98_k", "")]


@pytest.fixture
async def phpbb_dummy():
    phpbb = PhpBB("http://dummy.io")
    try:
        yield phpbb
    finally:
        await phpbb.close()


@pytest.mark.asyncio
async def test_init_close():
    phpbb = PhpBB("http://dummy.io")
    await phpbb.close()


@pytest.mark.asyncio
async def test_get_user_id(phpbb_dummy, cookies):
    """ "Test get_user_id"""
    # Mock cookies
    phpbb_dummy.browser.list_cookies = lambda: cookies

    # Test la méthode interne
    assert phpbb_dummy._get_user_id() == 43533


@pytest.mark.asyncio
async def test_get_sid(phpbb_dummy, cookies):
    """Test get user SID."""

    phpbb_dummy.browser.list_cookies = lambda: cookies
    assert phpbb_dummy._get_sid() == "ffac899f2ff73"


@pytest.mark.asyncio
async def test_is_logged(phpbb_dummy, cookies):
    """Test get user SID."""
    phpbb_dummy.browser.list_cookies = lambda: cookies
    assert phpbb_dummy.is_logged()


@pytest.mark.asyncio
async def test_is_logged_fail(phpbb_dummy, not_logged_cookies):
    """Test fail login."""
    phpbb_dummy.browser.list_cookies = lambda: not_logged_cookies
    assert not phpbb_dummy.is_logged()


@pytest.fixture
def message1() -> Message:
    return Message(
        subject="Sent by python.",
        url="./ucp.php?i=pm&mode=view&f=0&p=11850",
        fromto="Foobar",
        unread=True,
        content=None,
    )


def test__extract_mp_number_id1(message1: Message):
    f, p = PhpBB._extract_mp_number_id(message1)
    assert f == 0
    assert p == 11850


@pytest.fixture
def message2() -> Message:
    return Message(
        subject="Sent by python.",
        url="./ucp.php?i=pm&mode=view&f=-1&p=11852",
        fromto="Foobar",
        unread=True,
        content=None,
    )


def test__extract_mp_number_id2(message2):
    f, p = PhpBB._extract_mp_number_id(message2)
    assert f == -1
    assert p == 11852


html = """
<strong>
 <a class="username" href="./memberlist.php?mode=viewprofile&amp;u=1059">
  Superman
 </a>
 ,
 <a class="username" href="./memberlist.php?mode=viewprofile&amp;u=22820">
  Wolverine
 </a>
 ,
 <a class="username" href="./memberlist.php?mode=viewprofile&amp;u=6870">
  Wonder-Woman
 </a>
 (27),
 <a class="username" href="./memberlist.php?mode=viewprofile&amp;u=30914">
  Spider-Man
 </a>
 (27),
 <a class="username" href="./memberlist.php?mode=viewprofile&amp;u=23851">
  Tony Stark
 </a>
 (35)
 <a class="username" href="./memberlist.php?mode=viewprofile&amp;u=23852">
  Batman
 </a>
</strong>
"""

root = HTMLParser(html)
birthdays = root.css("a.username")

testdata = [
    (birthdays[0], 0),
    (birthdays[1], 0),
    (birthdays[2], 27),
    (birthdays[3], 27),
    (birthdays[4], 35),
    (birthdays[5], 0),
]


@pytest.mark.parametrize("tag,expected", testdata)
def test_parse_age(tag, expected):
    age = PhpBB._parse_age(tag)
    assert age == expected

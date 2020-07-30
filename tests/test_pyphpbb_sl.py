#!/usr/bin/env python

"""Tests for `pyphpbb_sl` package."""

from collections import namedtuple
import pytest


from pyphpbb_sl import PhpBB


@pytest.fixture
def cookies():
    """Mock session cookies."""
    Cookie = namedtuple('Cookie', ['key', 'value'])
    return [Cookie("phpbb_pth98_u", 43533),
            Cookie("phpbb_pth98_k", ""),
            Cookie("phpbb_pth98_sid", "ffac899f2ff73")]


@pytest.fixture
def not_logged_cookies():
    """Mock session cookies."""
    Cookie = namedtuple('Cookie', ['key', 'value'])
    return [Cookie("phpbb_pth98_u", 1),
            Cookie("phpbb_pth98_k", "")]


@pytest.mark.asyncio
async def test_init_close():
    phpbb = PhpBB("http://dummy.io")
    await phpbb.close()


@pytest.mark.asyncio
async def test_get_user_id(cookies):
    """Test _get_user_id."""
    def mock_cookies():
        return cookies
    async with PhpBB("http://dummy.io") as phpbb:
        phpbb.browser.list_cookies = mock_cookies
    assert phpbb._get_user_id() == 43533


@pytest.mark.asyncio
async def test_get_sid(cookies):
    """Test get user SID."""
    def mock_cookies():
        return cookies
    async with PhpBB("http://dummy.io") as phpbb:
        phpbb.browser.list_cookies = mock_cookies
    assert phpbb._get_sid() == "ffac899f2ff73"


@pytest.mark.asyncio
async def test_is_logged(cookies):
    """Test get user SID."""
    def mock_cookies():
        return cookies
    async with PhpBB("http://dummy.io") as phpbb:
        phpbb.browser.list_cookies = mock_cookies
        assert phpbb.is_logged()


@pytest.mark.asyncio
async def test_is_logged_fail(not_logged_cookies):
    """Test get user SID."""
    def mock_cookies():
        return not_logged_cookies
    async with PhpBB("http://dummy.io") as phpbb:
        phpbb.browser.list_cookies = mock_cookies
        assert not phpbb.is_logged()

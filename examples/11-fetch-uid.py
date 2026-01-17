#!/usr/bin/env python
"""Docstring."""

# import aiohttp
import asyncio
import logging
import os

from dotenv import load_dotenv

from pyphpbb_sl import PhpBB

logging.basicConfig(level=logging.WARNING)

# Parse a .env file and then load all the variables found as environment variables.  # noqa: E501
load_dotenv()

host = os.getenv("HOST")

username = os.getenv("SENDER_NAME")
password = os.getenv("SENDER_PASSWORD")

logging.debug("host %s", host)
logging.debug("username %s", username)
logging.debug("password %s", password)

querry_user: str = os.getenv("RECEIVER_NAME") or ""


# Context Manager code
async def main():
    async with PhpBB(host) as phpbb:
        await phpbb.login(username, password)
        uid = await phpbb.get_member_uid(querry_user)
        print(uid)


asyncio.run(main())

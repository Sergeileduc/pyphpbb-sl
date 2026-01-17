#!/usr/bin/env python
"""Docstring."""

# import aiohttp
import asyncio
import logging
import os

from dotenv import load_dotenv

from pyphpbb_sl import PhpBB

logging.basicConfig(level=logging.INFO)

# Parse a .env file and then load all the variables found as environment variables.  # noqa: E501
load_dotenv()

host = os.getenv("HOST")

username = os.getenv("RECEIVER_NAME")
password = os.getenv("RECEIVER_PASSWORD")
sender_name = os.getenv("SENDER_NAME")


logging.debug("host %s", host)
logging.debug("username %s", username)
logging.debug("password %s", password)


# Context Manager code
async def main():
    async with PhpBB(host) as phpbb:
        await phpbb.login(username, password)
        unread_mess_list = await phpbb.fetch_read_messages()
        print("Here are your read messages :")
        filterd_mess_by_sender = [m for m in unread_mess_list if m.sender == sender_name]
        print(*filterd_mess_by_sender, sep="\n")


asyncio.run(main())

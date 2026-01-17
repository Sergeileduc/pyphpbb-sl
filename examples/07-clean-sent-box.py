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

username = os.getenv("SENDER_NAME")
password = os.getenv("SENDER_PASSWORD")
receiver = os.getenv("RECEIVER_NAME")

logging.debug("host %s", host)
logging.debug("username %s", username)
logging.debug("password %s", password)
logging.debug("receiver %s", password)


# Context Manager code
async def main():
    async with PhpBB(host) as phpbb:
        await phpbb.login(username, password)
        sent_message_list = await phpbb.fetch_sent_messages()
        filtered_sent_message_list = [m for m in sent_message_list if m.receiver == receiver]

        print(*filtered_sent_message_list, sep="\n")
        for m in filtered_sent_message_list:
            await phpbb.delete_mp(m)


asyncio.run(main())

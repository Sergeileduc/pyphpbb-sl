#!/usr/bin/env python
# -*-coding:utf-8 -*-
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

expect_message_from_user = os.getenv("SENDER_NAME")


# Context Manager code
async def main():
    async with PhpBB(host) as phpbb:
        await phpbb.login(username, password)
        await phpbb.fetch_unread_messages()
        message_to_read = phpbb.find_expected_message_by_user(expect_message_from_user)  # noqa: E501
        if message_to_read:
            message = await phpbb.read_private_message(message_to_read)
            print(message)


asyncio.run(main())

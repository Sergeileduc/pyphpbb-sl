#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""Docstring."""

# import aiohttp
import asyncio
import logging
import os
import time
from secrets import token_hex

from dotenv import load_dotenv

from pyphpbb_sl import PhpBB

logging.basicConfig(level=logging.INFO)

# Parse a .env file and then load all the variables found as environment variables.  # noqa: E501
load_dotenv()

host = os.getenv("HOST")

username = os.getenv("RECEIVER_NAME")
password = os.getenv("RECEIVER_PASSWORD")

expect_message_from_user = os.getenv("SENDER_NAME")

token = token_hex(16)


async def try_to_verify(expected):
    # Connect to phpbb forum and fetch unread PM
    async with PhpBB(host) as phpbb:
        await phpbb.login(username, password)
        await phpbb.fetch_unread_messages()
        # Read message from expected user
        message_to_read = phpbb.find_expected_message_by_user(expected)  # noqa: E501
        if message_to_read:
            message = await phpbb.read_private_message(message_to_read)
            if message['content'] == token:
                print("Valid token ! GOOD")
                return True
            else:
                print("Invalid token ! BAD !")
                return False
        return False


# Context Manager code
async def main():
    print(f"Please send the token :\n{token} to the user {username}.\n"
          f"You're expected to be {expect_message_from_user}.\n"
          "You have 5 minutes.")
    timeout = time.time() + 5 * 60   # 50 minutes from now
    while True:
        await asyncio.sleep(30)  # will fetch PM every 30 seconds
        if time.time() > timeout:
            break
        valid = await try_to_verify(expect_message_from_user)
        if valid:
            # do_stuff()
            break


asyncio.run(main())

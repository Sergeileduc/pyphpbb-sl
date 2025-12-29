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

logging.debug("host %s", host)
logging.debug("username %s", username)
logging.debug("password %s", password)


# Context Manager code
async def main():
    async with PhpBB(host) as phpbb:
        await phpbb.login(username, password)
        unread_mess_list = await phpbb.fetch_unread_messages()
        print("Here are your unread messages :")
        print(*unread_mess_list, sep='\n')

        print(
            "\nHere are the contents of messages (messages have been marked as read) :"
        )  # noqa: E501
        for unread_mess in unread_mess_list:
            message = await phpbb.read_private_message(unread_mess)
            print(message)


asyncio.run(main())

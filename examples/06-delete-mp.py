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
sender = os.getenv("SENDER_NAME")


logging.debug("host %s", host)
logging.debug("username %s", username)
logging.debug("password %s", password)


# Context Manager code
async def main():
    async with PhpBB(host) as phpbb:
        await phpbb.login(username, password)
        read_mess_list = await phpbb.fetch_read_messages()
        print("Here are your read messages :")
        filterd_mess_by_sender = [m for m in read_mess_list if m['fromto'] == sender]  # noqa: E501
        print(*filterd_mess_by_sender, sep='\n')
        for m in filterd_mess_by_sender:
            await phpbb.delete_mp(m)

asyncio.run(main())

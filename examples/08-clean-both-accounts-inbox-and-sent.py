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

account_a = os.getenv("RECEIVER_NAME")
password_a = os.getenv("RECEIVER_PASSWORD")
account_b = os.getenv("SENDER_NAME")
password_b = os.getenv("SENDER_PASSWORD")


# logging.debug("host %s", host)
# logging.debug("username %s", account_A)
# logging.debug("password %s", password_A)


# Context Manager code
async def clean(user, password, other_user):
    async with PhpBB(host) as phpbb:
        await phpbb.login(user, password)

        # Unread messages
        logging.info("clean account A unread mess")
        unread_mess_list = await phpbb.fetch_unread_messages()
        filtered_unread_mess_by_sender = [m for m in unread_mess_list if m.sender == other_user]
        for m in filtered_unread_mess_by_sender:
            await phpbb.delete_mp(m)

        # Read messages
        logging.info("clean account A read mess")
        read_mess_list = await phpbb.fetch_read_messages()
        filtered_mess_by_sender = [m for m in read_mess_list if m.sender == other_user]
        for m in filtered_mess_by_sender:
            await phpbb.delete_mp(m)

        # Sent messages
        logging.info("clean account A sent mess")
        sent_message_list = await phpbb.fetch_sent_messages()
        filtered_sent_message_list = [m for m in sent_message_list if m.receiver == other_user]
        for m in filtered_sent_message_list:
            await phpbb.delete_mp(m)


async def main():
    await clean(account_a, password_a, account_b)
    await asyncio.sleep(1)
    await clean(account_b, password_b, account_a)


asyncio.run(main())

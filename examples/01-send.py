#!/usr/bin/env python
"""Docstring."""

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
subject = "Sent by python."
message = "This message was sent by python."

# DEBUG##############################
logging.debug("host %s", host)
logging.debug("username %s", username)
logging.debug("password %s", password)
logging.debug("receiver %s", receiver)
# DEBUG##############################


# Context Manager code
async def main():
    print(f"host : {host}")
    async with PhpBB(host) as phpbb:
        await phpbb.login(username, password)
        await phpbb.send_private_message(receiver=receiver, subject=subject, message=message)


asyncio.run(main())

# async def main():
#     phpbb = PhpBB(host)
#     await phpbb.login(username, password)
#     await phpbb.send_private_message(receiver=receiver,
#                                      subject=subject,
#                                      message=message)

#     await phpbb.logout()
#     await phpbb.close()

# asyncio.run(main())

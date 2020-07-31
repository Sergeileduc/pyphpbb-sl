import asyncio
import logging
import os
from secrets import token_hex

import pytest

from dotenv import load_dotenv
from pyphpbb_sl import PhpBB

logging.basicConfig(level=logging.INFO)


# Parse a .env file and then load all the variables found as environment variables.  # noqa: E501
load_dotenv()

host = os.getenv("HOST")

sender_name = os.getenv("SENDER_NAME")
sender_password = os.getenv("SENDER_PASSWORD")

receiver_name = os.getenv("RECEIVER_NAME")
receiver_password = os.getenv("RECEIVER_PASSWORD")

token = token_hex(16)


async def send():
    """Send message with token to receiver."""
    async with PhpBB(host) as phpbb:
        await phpbb.login(sender_name, sender_password)
        await phpbb.send_private_message(receiver=receiver_name,
                                         subject="validate my token",
                                         message=token)


async def receive():
    async with PhpBB(host) as phpbb:
        await phpbb.login(receiver_name, receiver_password)
        await phpbb.fetch_unread_messages()
        message_to_read = phpbb.find_expected_message_by_user(sender_name)
        if message_to_read:
            message = await phpbb.read_private_message(message_to_read)
            print(message)

        assert message['content'] == token


@pytest.mark.asyncio
async def test_token():
    """Send and receive"""
    await send()
    await asyncio.sleep(3)
    await receive()

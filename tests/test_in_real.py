import aiohttp
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


async def delete():
    """Delete last message from sender."""
    async with PhpBB(host) as phpbb:
        await phpbb.login(receiver_name, receiver_password)
        read_mess_list = await phpbb.fetch_read_messages()
        filterd_mess_by_sender = [m for m in read_mess_list if m['fromto'] == sender_name]  # noqa: E501
        await phpbb.delete_mp(filterd_mess_by_sender[0])


@pytest.mark.asyncio
async def test_token():
    """Send and receive"""
    await send()
    await asyncio.sleep(3)
    await receive()
    await asyncio.sleep(2)
    await delete()


@pytest.mark.asyncio
async def test_misc():

    session = aiohttp.ClientSession()

    """Send and receive"""
    async with PhpBB(host, session=session) as phpbb:
        await phpbb.login(sender_name, sender_password)
        messages = await phpbb.fetch_read_messages()
        url, payload = await phpbb._make_delete_mp_payload(messages[0])  # #pylint: disable=unused-variable  # noqa: E501

    await session.close()


@pytest.mark.asyncio
async def test_fetch_birthdays():
    """Fetch birthdays"""
    async with PhpBB(host) as phpbb:
        await phpbb.login(receiver_name, receiver_password)
        out = await phpbb.get_birthdays()
    print(*out, sep='\n')
    assert out is not None


@pytest.mark.asyncio
async def test_fetch_rank():
    """Fetch rank"""
    async with PhpBB(host) as phpbb:
        await phpbb.login(sender_name, sender_password)
        rank = await phpbb.get_member_rank(receiver_name)
        assert rank == "Modérateur"


@pytest.mark.asyncio
async def test_fetch_info():
    """Fetch rank"""
    async with PhpBB(host) as phpbb:
        await phpbb.login(sender_name, sender_password)
        uid, rank = await phpbb.get_member_infos(receiver_name)
        assert rank == "Modérateur"
        assert uid == 43533

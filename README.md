![Python package](https://github.com/Sergeileduc/pyphpbb-sl/workflows/Python%20package/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/pyphpbb-sl/badge/?version=latest)](https://pyphpbb-sl.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/Sergeileduc/pyphpbb-sl/branch/master/graph/badge.svg)](https://codecov.io/gh/Sergeileduc/pyphpbb-sl)

# pyphpbb-sl

Interact with phpbb forums.


* Free software: MIT license
* Documentation: https://pyphpbb-sl.readthedocs.io/

## Installation
```shell
pip install git+https://github.com/Sergeileduc/pyphpbb-sl.git
```

or put this line in your `requirements.txt`

`git+https://github.com/Sergeileduc/pyphpbb-sl.git`

To install specific version (git tag), use the following syntax with `@`:

`pip install git+https://github.com/Sergeileduc/pyphpbb-sl.git@v0.11.0`

### Features
* Log-in
* Send Private-Messages
* Read Private-Messages
* Delete Private-Messages
* Fetch forum birthdays

### Usage

#### To send *Private Message* :

```python
import asyncio
import logging
from pyphpbb_sl import PhpBB

# Credentials
host = "http://myforum.fr/"
username = "Username"
password = "Pass1234"

# Message
receiver = "ReceiverPseudo"
subject = "Sent from Python"
message = "Message sent from Python.\nSee yah !"

async def main():
    # Here is the code :
    phpbb = PhpBB(host)
    await phpbb.login(username, password)
    await phpbb.send_private_message(receiver=receiver,
                                     subject=subject,
                                     message=message)

    await phpbb.logout()
    await phpbb.close()

# Run sample
asyncio.run(main())
```

You can also use a context manager with the keyword `with`(automatic logout and close)

```python
import asyncio
import logging
from pyphpbb_sl import PhpBB

logging.basicConfig(level=logging.INFO)

# Credentials
host = "http://myforum.fr/"
username = "Username"
password = "Pass1234"

# Message
receiver = "ReceiverPseudo"
subject = "Sent from Python"
message = "Message sent from Python.\nSee yah !"

# With context manager
async def main():
    async with PhpBB(host) as phpbb:
        await phpbb.login(username, password)
        await phpbb.send_private_message(receiver=receiver,
                                         subject=subject,
                                         message=message)

# Run sample
asyncio.run(main())
```

#### To read *Private Message* :
```python
import asyncio
import logging
from pyphpbb_sl import PhpBB

logging.basicConfig(level=logging.INFO)

host = "http://myforum.fr/"
username = "Username"
password = "Pass1234"


# Context Manager code
async def main():
    async with PhpBB(host) as phpbb:
        await phpbb.login(username, password)
        unread_mess_list = await phpbb.fetch_unread_messages()
        print("Here are your unread messages :")
        print(*unread_mess_list, sep='\n')

        print("\nHere are the contents of messages (messages have been marked as read) :")
        for unread_mess in unread_mess_list:
            message = await phpbb.read_private_message(unread_mess)
            print(message)

asyncio.run(main())
```

Ouput :

```shell
Here are your unread messages :
{'subject': 'Sent by python. Number 2', 'url': './ucp.php?i=pm&mode=view&f=0&p=11822', 'fromto': 'Foo', 'unread': True, 'content': None}
{'subject': 'Sent by python. Number 1', 'url': './ucp.php?i=pm&mode=view&f=0&p=11821', 'fromto': 'Bar', 'unread': True, 'content': None}

Here are the contents of messages (messages have been marked as read
{'subject': 'Sent by python. Number 2', 'url': './ucp.php?i=pm&mode=view&f=0&p=11822', 'fromto': 'Foo', 'unread': False, 'content': 'This message was sent by python. Number 2'}
{'subject': 'Sent by python. Number 1', 'url': './ucp.php?i=pm&mode=view&f=0&p=11821', 'fromto': 'Bar', 'unread': False, 'content': 'This message was sent by python. Number 1'}
```

#### To read *PM* from expected user:
```python
import asyncio
import logging
from pyphpbb_sl import PhpBB

logging.basicConfig(level=logging.INFO)

host = "http://myforum.fr/"
username = "Username"
password = "Pass1234"

expect_message_from_username = "OtherName"


# Context Manager code
async def main():
    async with PhpBB(host) as phpbb:
        await phpbb.login(username_server, password_server)
        await phpbb.fetch_unread_messages()
        message_to_read = phpbb.find_expected_message_by_user(expect_message_from_username)
        if message_to_read:
            message = await phpbb.read_private_message(message_to_read)
            print(message)


asyncio.run(main())
```

#### To validate a token :

In next code, we will :
- generate a token
- *not in code* : give the token to your user (by Discord, mail, etc...)
- fetch our inbox every 30 seconds in a loop (with 5 minutes timeout)
- read message from our expected user
- compare token and message content to validate or not

```python
import asyncio
import logging
from secrets import token_hex
import time
from pyphpbb_sl import PhpBB

logging.basicConfig(level=logging.INFO)

host = "http://myforum.fr/"
username = "Username"
password = "Pass1234"

expect_message_from_username = "OtherName"

token = token_hex(16)

# Here we pretend that we give the token to our user {OtherName}, by mail, discord, etc...

async def try_to_verify(username):
    """Fetch unread mail and try to read PM from OtherName.

    Compare PM content to token.
    """
    # Connect to phpbb forum and fetch unread PM
    async with PhpBB(host) as phpbb:
        await phpbb.login(username_server, password_server)
        await phpbb.fetch_unread_messages()
        # Read message from expected user
        message_to_read = phpbb.find_expected_message_by_user(expect_message_from_username)
        if message_to_read:
            message = await phpbb.read_private_message(message_to_read)
            if message['content'] == token:
                print("Valid token ! GOOD")
                return True
            else:
                print("Invalid token ! BAD !")
                return False
        return False


async def main():
    """Main loop : lauch try_to_verify() every 30 seconds, with a 5 minutes timeout."""
    print(f"Please send me the token :\n{token}")
    timeout = time.time() + 5 * 60   # 5 minutes from now
    while True:
        await asyncio.sleep(30)  # will fetch PM every 30 seconds
        if time.time() > timeout:
            break
        valid = await try_to_verify(expect_message_from_username)
        if valid:
            # do_stuff()
            break


asyncio.run(main())
```

#### Fetch forum members birthdays

```python
import asyncio
import logging
from pyphpbb_sl import PhpBB

# Credentials
host = "http://myforum.fr/"
username = "Username"
password = "Pass1234"


async def main():
    async with PhpBB(host) as phpbb:
        await phpbb.login(username, password)
        out = await phpbb.get_birthdays()
        print(*out, sep='\n')


asyncio.run(main())
```

Output :
```shell
{'name': 'Foo', 'age': 45}
{'name': 'Bar', 'age': 27}
{'name': 'FooBar', 'age': 22}
```

#### Fetch rank of a member

```python
import asyncio
import logging
from pyphpbb_sl import PhpBB

# Credentials
host = "http://myforum.fr/"
username = "Username"
password = "Pass1234"

member_name = "Foobar"


async def main():
    async with PhpBB(host) as phpbb:
        await phpbb.login(username, password)
        rank = await phpbb.get_member_rank(member_name)
        print(rank)


asyncio.run(main())
```

## Fetch infos (uid and rank) of a member

```python
import asyncio
import logging
from pyphpbb_sl import PhpBB

# Credentials
host = "http://myforum.fr/"
username = "Username"
password = "Pass1234"

member_name = "Foobar"


async def main():
    async with PhpBB(host) as phpbb:
        uid, rank = await phpbb.get_member_infos(querry_user)
        print(uid)
        print(rank)

asyncio.run(main())
```

### Credits

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

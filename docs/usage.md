#  Usage

To use pyphpbb-sl in a project::

To send *Private Message* :

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
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

You can also use a context manager with the keyword `async with`(automatic logout and close)

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
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```
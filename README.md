[![Documentation Status](https://readthedocs.org/projects/pyphpbb-sl/badge/?version=latest)](https://pyphpbb-sl.readthedocs.io/en/latest/?badge=latest)

# pyphpbb-sl

Interract with phpbb forums.


* Free software: MIT license
* Documentation: https://pyphpbb-sl.readthedocs.io/

## Installation
```shell
pip install git+https://github.com/Sergeileduc/pyphpbb-sl.git
```

or put this line in your `requirements.txt`

`git+https://github.com/Sergeileduc/pyphpbb-sl.git`

To install specific version (git tag), use the following syntax with `@`:

`pip install git+https://github.com/Sergeileduc/pyphpbb-sl.git@v0.3.1`

### Features
* Log-in
* Send Private-Messages

### Usage
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
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

### Credits

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

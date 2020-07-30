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
`pip install git+https://github.com/Sergeileduc/pyphpbb-sl.git@v0.2.1`

### Features
* Log-in
* Send Private-Messages

### Usage
To send *Private Message* :

```python
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

# Log in, Send, Logout
phpbb = PhpBB(host)
phpbb.login(username, password)

phpbb.send_private_message(receiver=receiver,
                           subject=subject,
                           message=message)

phpbb.logout()
phpbb.close()
```

You can also use a context manager with the keyword `with`(automatic logout and close)

```python
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

# Context Manager
with PhpBB(host) as phpbb:
    phpbb.login(username, password)
    phpbb.send_private_message(receiver=receiver,
                               subject=subject,
                               message=message)
```

### Credits

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

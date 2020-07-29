[![Documentation Status](https://readthedocs.org/projects/pyphpbb-sl/badge/?version=latest)](https://pyphpbb-sl.readthedocs.io/en/latest/?badge=latest)

# pyphpbb-sl

Interract with phpbb forums.


* Free software: MIT license
* Documentation: 

## Installation
```shell
pip install git+https://github.com/Sergeileduc/pyphpbb-sl.git
```

or put this line in your `requirements.txt`
`git+https://github.com/Sergeileduc/pyphpbb-sl.git`

### Usage

```python
from pyphpbb_sl import PhpBB


host = "http://myforum.fr/"
username = "Username"
password = "Pass1234"

phpbb = PhpBB(host)
phpbb.login(username, password)

receiver = "ReceiverPseudo"
subject = "Sent from Python"
message = "Message sent from Python.\nSee yah !"

phpbb.send_private_message(receiver=receiver,
                           subject=subject,
                           message=message)

phpbb.logout()
phpbb.close()
```

### Credits

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

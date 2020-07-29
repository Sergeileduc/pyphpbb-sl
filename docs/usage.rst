#  Usage

To use pyphpbb-sl in a project::

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

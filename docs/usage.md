#  Usage

To use pyphpbb-sl in a project::

To send *Private Message* :

```python
from pyphpbb_sl import PhpBB

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

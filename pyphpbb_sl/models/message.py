from dataclasses import dataclass
from typing import Optional


@dataclass
class Message:
    id: int
    subject: str
    url: str
    sender: str
    receiver: Optional[str]
    content: Optional[str]
    unread: bool

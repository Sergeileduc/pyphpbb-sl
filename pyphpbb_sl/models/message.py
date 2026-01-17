from dataclasses import dataclass


@dataclass
class Message:
    id: int
    subject: str
    url: str
    sender: str
    receiver: str | None
    content: str | None
    unread: bool

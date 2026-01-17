from selectolax.parser import HTMLParser

from pyphpbb_sl.models import SubForum


def parse_sub_forums(root: HTMLParser) -> list[SubForum]:
    nodes = root.css("a.forumtitle")
    return [
        SubForum(
            name=n.text().strip(),
            url=n.attributes.get("href") or "",
        )
        for n in nodes
    ]

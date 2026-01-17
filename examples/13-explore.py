#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""Docstring."""

import asyncio
import logging
import os
import re
from string import ascii_uppercase
from urllib.parse import urljoin

import httpx
from dotenv import load_dotenv
from selectolax.parser import HTMLParser, Node

from pyphpbb_sl import PhpBB

logging.basicConfig(level=logging.INFO)

# Parse a .env file and then load all the variables found as environment variables.  # noqa: E501
load_dotenv()

host: str = os.getenv("HOST") or ""

username: str = os.getenv("RECEIVER_NAME") or ""
password: str = os.getenv("RECEIVER_PASSWORD") or ""

logging.debug("host %s", host)
logging.debug("username %s", username)
logging.debug("password %s", password)


def get_sub_forums(html):
    sub_forums = html.css("a.forumtitle")
    return [
        {"name": s.text().strip(), "url": s.attributes.get("href", "")}
        for s in sub_forums
    ]


def get_nb_topics(html: HTMLParser):
    """Get number of topics in sub-forum."""
    try:
        node: Node | None = html.css_first("div.pagination")
        raw: str = node.text() if node else ""

        n = re.search(r"(?P<nb_topics>\d+?) sujet(s)?", raw)["nb_topics"]
        return int(n)
    except (AttributeError, TypeError):
        return 0


def get_topics(html):
    topics = html.css("a.topictitle")
    return [
        {"name": t.text().strip(), "url": t.attributes.get("href", "")} for t in topics
    ]


async def get_all_topics(phpbb, html, url):
    # First iteration, we allready have the html from the while loop
    n = get_nb_topics(html)
    topics = get_topics(html)
    n -= 40
    start = 40
    while n > 0:
        params = {"start": start}
        try:
            html = await phpbb.browser.get_html(url, params=params)
        except httpx.TransportError:
            continue
        new_topics = get_topics(html)
        topics += new_topics
        n -= 40
        start += 40
    return topics


def print_res_numbers(res_list, start_index=0):
    if res_list:
        for i, res in enumerate(res_list, start_index):
            # print(i, res['name'], res['url'])
            print(f"{i:.<5d}{res['name']:.<20s}{res['url']}")


def print_res_letters(res_list, start_index=0):
    if res_list:
        for i, res in enumerate(res_list, start_index):
            # print(i, res['name'], res['url'])
            print(f"{ascii_uppercase[i]:.<5s}{res['name']:.<20s}{res['url']}")


# Context Manager code
async def main():
    phpbb = PhpBB(host)
    is_looged = await phpbb.login(username, password)
    print(is_looged)
    next_url = "viewforum.php?f=11"
    topics_page = 0
    nb_topics = 0
    while True:  # Infinite loop for user inputs
        print("===========New loop===================")
        url = urljoin(host, next_url)
        print(url)
        try:
            html = await phpbb.browser.get_html(url)
        except httpx.TransportError:
            continue
        sub_forums = get_sub_forums(html)
        active_topics_flag = (
            node := html.css_first("#active_topics")
        ) and "Sujets actifs" in node.text()
        topics = await get_all_topics(phpbb, html, url)
        nb_topics = get_nb_topics(html)
        print("*****Forums**************")
        print_res_letters(sub_forums)
        if not active_topics_flag:
            print(f"*****{nb_topics} Topics**************")
            print_res_numbers(
                topics[topics_page * 10 : (topics_page + 1) * 10],
                1,  # noqa: E203,E226
            )

        if nb_topics > 10:
            choice = input(
                "Entrez un choix :\n"
                "- une lettre/un nombre pour naviguer\n"
                "- 'ù' pour remonter dans le dossier précédent\n"
                "- '!' pour la prochaine page de topics (10 suivants)\n"
                "- ':' pour la page précédente de topics (10 d'avant)\n"
                "- 'exit' pour sortir.\n"
            )
        else:
            choice = input(
                "Entrez un choix :\n"
                "- un nombre pour naviguer dans un dossier\n"
                "- 'u' pour remonter dans le dossier précédent\n"
                "- 'exit' pour sortir.\n"
            )

        if choice == "exit":
            break

        while choice in ["!", ":"]:
            print(f"choice : {choice}")
            print(f"topics_page : {topics_page}")
            print(f"pages limit : {nb_topics // 10}")
            if choice == "!" and topics_page < nb_topics // 10:
                topics_page += 1
            if choice == ":" and topics_page > 0:
                topics_page -= 1
            print_res_numbers(
                topics[topics_page * 10 : (topics_page + 1) * 10],
                1,  # noqa: E203,E226
            )
            choice = input(
                "Entrez un choix :\n"
                "- une lettre/un nombre pour naviguer\n"
                "- 'ù' pour remonter dans le dossier précédent\n"
                "- '!' pour la prochaine page de topics (10 suivants)\n"
                "- ':' pour la page précédente de topics (10 d'avant)\n"
                "- 'exit' pour sortir.\n"
            )

        if choice.isdigit():
            choice = int(choice)
            print("OK, here you are :")
            t = topics[topics_page * 10 + choice - 1]  # noqa: E226
            url = urljoin(host, t["url"])
            print(f"{t['name']}\t{url}")
            break

        next_url = sub_forums[ascii_uppercase.index(choice.upper())].get("url")
        print(next_url)

    await phpbb.logout()
    await phpbb.close()


asyncio.run(main())

#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""Docstring."""

import aiohttp
import asyncio
import logging
import os
from string import ascii_uppercase
import re
from urllib.parse import urljoin

from dotenv import load_dotenv

from pyphpbb_sl import PhpBB

logging.basicConfig(level=logging.INFO)

# Parse a .env file and then load all the variables found as environment variables.  # noqa: E501
load_dotenv()

host = os.getenv("HOST")

username = os.getenv("RECEIVER_NAME")
password = os.getenv("RECEIVER_PASSWORD")

logging.debug("host %s", host)
logging.debug("username %s", username)
logging.debug("password %s", password)


def get_sub_forums(html):
    sub_forums = html.select("a.forumtitle")
    if sub_forums:
        return [{'name': s.text, 'url': s['href']} for s in sub_forums]
    return []


def get_nb_topics(html):
    """Get number of topics in sub-forum."""
    try:
        raw = html.select('div.pagination')[0].text
        n = re.search(r"(?P<nb_topics>\d+?) sujet(s)?", raw).group('nb_topics')
        return int(n)
    except AttributeError:
        return 0


def get_topics(html):
    topics = html.select("a.topictitle")
    if topics:
        return [{'name': t.text, 'url': t['href']} for t in topics]
    return []


async def get_all_topics(phpbb, html, url):
    # First iteration, we allready have the html from the while loop
    n = get_nb_topics(html)
    topics = get_topics(html)
    n -= 40
    start = 40
    while n > 0:
        params = {'start': start}
        try:
            html = await phpbb.browser.get_html(url, params=params)
        except aiohttp.client_exceptions.ServerDisconnectedError:
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
        except aiohttp.client_exceptions.ServerDisconnectedError:
            continue
        sub_forums = get_sub_forums(html)
        active_topics_flag = html.find(id="active_topics", string="Sujets actifs")
        topics = await get_all_topics(phpbb, html, url)
        nb_topics = get_nb_topics(html)
        print("*****Forums**************")
        print_res_letters(sub_forums)
        if not active_topics_flag:
            print(f"*****{nb_topics} Topics**************")
            print_res_numbers(topics[topics_page*10:(topics_page+1)*10], 1)  # noqa: E226, E501

        if nb_topics > 10:
            choice = input("Entrez un choix :\n"
                           "- une lettre/un nombre pour naviguer\n"
                           "- 'ù' pour remonter dans le dossier précédent\n"
                           "- '!' pour la prochaine page de topics (10 suivants)\n"
                           "- ':' pour la page précédente de topics (10 d'avant)\n"
                           "- 'exit' pour sortir.\n")
        else:
            choice = input("Entrez un choix :\n"
                           "- un nombre pour naviguer dans un dossier\n"
                           "- 'u' pour remonter dans le dossier précédent\n"
                           "- 'exit' pour sortir.\n")

        if choice == "exit":
            break

        while choice in ['!', ':']:
            print(f"choice : {choice}")
            print(f"topics_page : {topics_page}")
            print(f"pages limit : {nb_topics // 10}")
            if choice == '!' and topics_page < nb_topics // 10:
                topics_page += 1
            if choice == ':' and topics_page > 0:
                topics_page -= 1
            print_res_numbers(topics[topics_page*10:(topics_page+1)*10], 1)  # noqa: E226, E501
            choice = input("Entrez un choix :\n"
                           "- une lettre/un nombre pour naviguer\n"
                           "- 'ù' pour remonter dans le dossier précédent\n"
                           "- '!' pour la prochaine page de topics (10 suivants)\n"
                           "- ':' pour la page précédente de topics (10 d'avant)\n"
                           "- 'exit' pour sortir.\n")

        if choice.isdigit():
            choice = int(choice)
            print("OK, here you are :")
            t = topics[topics_page*10 + choice-1]  # noqa: E226
            url = urljoin(host, t['url'])
            print(f"{t['name']}\t{url}")
            break

        next_url = sub_forums[ascii_uppercase.index(choice.upper())].get('url')
        print(next_url)

    await phpbb.logout()
    await phpbb.close()

asyncio.run(main())

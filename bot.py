#!/usr/bin/env python

import re
import time
import miniirc
import urltitle
from urllib.parse import urlparse
from typing import Optional, NoReturn, Tuple, List

import conf


class URLTitleReader:
    def __init__(self) -> None:
        self._url_title_reader = urltitle.URLTitleReader(verify_ssl=True)

    def title(self, url: str) -> Optional[str]:
        try:
            title = self._url_title_reader.title(url)
        except Exception as exc:
            print("Failed to read title. %s", exc)
            return False
        return title


class Bot:
    def __init__(self) -> None:
        self._irc = miniirc.IRC(
            ssl           = conf.SSL,
            ip            = conf.SERVER,
            port          = conf.PORT,
            nick          = conf.NICK,
            ident         = conf.IDENT,
            realname      = conf.REALNAME,
            channels      = conf.CHANNELS,
            quit_message  = conf.QUIT_MSG,
            ns_identity   = (conf.NICK, conf.PASSWORD),
        )

        while True:
            time.sleep(123457)


@miniirc.Handler("PRIVMSG", colon=False)
def _handle_privmsg(irc: miniirc.IRC, hostmask: Tuple[str, str, str], args: List[str]) -> None:
    #print("Handling incoming message: hostmask=%s, args=%s", hostmask, args)
    # Ignore ourself
    if hostmask[0] == conf.NICK:
        return

    # Watch only for channel messages
    if args[0] in conf.CHANNELS:
        urls = _find_urls(args[1])
        # Walk URLs (if any)
        for url in urls:
            if stack_push(url) and domain_validate(url):
                title = _get_title(irc, args[0], url)
                if title:
                    msg = f"{conf.TITLE_PREFIX} {title[1]}"
                    irc.msg(args[0], msg)
            else:
                print("Skipping URL: %s" % url)
    return


def _get_title(irc: miniirc.IRC, channel: str, url: str) -> Optional[Tuple[str, str, str]]:
    url_title_reader = URLTitleReader()

    try:
        title = url_title_reader.title(url)
    except Exception as exc:
        print(f"Error retrieving title for URL in message in {channel}: {exc}")
    else:
        if title:
            print('Returning title "%s" for URL %s in message in %s.' % (title, url, channel))
            return url, title

    return None


def _find_urls(msg):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, msg)
    return [x[0] for x in url]


def stack_push(url):
    if url in conf.url_cache:
        return False
    # Add URL to stack
    conf.url_cache.append(url)
    conf.url_cache = conf.url_cache[:10]
    return True


def domain_validate(url):
    try:
        domain = urlparse(url).netloc
    except:
        return False

    if not domain in conf.DOMAIN_BACKLIST:
        return True

    return False

# 0xFF we go
print("Starting...")
conf.url_cache = []
b=Bot()
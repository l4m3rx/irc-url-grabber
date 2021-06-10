#!/usr/bin/env python

import re
import miniirc
import requests
from time import sleep
from typing import Tuple, List
from urllib.parse import urlparse
from urltitle import URLTitleReader as url_reader

import conf


class URLTitleReader:
    def __init__(self):
        self._url_title_reader = url_reader(verify_ssl=True)

    def title(self, url: str):
        try:
            title = self._url_title_reader.title(url)
        except Exception as exc:
            print(f"Failed to read title. {exc}")
            return False
        return title


class Bot:
    def __init__(self):
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
        conf.instance = self._irc

        while True:
            sleep(123457)


@miniirc.Handler("PRIVMSG", colon=False)
def _handle_privmsg(irc: miniirc.IRC, hostmask: Tuple[str, str, str], args: List[str]):

    # Handling incoming message: hostmask=%s, args=%s ('nick', '~ident', 'host.com') ['#channel', 'message']
    if conf.DEBUG:
        print("Handling incoming message: hostmask=%s, args=%s", hostmask, args)

    # Ignore ourself
    if (hostmask[0] == conf.NICK) or (hostmask[0] in conf.IGNORE_NICKS):
        return

    # Watch only for channel messages
    if args[0] in conf.CHANNELS:
        urls = find_urls(args[1])
        # Walk URLs (if any)
        for url in urls:
            if stack_push(url) and validate(url):
                title = get_title(irc, args[0], url)
                if title:
                    msg = f"{conf.TITLE_PREFIX} {title[1]}"
                    irc.msg(args[0], msg)
            else:
                print(f"Skipping URL: {url}")
        # Crypto prices
        try:
            if args[1].startswith('.price '):
                _msg = args[1].split()
                if (len(_msg) == 2) and (_msg[1].upper() in conf.CRYPTOS):
                    irc.msg(args[0], coin_price(_msg[1]))
        except:
            pass  # too lazy to handle it properly

    return


def get_title(irc: miniirc.IRC, channel: str, url: str):

    url_title_reader = URLTitleReader()

    try:
        title = url_title_reader.title(url)
    except Exception as exc:
        print(f"Error retrieving title for URL in message in {channel}: {exc}")
    else:
        if title:
            return url, title

    return None


def find_urls(msg: str):
    url = re.findall(conf.URL_REGEX, msg)
    return [x[0] for x in url]


def stack_push(url: str):
    if url in conf.url_cache:
        return False
    # Add URL to stack
    conf.url_cache.append(url)
    conf.url_cache = conf.url_cache[:conf.URL_STACK_SIZE]
    return True


def validate(url: str):
    try:
        domain = urlparse(url).netloc
    except:
        return False

    if not domain in conf.DOMAIN_BACKLIST:
        return True

    return False


def coin_price(coin: str):
    try:
        response = requests.get("https://poloniex.com/public?command=returnTicker").json()
    except:
        print("Error while trying to fetch data from poloniex.")
        return False

    pair_name = 'USDT_' + coin.upper()
    if pair_name in response.keys():
        last_price = str( round( float( response[pair_name]['last'] ), 2) )
        price_message = f"[{coin.upper()}] Current price: ${last_price}"
        return price_message

    return False



# 0xFF we go
conf.url_cache = []
conf.instance = None

print("Starting...")
b=Bot()
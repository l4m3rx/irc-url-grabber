#!/usr/bin/env python

import re
import miniirc
import requests
import contextlib
from time import sleep
from typing import Tuple, List
from urllib.request import urlopen
from urllib.parse import urlparse, urlencode
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
            debug         = conf.DEBUG,
            realname      = conf.REALNAME,
            channels      = conf.CHANNELS,
            quit_message  = conf.QUIT_MSG,
            ns_identity   = (conf.NICK, conf.PASSWORD),
        )
        conf.instance = self._irc

        while True:
            sleep(123457)


def _is_main_bot(hostm: str, join: bool):
    if hostm.lower() == conf.MAIN_BOT.lower():
        if join:
            conf.active_bot = True
        else:
            conf.active_bot = False


@miniirc.Handler('353', colon=False)
def _handle_353(irc: miniirc.IRC, hostmask: Tuple[str, str, str], args: List[str]):
    if conf.MAIN_BOT.lower() in args[-1].lower().split():
        conf.active_bot = True
    else:
        conf.active_bot = False


@miniirc.Handler('NICK', colon=False)
def _handle_nickchange(irc: miniirc.IRC, hostmask: Tuple[str, str, str], args: List[str]):
    pass


@miniirc.Handler('JOIN', colon=False)
def _handle_join(irc: miniirc.IRC, hostmask: Tuple[str, str, str], args: List[str]):
    _is_main_bot(hostmask[0], join=True)


@miniirc.Handler('PART', 'QUIT', 'KICK', colon=False)
def _handle_quit(irc: miniirc.IRC, hostmask: Tuple[str, str, str], args: List[str]):
    _is_main_bot(hostmask[0], join=False)


@miniirc.Handler("PRIVMSG", colon=False)
def _handle_privmsg(irc: miniirc.IRC, hostmask: Tuple[str, str, str], args: List[str]):

    # Ignore ourself and some other ppl :)
    if (hostmask[0] == conf.NICK) or (hostmask[0] in conf.IGNORE_NICKS):
        return

    # Watch only for channel messages
    if args[0] in conf.CHANNELS:
        if args[0] in conf.URL_CHANNELS:
            urls = find_urls(args[1])
            # Walk URLs (if any)
            for url in urls:
                if stack_push(url) and validate(url):
                    title = get_title(irc, args[0], url)
                    if title:
                        msg = f"{conf.TITLE_PREFIX} {title[1]}"
                        if not conf.active_bot:
                            irc.msg(args[0], msg)
                else:
                    print(f"Skipping URL: {url}")
        # Crypto prices
        try:
            if args[1].startswith('.price '):
                _msg = args[1].split()
                if (len(_msg) == 2) and (_msg[1].upper() in conf.CRYPTOS):
                    irc.msg(args[0], ncoin_price(_msg[1]))
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


def round_it(price: float):
    if (price < 1):
        price = round(price, 4)
    elif (price >= 1) and (price < 10):
        price = round(price, 2)
    else:
        price = round(price, 0)
    return price


def ncoin_price(coin: str):
    try:
        price_usd = round_it(requests.get(f"https://rate.sx/1{coin}").json())
        price_eur = round_it(requests.get(f"https://eur.rate.sx/1{coin}").json())
    except:
        print("Error while trying to fetch data from rate.sx")
        return False

    return f"[{coin.upper()}] Price: ${price_usd} / €{price_eur}"


def shorten_url(url: str):
    request_url = ('http://tinyurl.com/api-create.php?' + urlencode({'url':url}))
    try:
        with contextlib.closing(urlopen(request_url)) as response:
            return response.read().decode('utf-8')
    except:
        return url


# 0xFF we go
conf.instance = None
conf.url_cache = []
conf.active_bot = True

print("Starting...")
b=Bot()
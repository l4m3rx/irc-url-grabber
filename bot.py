#!/usr/bin/env python

import re
import miniirc
import requests
import feedparser
import contextlib
from time import sleep, localtime, time
from dateutil import parser
from threading import Thread
from typing import Tuple, List
from urllib.request import urlopen
from urllib.parse import urlparse, urlencode
from urltitle import URLTitleReader as url_reader

import conf


def shorten_url(url: str):
    request_url = ('http://tinyurl.com/api-create.php?' + urlencode({'url':url}))
    try:
        with contextlib.closing(urlopen(request_url)) as response:
            return response.read().decode('utf-8')
    except:
        return url


def xml_feed(rss_url: str):
    result = []
    try:
        rss_feed = feedparser.parse(rss_url)
        for entry in rss_feed.entries:
            now = time() 
            entry_date = parser.parse(entry.updated).timestamp()

            fresh = (now - entry_date) < (conf.RSS_REFRESH * 60)
            if fresh:
                result.append([entry.title, entry.link])

            if conf.DEBUG:
                print(f"RSS {fresh} N:{now} | E:{entry_date}")

    except:
        print(f"Error while handleing {rss_url}")
        return result
    else:
        return result


def rss_thread():
    while True:
        if not conf.instance:
            sleep(30)
        
        if conf.DEBUG:
            print("RSS check starting...")

        _sleeptill = time() + (conf.RSS_REFRESH * 60)

        for rss_name in conf.RSS_FEEDS:

            if conf.DEBUG:
                print("RSS Feed: %s" % rss_name)

            for rrs_entry in xml_feed(conf.RSS_FEEDS[rss_name]):
                msg = f"[{rss_name}] {rrs_entry[0]} --- {shorten_url(rrs_entry[1])}"
                try:
                    for chan in conf.RSS_CHANNELS:
                        conf.instance.msg(chan, msg)
                        sleep(2)
                except:
                    print("Error while sending RSS feed.")

        sleep(_sleeptill - time())


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


# 0xFF we go
conf.url_cache = []
conf.instance = None

print("Starting...")
Thread(target = rss_thread).start()
b=Bot()
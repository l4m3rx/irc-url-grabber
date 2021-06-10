# Server
SSL    = True
SERVER = 'irc.libera.chat'
PORT   = 6697
# Bot
NICK     = 'botnick'
CHANNELS = ['#randombotchan']
PASSWORD = 'botpass'
IDENT    = 'roBot'
REALNAME = 'Testis'
QUIT_MSG = 'I quit!'
# URL Grabber
TITLE_TIMEOUT   = 15
URL_STACK_SIZE  = 10
TITLE_PREFIX    = ">>"
URL_REGEX       = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
IGNORE_NICKS    = ["lambot"]
DOMAIN_BACKLIST = [
    "127.0.0.1",
    "localhost",
    "ip6-loopback",
    "ip6-allnodes",
    "ip6-localhost",
    "ip6-allrouters",
]
# RSS Feed
RSS_CHANNELS = ['#randombotchan']
RSS_FEEDS    = {
    'Hackaday': 'https://hackaday.com/blog/feed/',
    'Phoronix': 'https://www.phoronix.com/rss.php',
    'Slashdot': 'http://rss.slashdot.org/Slashdot/slashdotMain',
}
RSS_REFRESH  = 10
# Other
CRYPTOS = ['BTC', 'ETH', 'XMR', 'DOGE', 'LINK', 'BNB', 'ADA', 'DOT']
DEBUG   = True

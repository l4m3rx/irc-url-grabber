import ircstyle

# Server
SSL    = True
SERVER = 'irc.libera.chat'
PORT   = 6697
# Bot
NICK     = 'botnick'
CHANNELS = ['#botchannel']
PASSWORD = 'botpass'
IDENT    = 'roBot'
REALNAME = 'Testis'
QUIT_MSG = 'I quit!'
# URL Grabber
TITLE_TIMEOUT   = 15
TITLE_PREFIX    = ircstyle.style("»", fg="green", reset=True) # ⤷
DOMAIN_BACKLIST = [
    "domoticz",
    "127.0.0.1",
    "localhost",
    "ip6-loopback",
    "ip6-allnodes",
    "ip6-localhost",
    "ip6-allrouters",
]

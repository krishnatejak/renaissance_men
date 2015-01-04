from tornado.web import Application

from search.handlers import *
import config


search_application = Application(
    [
        ('/search/', SearchHandler),
        ('/search/(?P<s>[\w]*)/', SearchHandler)
    ],
    cookie_secret=config.COOKIE_SECRET,
    debug=config.DEBUG
)
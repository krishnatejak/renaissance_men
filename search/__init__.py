from tornado.web import Application

from search.handlers import *
import config


search_application = Application(
    [
        ('/search/', SearchHandler),
        ('/search/(?P<s>[\w]*)/', SearchHandler)
    ],
    debug=config.DEBUG
)
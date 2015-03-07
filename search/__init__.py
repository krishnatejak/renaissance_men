from tornado.web import Application

from search.handlers import *
import config

search_application = Application(
    [
        ('/api/search/?', SearchHandler),
        ('/api/search/(?P<s>[\w]*)/', SearchHandler),
        ('/api/search/slots/service/(?P<service>[\w]+)/', SlotHandler),
        ('/api/search/slots/block/(?P<service>[\w]+)/', SlotHandler)
    ],
    cookie_secret=config.COOKIE_SECRET,
    debug=config.DEBUG
)
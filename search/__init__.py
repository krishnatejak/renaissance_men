from tornado.web import Application

from search.handlers import *
import config

search_application = Application(
    [
        ('/api/search/?', SearchHandler),
        ('/api/search/(?P<s>[\w]*)/', SearchHandler),
        ('/api/slots/(?P<service>[\w]+)/?', SearchHandler)
    ],
    cookie_secret=config.COOKIE_SECRET,
    debug=config.DEBUG
)
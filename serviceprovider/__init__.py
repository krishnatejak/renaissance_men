from tornado.web import Application

from serviceprovider.handlers import *
import config
import db


service_provider = Application([
    (r'/service_providers/?', ServiceProviderHandler)
], debug=config.DEBUG)

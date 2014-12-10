from tornado.web import Application

from serviceprovider.handlers import *
import config
import db


service_provider = Application([
    (r'/serviceproviders/?', ServiceProviderHandler),
    (r'/serviceproviders/([\d-]*)/?', ServiceProvider_id_Handler)
], debug=config.DEBUG)

from tornado.web import Application

from serviceprovider.handlers import *
import config


service_provider = Application([
    (r'/serviceproviders/(P<provider_id>[\d]*)?', ServiceProviderHandler)
], debug=config.DEBUG)

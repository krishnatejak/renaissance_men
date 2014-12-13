from tornado.web import Application

from admin.handlers import *
import config


service_provider = Application([
    (r'/serviceprovider/?', ServiceProviderHandler),
    (r'/serviceprovider/([\d]*)/?', ServiceProviderHandler),
    (r'/serviceprovider/(P<spid>[\d]*)/verify/(P<token>[\d]*)?', ServiceProviderVerifyHandler),
    (r'/service/?', ServiceHandler),
    (r'/job/?', JobHandler),
    (r'/job/(P<jid>[\d]*)/start', JobStartHandler),
    (r'/job/(P<jid>[\d]*)/end', JobStartHandler),
], debug=config.DEBUG)

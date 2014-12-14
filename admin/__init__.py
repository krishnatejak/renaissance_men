from tornado.web import Application

from admin.handlers import *
import config


service_provider = Application([
    (r'/serviceprovider/([\d]+)?/?', ServiceProviderHandler),
    (r'/serviceprovider/([\d]+)/verify/([\d]+)/', ServiceProviderVerifyHandler),
    (r'/service/', ServiceHandler),
    (r'/job/([\d]+)?/?', JobHandler),
    (r'/job/([\d]+)/start/', JobStartHandler),
    (r'/job/([\d]+)/end/', JobStartHandler),
], debug=config.DEBUG)

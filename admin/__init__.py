from tornado.web import Application

from admin.handlers import *
import config


admin_application = Application([
    (r'/serviceprovider/([\d]+)?/?', ServiceProviderHandler),
    (r'/serviceprovider/([\d]+)/verify/([\d]+)/', ServiceProviderVerifyHandler),
    (r'/serviceprovider/([\d]+)/gcm/', ServiceProviderGCMHandler),
    (r'/service/', ServiceHandler),
    (r'/job/([\d]+)?/?', JobHandler),
    (r'/job/([\d]+)/start/', JobStartHandler),
    (r'/job/([\d]+)/end/', JobEndHandler),
    (r'/populate/all/', PopulateHandler),
], debug=config.DEBUG)

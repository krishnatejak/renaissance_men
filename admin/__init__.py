from tornado.web import Application

from admin.handlers import *
import config


admin_application = Application(
    [
        (r'/api/serviceprovider/(?P<id>[\d]+)?/?', ServiceProviderHandler),
        #(r'/api/serviceprovider/([\d]+)/verify/?', ServiceProviderVerifyHandler),
        (r'/api/serviceprovider/([\d]+)/job/?', ServiceProviderJobHandler),
        #(r'/api/serviceprovider/([\d]+)/gcm/?', ServiceProviderGCMHandler),
        #(r'/api/service/?', ServiceHandler),
        (r'/api/job/?', JobHandler),
        (r'/api/job/([\d]+)?/?', JobHandler),
        (r'/api/job/([\d]+)/start/?', JobStartHandler),
        (r'/api/job/([\d]+)/end/?', JobEndHandler),
        (r'/api/job/([\d]+)/accept/?', JobAcceptHandler),
        (r'/api/job/([\d]+)/reject/?', JobRejectHandler),
        (r'/api/populate/all/?', PopulateHandler),
        (r'/api/auth/google/?', GoogleAuthHandler),
        (r'/api/order/([\d]+)?/?', OrderHandler),
        (r'/api/order/([\d]+)/serviceprovider/', OrderHandler),
        (r'/api/order/([\w]+)/', OrderStatusHandler),
        (r'/api/user/([\d]+)/verify/', UserVerifyHandler),
        (r'/api/user/([\d]+)?/?', UserHandler),
        (r'/api/signup/?', SignupEmail)
    ],
    google_oauth={
        "key": config.GOOGLE_OAUTH2_CLIENT_ID,
        "secret": config.GOOGLE_OAUTH2_CLIENT_SECRET,
    },
    cookie_secret=config.COOKIE_SECRET,
    debug=config.DEBUG
)

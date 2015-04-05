from tornado.web import Application

import config
from admin.handlers.auth import *
from admin.handlers.job import *
from admin.handlers.serviceprovider import *
from admin.handlers.order import *
from admin.handlers.user import *
from admin.handlers.common import *
from admin.handlers.signup import *


admin_application = Application(
    [
        (r'/api/serviceprovider/(?P<id>[\d]+)?/?', ServiceProviderHandler),
        # (r'/api/serviceprovider/([\d]+)/verify/?', ServiceProviderVerifyHandler),
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
        (r'/api/order/(?P<id>[\d]+)?/?', OrderHandler),
        (r'/api/missedorder/?', MissedOrderHandler),
        (r'/api/order/([\d]+)/serviceprovider/', OrderHandler),
        (r'/api/order/([\w]+)/', OrderStatusHandler),
        (r'/api/order/([\d]+)/rating/(\d)', OrderRatingHandler),
        (r'/api/user/([\d]+)/verify/', UserVerifyHandler),
        (r'/api/user/?', UserHandler),
        (r'/api/signup/?', SignupHandler),
        (r'/api/close', CloseHandler)
    ],
    google_oauth={
        "key": config.GOOGLE_OAUTH2_CLIENT_ID,
        "device_key": config.GOOGLE_OAUTH2_DEVICE_CLIENT_ID,
        "secret": config.GOOGLE_OAUTH2_CLIENT_SECRET,
    },
    cookie_secret=config.COOKIE_SECRET,
    debug=config.DEBUG
)

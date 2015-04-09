from tornado.web import Application

import config
from admin.handlers.auth import *
from admin.handlers.job import *
from admin.handlers.serviceprovider import *
from admin.handlers.order import *
from admin.handlers.user import *
from admin.handlers.common import *
from admin.handlers.signup import *

"""
API URL Guidelines

1.  API URLs for base resources like user, service provider, service user
    which perform operations (GET, PUT, POST, DELETE) only on base resources
    should not include primary keys as these will be derived from session

    eg. GET /api/serviceprovider
        PUT /api/serviceprovider
        GET /api/user
        PUT /api/user
        GET /api/serviceprovider/orders

2.  Primary key for the resource in URL should always be referred as pk
"""

admin_application = Application(
    [
        (r'/api/serviceprovider', ServiceProviderHandler),
        #(r'/api/serviceprovider/jobs', ServiceProviderJobHandler),
        (r'/api/serviceprovider/orders', ServiceProviderOrdersHandler),
        (r'/api/serviceprovider(?P<pk>/\d+)?/upload', ServiceProviderUploadHandler),
        #(r'/api/job/?', JobHandler),
        #(r'/api/job/([\d]+)?/?', JobHandler),
        #(r'/api/job/([\d]+)/start/?', JobStartHandler),
        #(r'/api/job/([\d]+)/end/?', JobEndHandler),
        #(r'/api/job/([\d]+)/accept/?', JobAcceptHandler),
        #(r'/api/job/([\d]+)/reject/?', JobRejectHandler),
        (r'/api/populate/all/?', PopulateHandler),
        (r'/api/auth/google/?', GoogleAuthHandler),
        (r'/api/order/?(?P<pk>[\d]+)?', OrderHandler),
        (r'/api/order/status/(?P<status>[a-z]+)', SuOrderStatusHandler),
        (r'/api/order/(?P<pk>[\d]+)/rating/(?P<rating>[\d])', OrderRatingHandler),
        (r'/api/missedorder/?', MissedOrderHandler),

        (r'/api/user', UserHandler),
        (r'/api/user/phone/verify', UserVerifyHandler),

        (r'/api/signup/?', SignupHandler),
        (r'/api/close', CloseHandler),

        # admin apis
        (r'/api/admin/serviceprovider/?(?P<pk>\d+)?', AdminServiceProviderHandler),
        (r'/api/admin/order/?(?P<pk>[\d]+)?', AdminOrderHandler),
        (r'/api/admin/order/(?P<pk>[\d]+)/assign', AssignOrderHandler),
        (r'/api/admin/order/(?P<pk>[\d]+)/status/(?P<status>[a-z]+)', UpdateOrderStatusHandler),
    ],
    google_oauth={
        "key": config.GOOGLE_OAUTH2_CLIENT_ID,
        "device_key": config.GOOGLE_OAUTH2_DEVICE_CLIENT_ID,
        "secret": config.GOOGLE_OAUTH2_CLIENT_SECRET,
    },
    cookie_secret=config.COOKIE_SECRET,
    debug=config.DEBUG
)

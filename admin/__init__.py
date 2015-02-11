from tornado.web import Application

from admin.handlers import *
import config

admin_application = Application(
    [
        (r'/api/serviceprovider/([\d]+)?/?', ServiceProviderHandler),
        (r'/api/serviceprovider/([\d]+)/verify/?', ServiceProviderVerifyHandler),
        (r'/api/serviceprovider/([\d]+)/job/?', ServiceProviderJobHandler),
        (r'/api/serviceprovider/([\d]+)/gcm/?', ServiceProviderGCMHandler),
        (r'/api/service/?', ServiceHandler),
        (r'/api/job/?', JobHandler),
        (r'/api/job/([\d]+)?/?', JobHandler),
        (r'/api/job/([\d]+)/start/?', JobStartHandler),
        (r'/api/job/([\d]+)/end/?', JobEndHandler),
        (r'/api/job/([\d]+)/accept/?', JobAcceptHandler),
        (r'/api/job/([\d]+)/reject/?', JobRejectHandler),
        (r'/api/populate/all/?', PopulateHandler),
        (r'/api/serviceprovider/auth/google/?', SpGoogleAuthHandler),
        (r'/api/user/auth/google/?', UserGoogleAuthHandler),
        (r'/api/signup/?', SignupEmail)
    ],
    google_oauth={
        "key": config.GOOGLE_OAUTH2_CLIENT_ID,
        "secret": config.GOOGLE_OAUTH2_CLIENT_SECRET,
    },
    debug=config.DEBUG
)

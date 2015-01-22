from tornado.web import Application

from admin.handlers import *
import config


admin_application = Application(
    [
        (r'/admin/serviceprovider/([\d]+)?/?', ServiceProviderHandler),
        (r'/admin/serviceprovider/([\d]+)/verify/([\d]+)/', ServiceProviderVerifyHandler),
        (r'/admin/serviceprovider/([\d]+)/gcm/', ServiceProviderGCMHandler),
        (r'/admin/service/', ServiceHandler),
        (r'/admin/job/([\d]+)?/?', JobHandler),
        (r'/admin/job/([\d]+)/start/', JobStartHandler),
        (r'/admin/job/([\d]+)/end/', JobEndHandler),
        (r'/admin/populate/all/', PopulateHandler),
        (r'/admin/serviceprovider/auth/google/', SpGoogleAuthHandler),
        (r'/admin/user/auth/google/', UserGoogleAuthHandler),
        (r'/admin/signup/?', SignupEmail)
    ],
    google_oauth={
        "key": config.GOOGLE_OAUTH2_CLIENT_ID,
        "secret": config.GOOGLE_OAUTH2_CLIENT_SECRET,
    },
    debug=config.DEBUG
)

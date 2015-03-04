from tornado.web import Application

from jobs.handlers import *
import config

job_application = Application(
    [
        ('/job/?', JobHandler),
    ],
    cookie_secret=config.COOKIE_SECRET,
    debug=config.DEBUG
)
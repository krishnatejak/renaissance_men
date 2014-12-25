from tornado.web import RequestHandler

import db
from session import Session
import config

__all__ = ['SearchHandler']

class SearchHandler(RequestHandler):
    def initialize(self):
        self.r = db.Redis()
        session = self.session

    @property
    def session(self):
        sessionid = self.get_secure_cookie(config.SESSION_COOKIE_NAME)
        session = Session(sessionid)
        if not sessionid:
            self.set_secure_cookie(
                config.SESSION_COOKIE_NAME,
                session.sessionid,
                expires_days=config.SESSION_EXPIRY
            )
        return session

    def get(self, s=None, sk=None):
        pass
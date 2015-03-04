import json

from tornado.web import RequestHandler

from session import SessionMixin
from exc import handle_exceptions
import db
from search.service.search_service import *

__all__ = ['JobHandler']


class JobHandler(RequestHandler, SessionMixin):
    def initialize(self):
        self.r = db.Redis()

    @handle_exceptions
    def post(self):


        data = search(self.r, service, skill, latitude, longitude, self.session.sessionid)
        self.write(json.dumps(data))
        self.finish()
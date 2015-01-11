import json

from tornado.web import RequestHandler

from session import SessionMixin
from exc import handle_exceptions
import db
from search.service.search_service import *

__all__ = ['SearchHandler']


class SearchHandler(RequestHandler, SessionMixin):
    def initialize(self):
        self.r = db.Redis()

    @handle_exceptions
    def get(self):
        service = self.get_argument("s", None)
        skill = self.get_argument("sk", None)
        if service and not self.r.hget(self.session.sessionid,'search_id:{0}'.format(service)):
            latitude = self.request.headers['latitude']
            longitude = self.request.headers['longitude']
        else:
            latitude = None
            longitude = None
        data = search(self.r, service, skill, latitude, longitude, self.session.sessionid)
        self.write(json.dumps(data))
        self.finish()
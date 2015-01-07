import json

from tornado.web import RequestHandler

from session import SessionMixin
from exc import handle_exceptions
import db
from search.service.search import search

__all__ = ['SearchHandler']


class SearchHandler(RequestHandler, SessionMixin):
    def initialize(self):
        self.r = db.Redis()

    @handle_exceptions
    def get(self):
        service = self.get_argument("s", None)
        skill = self.get_argument("sk", None)
        data = search(self.r, service, skill)
        self.write(json.dumps(data))
        self.finish()
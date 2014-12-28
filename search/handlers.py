import json

from tornado.web import RequestHandler
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from exc import AppException

import db
from session import Session
import config
from search.service.search import search

__all__ = ['SearchHandler']

class SearchHandler(RequestHandler):
    def initialize(self):
        self.r = db.Redis()
        session = self.session

    def handle_exceptions(function):
        def _wrapper(instance, *args, **kwargs):
            try:
                return function(instance, *args, **kwargs)
            except AppException as ae:
                instance.set_status(400)
                instance.write({
                    'error': str(ae)
                })
                instance.flush()
            except (NoResultFound, MultipleResultsFound):
                instance.set_status(400)
                instance.write({
                    'error': 'No results found'
                })
                instance.flush()
            except Exception as e:
                instance.set_status(500)
                instance.write({
                    'error': str(e)
                })
                instance.flush()
        return _wrapper

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

    @handle_exceptions
    def get(self):
        service =  self.get_argument("s",None)
        skill = self.get_argument("sk",None)
        data = search(self.r, service, skill)
        self.write(json.dumps(data))
        self.finish()
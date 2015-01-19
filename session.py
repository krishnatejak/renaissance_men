from uuid import uuid4

import db
import config
from utils import get_json_datetime


class Session(object):
    def __init__(self, sessionid=None):
        self.r = db.session_redis
        self._sessionid = None
        self.sessionid = sessionid


    @property
    def sessionid(self):
        return self._sessionid

    @sessionid.setter
    def sessionid(self, session_id):
        if not session_id:
            self._sessionid = self.prefixed(self.generate_sid())
        else:
            self._sessionid = session_id
        self.__set_last_accessed()

    @staticmethod
    def prefixed(sid):
        return '%s:%s' % (config.SESSION_PREFIX, sid)

    @staticmethod
    def generate_sid():
        return uuid4().get_hex()

    def __set_last_accessed(self):
        exists = False
        if self.r.exists(self.sessionid):
            exists = True
        self.r.hset(self.sessionid, 'last_accessed', get_json_datetime())
        if not exists:
            self.r.expire(
                self.sessionid,
                config.SESSION_EXPIRY * 24 * 60 * 60
            )

    def clear(self):
        self.r.delete(self.sessionid)

    def __getitem__(self, key):
        return self.r.hget(self.sessionid, key)

    def __setitem__(self, key, value):
        self.r.hset(self.sessionid, key, value)

    def __delitem__(self, key):
        self.r.hdel(self.sessionid, key)

    def __len__(self):
        return self.r.hlen(self.sessionid)

    def __contains__(self, key):
        return self.r.hexists(self.sessionid, key)

    def __iter__(self):
        session_data = self.r.hkeys(self.sessionid)
        for key in session_data:
            yield key


class SessionMixin(object):

    @property
    def session(self):
        """session id should be sent as request header"""
        if not hasattr(self, '_session'):
            sessionid = self.request.headers.get(config.SESSION_HEADER)
            session = Session(sessionid)
            if not sessionid:
                self.set_header(config.SESSION_HEADER, session.sessionid)
            self._session = session

        return self._session

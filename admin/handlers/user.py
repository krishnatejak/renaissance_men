from tornado.web import authenticated

from admin.handlers.common import BaseHandler

from admin.service.user import *
from exc import AppException, handle_exceptions

__all__ = ['UserHandler', 'UserVerifyHandler']

class UserHandler(BaseHandler):
    resource_name = 'user'
    update_ignored = {'verified', 'id', 'admin', 'email'}

    @authenticated
    def get(self):
        user = get_user(self.dbsession, self.session['buid'])
        self.send_model_response(user)

    @authenticated
    def put(self):
        data = self.check_input('update')
        user = update_user(self.dbsession, self.session['buid'], data)
        self.send_model_response(user)


class UserVerifyHandler(BaseHandler):
    @authenticated
    @handle_exceptions
    def post(self, uid):
        otp = self.get_argument('otp', None)

        if otp is not None:
            verify_otp(self.dbsession, self.redisdb, uid, otp)
        else:
            raise AppException('otp required to verify user')

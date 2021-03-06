from admin.handlers.common import BaseHandler

from admin.service.user import *
from exc import AppException, handle_exceptions
from utils import allow

__all__ = ['UserHandler', 'UserVerifyHandler', 'AdminUserHandler']


class UserHandler(BaseHandler):
    resource_name = 'user'
    update_ignored = {'verified', 'id', 'admin', 'email'}

    @handle_exceptions
    @allow('service_provider', 'service_user', 'admin', base=True)
    def get(self, *args, **kwargs):
        user = get_user(self.dbsession, kwargs['buid'])
        self.send_model_response(user)

    @handle_exceptions
    @allow('service_provider', 'service_user', 'admin')
    def put(self, *args, **kwargs):
        data = self.check_input('update')
        user = update_user(self.dbsession, kwargs['buid'], data)
        self.send_model_response(user)


class UserVerifyHandler(BaseHandler):
    @handle_exceptions
    @allow('service_provider', 'service_user', 'admin', base=True)
    def post(self, *args, **kwargs):
        otp = self.get_argument('otp', None)

        if otp is not None:
            verify_otp(self.dbsession, self.redisdb, kwargs['buid'], otp)
        else:
            raise AppException('otp required to verify user')


class AdminUserHandler(BaseHandler):
    create_required = {'email', 'phone_number'}
    update_ignored = {'admin'}

    @handle_exceptions
    @allow('admin')
    def post(self, *args, **kwargs):
        data = self.check_input('create')
        user = create_user(self.dbsession, data)
        self.send_model_response(user)

    @handle_exceptions
    @allow('admin', allow_list=True)
    def get(self, *args, **kwargs):
        users = get_admin_users(self.dbsession, kwargs['pk'])
        self.send_model_response(users)

    @handle_exceptions
    @allow('admin')
    def put(self, *args, **kwargs):
        data = self.check_input('update')
        user = update_user(self.dbsession, kwargs['pk'], data)
        self.send_model_response(user)

    @handle_exceptions
    @allow('admin')
    def delete(self, *args, **kwargs):
        pass
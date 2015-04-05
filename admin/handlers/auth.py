import json

from tornado.auth import GoogleOAuth2Mixin
from tornado.gen import coroutine
from oauth2client import client
from oauth2client import crypt

from admin.handlers.common import BaseHandler
import config
from admin.service.user import *
from exc import AppException, handle_exceptions

__all__ = ['GoogleAuthHandler']


class GoogleAuthHandler(BaseHandler, GoogleOAuth2Mixin):
    resource_name = 'user'
    REDIRECT_URL = config.GOOGLE_OAUTH_REDIRECT

    @coroutine
    def get(self):
        user_type = self.get_argument('user_type', None)
        next_url = self.get_argument('next', None)

        if next_url:
            self.set_secure_cookie('next', next_url)

        if user_type:
            self.set_secure_cookie('user_type', user_type)

        if self.get_argument('code', False):
            user = yield self.get_authenticated_user(
                redirect_uri=self.REDIRECT_URL,
                code=self.get_argument('code'))

            try:
                details = client.verify_id_token(
                    user['id_token'],
                    config.GOOGLE_OAUTH2_CLIENT_ID
                )
                user_type = self.get_secure_cookie('user_type')
                user = handle_user_authentication(
                    self.dbsession, details, user_type
                )

                self.session['user_type'] = user_type
                if user_type == 'admin':
                    self.session['buid'] = user.id
                    self.session['uid'] = user.id
                    self.session['admin'] = "true"
                elif user_type in ('service_provider', 'service_user'):
                    self.session['buid'] = user.user_id
                    self.session['uid'] = user.id

                next_url = self.get_secure_cookie('next', None)
                if next_url:
                    self.clear_cookie('next')
                    self.redirect(next_url)
                else:
                    self.send_model_response(user)

            except crypt.AppIdentityError:
                self.set_status(403)
            except AppException:
                self.set_status(400)
                self.write('User is not admin')
        else:
            yield self.authorize_redirect(
                redirect_uri=self.REDIRECT_URL,
                client_id=self.settings['google_oauth']['key'],
                scope=['email', 'profile'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})

    @handle_exceptions
    def post(self):
        data = json.loads(self.request.body)
        user_type = self.get_argument('user_type')
        if 'access_token' in data:
            try:
                details = client.verify_id_token(
                    data['access_token'],
                    config.GOOGLE_OAUTH2_CLIENT_ID
                )
                print details
                user = handle_user_authentication(
                    self.dbsession, details, user_type
                )

                self.session['user_type'] = user_type
                if user_type == 'admin':
                    self.session['buid'] = user.id
                    self.session['admin'] = "true"
                elif user_type in ('service_provider', 'service_user'):
                    self.session['buid'] = user.user_id
                    self.session['uid'] = user.id

                self.send_model_response(user)
            except crypt.AppIdentityError:
                self.set_status(403)
        else:
            self.set_status(400)
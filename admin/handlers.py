import json

from tornado.web import RequestHandler, authenticated
from tornado.auth import GoogleOAuth2Mixin
from tornado.gen import coroutine

from session import SessionMixin

from oauth2client import client
from oauth2client import crypt
import db
from admin.service.serviceprovider import *
from admin.service.job import *
from admin.service.user import *
from admin.service.signup import *
from admin.service.order import *
from admin.tasks import admin_add_all
from utils import model_to_dict, TornadoJSONEncoder
from utils import sp, su
from exc import AppException, handle_exceptions

import config


__all__ = ['ServiceProviderHandler', 'JobHandler',
           'JobStartHandler', 'JobEndHandler', 'JobAcceptHandler',
           'JobRejectHandler', 'PopulateHandler','GoogleAuthHandler',
           'ServiceProviderJobHandler','SignupEmail', 'OrderHandler',
           'OrderStatusHandler','UserHandler', 'UserVerifyHandler',
           'CloseHandler']


class BaseHandler(RequestHandler, SessionMixin):
    resource_name = None
    create_required = {}
    update_ignored = {}
    model_response_uris = {'href': '/api/{resource_name}/{id}/'}

    def initialize(self):
        self.dbsession = db.Session()
        self.redisdb = db.Redis()

    def on_finish(self):
        self.dbsession.close()

    def check_input(self, input_type='create'):
        data = json.loads(self.request.body)
        if input_type == 'create':
            if not self.create_required <= set(data.keys()):
                raise AppException(
                    'required fields %s missing' %
                    ','.join(self.create_required - set(data.keys()))
                )
            else:
                return data
        elif input_type == 'update':
            for ignore_field in self.update_ignored:
                data.pop(ignore_field, None)
            return data

    def send_model_response(self, instance_or_query):
        """use this for returning model response"""
        uri_kwargs = {
            'resource_name': self.resource_name
        }
        models_dict = model_to_dict(
            instance_or_query,
            self.model_response_uris,
            uri_kwargs
        )
        self.set_status(200)
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(models_dict, cls=TornadoJSONEncoder))
        self.finish()

    def get_current_user(self):
        if 'buid' in self.session and 'user_type' in self.session:
            return '%s:%s' % (self.session['user_type'], self.session['buid'])


class ServiceProviderHandler(BaseHandler):
    resource_name = 'serviceprovider'
    create_required = {'name', 'phone_number'}
    update_ignored = {'service'}

    def get_login_url(self):
        return '/api/serviceprovider/auth/google/'

    @sp
    @handle_exceptions
    def put(self, id=None):
        data = self.check_input('update')
        service_provider = update_service_provider(self.dbsession, id, data)
        self.send_model_response(service_provider)

    @sp
    @handle_exceptions
    def get(self, id=None):
        service_provider = get_service_provider(self.dbsession, id)
        self.send_model_response(service_provider)

    @sp
    @handle_exceptions
    def delete(self, id=None):
        is_deleted = get_service_provider(self.dbsession, id)
        self.set_status(204)
        self.write('')
        self.finish()

    def send_model_response(self, instance_or_query):
        uri_kwargs = {
            'resource_name': self.resource_name
        }
        models_dict = model_to_dict(
            instance_or_query,
            self.model_response_uris,
            uri_kwargs
        )

        models_dict['skills'] = get_service_provider_skills(
            self.dbsession,
            instance_or_query.id
        )

        self.set_status(200)
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(models_dict, cls=TornadoJSONEncoder))
        self.finish()


class JobHandler(BaseHandler):
    resource_name = 'job'
    create_required = {'service_provider_id', 'service_id', 'location', 'request', 'appointment_time', 'address'}

    model_response_uris = {
        'href': '/{resource_name}/{id}/',
        'start': '/{resource_name}/{id}/start/',
        'end': '/{resource_name}/{id}/end/'
    }

    @handle_exceptions
    def post(self):
        data = self.check_input('create')
        job = create_job(self.dbsession, data)
        self.send_model_response(job)

    @handle_exceptions
    def get(self, jid):
        job = get_job(self.dbsession, jid)
        self.send_model_response(job)


class JobStartHandler(BaseHandler):
    resource_name = 'job'
    model_response_uris = {}

    @handle_exceptions
    def post(self, jid):
        set_job_started(self.dbsession, jid)
        self.set_status(200)
        self.flush()


class JobEndHandler(BaseHandler):
    resource_name = 'job'
    model_response_uris = {}

    @handle_exceptions
    def post(self, jid):
        set_job_ended(self.dbsession, jid)
        self.set_status(200)
        self.flush()

class JobAcceptHandler(BaseHandler):
    resource_name = 'job'
    model_response_uris = {}

    @authenticated
    @handle_exceptions
    def put(self, jid):
        set_job_accepted(self.dbsession, jid)
        self.set_status(200)
        self.flush()

class JobRejectHandler(BaseHandler):
    resource_name = 'job'
    model_response_uris = {}

    @authenticated
    @handle_exceptions
    def put(self, jid):
        set_job_rejected(self.dbsession, jid)
        self.set_status(200)
        self.flush()

class PopulateHandler(RequestHandler):
    def post(self):
        admin_add_all.apply_async()
        self.set_status(200)
        self.finish()

class ServiceProviderJobHandler(BaseHandler):
    @handle_exceptions
    def get(self, spid):
        status = self.get_argument("status", "").split(",")
        jobs = fetch_jobs_by_status(self.dbsession, spid, status)
        self.send_model_response(jobs)


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


class SignupEmail(BaseHandler):
    resource_name = 'signup'
    create_required = {'email'}

    @handle_exceptions
    def post(self):
        data = self.check_input('create')
        signupemail = save_signup_email(self.dbsession, data['email'], feedback=data.get('feedback'))
        email_dict = {
            "email" : signupemail.email,
            "feedback":signupemail.feedback
        }
        self.set_status(200)
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(email_dict))
        self.finish()


class OrderHandler(BaseHandler):
    resource_name = 'order'
    create_required = {'service', 'request', 'scheduled',}
    update_ignored = {'id', 'status', 'completed', 'created'}

    @su
    @handle_exceptions
    def post(self, id=None):
        data = self.check_input('create')
        order = create_order(
            self.dbsession, self.redisdb, data, self.session['user_id']
        )
        self.send_model_response(order)

    @su
    @handle_exceptions
    def get(self, id=None):
        orders = get_order(
            self.dbsession,
            oid=id,
            user_type=self.session['user_type'],
            user_id=self.session['user_id']
        )
        self.send_model_response(orders)

    @su
    @handle_exceptions
    def put(self, id=None):
        data = self.check_input('update')
        order = update_order(self.dbsession, id, data)
        self.send_model_response(order)


class OrderStatusHandler(BaseHandler):
    resource_name = 'order'

    @authenticated
    def get(self, status):
        orders = get_status_orders(
            self.dbsession,
            status,
            self.session['user_type'],
            self.session['user_id']
        )
        self.send_model_response(orders)


class UserHandler(BaseHandler):
    resource_name = 'user'
    update_ignored = {'verified', 'id', 'admin', 'email'}

    @authenticated
    def get(self, uid):
        if uid and uid != self.session['user_id']:
            raise AppException('Cannot access resource')
        user = get_user(self.dbsession, self.session['user_id'])
        self.send_model_response(user)

    @authenticated
    def put(self, uid):
        data = self.check_input('update')
        user = update_user(self.dbsession, uid, data)
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


class CloseHandler(RequestHandler):

    def get(self):
        self.flush()

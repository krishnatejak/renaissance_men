import json

import jwt
from tornado.web import RequestHandler, asynchronous
from tornado.auth import GoogleOAuth2Mixin
from tornado.gen import coroutine
from tornado import escape

from session import SessionMixin
import db
from admin.service.serviceprovider import *
from admin.service.job import *
from admin.service.service import *
from admin.tasks import admin_add_all
from utils import model_to_dict, TornadoJSONEncoder
from exc import AppException, handle_exceptions
import config


__all__ = ['ServiceProviderHandler', 'ServiceHandler', 'JobHandler',
           'JobStartHandler', 'JobEndHandler', 'ServiceProviderVerifyHandler',
           'ServiceProviderGCMHandler', 'PopulateHandler', 'SpGoogleAuthHandler',
           'UserGoogleAuthHandler']


class BaseHandler(RequestHandler, SessionMixin):
    resource_name = None
    create_required = {}
    update_ignored = {}
    model_response_uris = {'href': '/{resource_name}/{id}/'}

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
        if 'user' in self.session:
            return self.session['user']

class ServiceProviderHandler(BaseHandler):
    resource_name = 'serviceprovider'
    create_required = {'name', 'phone_number'}
    update_ignored = {'service'}

    @handle_exceptions
    def post(self, spid):
        if spid:
            raise AppException('Cannot create with Id')
        data = self.check_input('create')
        service_provider = create_service_provider(self.dbsession, data)
        self.send_model_response(service_provider)

    @handle_exceptions
    def put(self, spid):
        if not spid:
            raise AppException('Cannot update without Id')
        data = self.check_input('update')
        service_provider = update_service_provider(self.dbsession, spid,
                                                   data)
        self.send_model_response(service_provider)

    @handle_exceptions
    def get(self, spid):
        if not spid:
            raise AppException('Cannot fetch without Id')
        service_provider = get_service_provider(self.dbsession, spid)
        self.send_model_response(service_provider)

    @handle_exceptions
    def delete(self, spid):
        if not spid:
            raise AppException('Cannot delete without Id')
        is_deleted = get_service_provider(self.dbsession, spid)
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


class ServiceProviderVerifyHandler(BaseHandler):
    resource_name = 'serviceprovider'

    @handle_exceptions
    def post(self, spid, token):
        if not token:
            initiate_verification(self.dbsession, spid)
        else:
            verify_otp(self.dbsession, self.redisdb, spid, token)


class ServiceProviderGCMHandler(BaseHandler):
    resource_name = 'serviceprovider'
    create_required = {'gcm_reg_id'}

    @handle_exceptions
    def post(self, spid):
        data = self.check_input('create')
        update_gcm_reg_id(self.dbsession, spid, data['gcm_reg_id'])
        self.set_status(200)
        self.finish()


class ServiceHandler(BaseHandler):
    resource_name = 'service'
    create_required = {'name'}

    @handle_exceptions
    def get(self):
        services = get_services(self.dbsession)
        self.send_model_response(services)

    # TODO move this query to redis
    def send_model_response(self, instance_or_query):
        uri_kwargs = {
            'resource_name': self.resource_name
        }
        models_dict = model_to_dict(
            instance_or_query,
            self.model_response_uris,
            uri_kwargs
        )
        for obj in models_dict['objects']:
            obj['skills'] = list(set([
                skill['name']
                for skill in obj['skills']
            ]))
        self.set_status(200)
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(models_dict, cls=TornadoJSONEncoder))
        self.finish()

    @handle_exceptions
    def post(self):
        data = self.check_input('create')
        service = create_service(self.dbsession, data)
        self.send_model_response(service)


class JobHandler(BaseHandler):
    resource_name = 'job'
    create_required = {'service_provider', 'service', 'location', 'request',
                       'inspection', 'appointment_time', 'quote',
                       'quoted_duration', 'materials_required', 'address'}

    model_response_uris = {
        'href': '/{resource_name}/{id}/',
        'start': '/{resource_name}/{id}/start/',
        'end': '/{resource_name}/{id}/end/'
    }

    @handle_exceptions
    def post(self, jid):
        if jid:
            raise AppException('Cannot create with Id')
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


class PopulateHandler(RequestHandler):
    def post(self):
        admin_add_all.apply_async()
        self.set_status(200)
        self.finish()


class GoogleAuthHandler(BaseHandler, GoogleOAuth2Mixin):

    _OAUTH_PROFILE_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'
    REDIRECT_URL = None

    def handle_authenticated_user(self, access_token, token_type):
        print 'inside auth user'
        http = self.get_auth_http_client()
        http.fetch(
            self._OAUTH_PROFILE_URL,
            method='GET',
            headers={'Authorization': '%s %s' % (token_type, access_token)},
            callback=self.user_details_callback
        )

    def user_details_callback(self, response):
        raise NotImplementedError

    @coroutine
    def get(self):
        if self.get_argument('code', False):
            user = yield self.get_authenticated_user(
                redirect_uri=self.REDIRECT_URL,
                code=self.get_argument('code'))
            print user
            self.session['user_type'] = 'service_provider'

            self.handle_authenticated_user(
                user['access_token'], user['token_type']
            )
        else:
            yield self.authorize_redirect(
                redirect_uri=self.REDIRECT_URL,
                client_id=self.settings['google_oauth']['key'],
                scope=['email', 'profile'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


class SpGoogleAuthHandler(GoogleAuthHandler):
    REDIRECT_URL = config.GOOGLE_OAUTH_SP_REDIRECT

    def user_details_callback(self, response):
        response = escape.json_decode(response.body)
        service_provider = authenticate_service_provider(self.dbsession, response)
        self.session['user_id'] = service_provider.id



class UserGoogleAuthHandler(GoogleAuthHandler):
    REDIRECT_URL = config.GOOGLE_OAUTH_USER_REDIRECT

    def handle_authenticated_user(self, access_token, token_type):
        http = self.get_auth_http_client()
        response = yield http.fetch(
            self._OAUTH_PROFILE_URL,
            method='GET',
            headers={'Authorization': '%s %s' % (token_type, access_token)}
        )
        response = escape.json_decode(response)


        # handle user auth response

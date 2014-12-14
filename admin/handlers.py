import json

from tornado.web import RequestHandler
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import db
from admin.service.serviceprovider import *
from admin.service.job import *
from admin.service.service import *
from utils import model_to_dict, TornadoJSONEncoder
from exc import AppException


__all__ = ['ServiceProviderHandler', 'ServiceHandler', 'JobHandler',
           'JobStartHandler', 'JobEndHandler', 'ServiceProviderVerifyHandler']


class BaseHandler(RequestHandler):
    resource_name = None
    create_required = {}
    update_ignored = {}
    model_response_uris = {'href': '/{resource_name}/{id}/'}

    def initialize(self):
        self.dbsession = db.Session()
        self.redisdb = db.REDIS_DB

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
            print e
            instance.set_status(500)
            instance.write({
                'error': str(e)
            })
            instance.flush()
    return _wrapper


class ServiceProviderHandler(BaseHandler):
    resource_name = 'serviceprovider'
    create_required = {'name', 'phone_number', 'address', 'home_location',
                       'office_location', 'cost', 'service', 'experience',
                       'skills'}
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


class ServiceProviderVerifyHandler(BaseHandler):
    resource_name = 'serviceprovider'

    @handle_exceptions
    def post(self, spid, token):
        if not token:
            initiate_verification(self.dbsession, self.redisdb, spid)
        else:
            verify_otp(self.dbsession, self.redisdb, spid, token)


class ServiceHandler(BaseHandler):
    resource_name = 'service'

    @handle_exceptions
    def get(self):
        services = get_services(self.dbsession)
        self.send_model_response(services)


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



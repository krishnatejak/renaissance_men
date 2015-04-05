import json

from exc import handle_exceptions
from utils import model_to_dict, TornadoJSONEncoder
from utils import allow
from admin.handlers.common import BaseHandler
from admin.service.serviceprovider import *
from admin.service.order import get_sp_orders_by_status

__all__ = ['ServiceProviderHandler', 'ServiceProviderJobHandler',
           'ServiceProviderOrdersHandler']


class ServiceProviderHandler(BaseHandler):
    resource_name = 'serviceprovider'
    create_required = {'email', 'phone_number'}
    update_ignored = {'service', 'id'}

    @handle_exceptions
    @allow('service_provider', base=True)
    def put(self, *args, **kwargs):
        data = self.check_input('update')
        service_provider = update_service_provider(
            self.dbsession, kwargs['pk'], data
        )
        self.send_model_response(service_provider)

    @handle_exceptions
    @allow('service_provider', base=True)
    def get(self, *args, **kwargs):
        service_provider = get_service_provider(self.dbsession, kwargs['pk'])
        self.send_model_response(service_provider)

    @handle_exceptions
    @allow('admin')
    def post(self, *args, **kwargs):
        data = self.check_input('create')
        service_provider = create_service_provider(self.dbsession, data)
        self.send_model_response(service_provider)

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


class ServiceProviderJobHandler(BaseHandler):

    @handle_exceptions
    @allow('service_provider', base=True)
    def get(self, *args, **kwargs):
        status = self.get_argument("status", "")
        jobs = fetch_jobs_by_status(self.dbsession, kwargs['pk'], status)
        self.send_model_response(jobs)


class ServiceProviderOrdersHandler(BaseHandler):

    @handle_exceptions
    @allow('service_provider', base=True)
    def get(self, *args, **kwargs):
        status = self.get_argument("status", "")
        orders = get_sp_orders_by_status(self.dbsession, kwargs['pk'], status)
        self.send_model_response(orders)
import json

from exc import handle_exceptions
from utils import sp, model_to_dict, TornadoJSONEncoder
from admin.handlers.common import BaseHandler
from admin.service.serviceprovider import *

__all__ = ['ServiceProviderHandler', 'ServiceProviderJobHandler']

class ServiceProviderHandler(BaseHandler):
    resource_name = 'serviceprovider'
    create_required = {'name', 'phone_number'}
    update_ignored = {'service'}

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
    def get(self, spid):
        status = self.get_argument("status", "").split(",")
        jobs = fetch_jobs_by_status(self.dbsession, spid, status)
        self.send_model_response(jobs)
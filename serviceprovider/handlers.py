import json

from tornado.web import RequestHandler

import db
from serviceprovider.util import *
from utils import model_to_dict


__all__ = ['ServiceProviderHandler', 'ServiceProvider_id_Handler']


class BaseHandler(RequestHandler):

    resource_name = None

    def initialize(self):
        self.dbsession = db.Session()


    def on_finish(self):
        self.dbsession.close()


class ServiceProviderHandler(BaseHandler):

    resource_name = 'serviceproviders'

    def post(self):
        post_data = json.loads(self.request.body)
        service_provider = create_service_provider(self.dbsession, post_data)
        self.write(model_to_dict(service_provider, self.resource_name))
        self.finish()

class ServiceProvider_id_Handler(BaseHandler):

    resource_name = 'serviceproviders/{0}'

    def put(self, provider_id):
        put_data = json.loads(self.request.body)
        service_provider = update_service_provider(self.dbsession, provider_id, put_data)
        self.write(model_to_dict(service_provider, self.resource_name.format(provider_id)))
        self.finish()

    def get(self, provider_id):
        service_provider = get_service_provider(self.dbsession, provider_id)
        self.write(model_to_dict(service_provider, self.resource_name.format(provider_id)))
        self.finish()

    def delete(self, provider_id):
        is_deleted = get_service_provider(self.dbsession, provider_id)
        self.set_status(204)
        self.write('')
        self.finish()
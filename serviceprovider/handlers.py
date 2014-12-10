import json

from tornado.web import RequestHandler

import db
from serviceprovider.util import create_service_provider
from utils import model_to_dict


__all__ = ['ServiceProviderHandler']


class BaseHandler(RequestHandler):
    def initialize(self):
        self.dbsession = db.Session()


class ServiceProviderHandler(BaseHandler):
    def get(self, provider_id):
        pass

    def post(self):
        post_data = json.loads(self.request.body)
        service_provider = create_service_provider(self.dbsession, post_data)
        self.write(model_to_dict(service_provider))
        self.dbsession.close()
        self.finish()

    def put(self, provider_id):
        pass

    def delete(self, provider_id):
        pass
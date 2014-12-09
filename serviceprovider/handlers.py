import json
from tornado.web import RequestHandler
from db import DB_ENGINE as engine

from serviceprovider.util import create_service_provider
__all__ = ['ServiceProviderHandler']

class BaseHandler(RequestHandler):
    def initialize(self, dbsession):
        self.dbsession = dbsession


class ServiceProviderHandler(RequestHandler):

    def get(self, provider_id):
        pass

    def post(self):
        post_data = json.loads(self.request.body)
        return_dict = create_service_provider(engine, post_data)
        self.set_status(return_dict.pop('response_code'))
        self.write(return_dict)
        self.finish()

    def put(self, provider_id):
        pass

    def delete(self, provider_id):
        pass
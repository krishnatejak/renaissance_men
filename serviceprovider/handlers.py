from tornado.web import RequestHandler

__all__ = ['ServiceProviderHandler']

class BaseHandler(RequestHandler):
    def initialize(self, dbsession):
        self.dbsession = dbsession


class ServiceProviderHandler(RequestHandler):

    def get(self, provider_id):
        pass

    def post(self):
        pass

    def put(self, provider_id):
        pass

    def delete(self, provider_id):
        pass
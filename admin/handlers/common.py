import json

from tornado.web import RequestHandler

import db
from exc import AppException
from session import SessionMixin
from utils import model_to_dict, TornadoJSONEncoder
from admin import tasks

__all__ = ['CloseHandler', 'PopulateHandler']


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

    def send_model_response(self, instance_or_query, follow=False):
        """use this for returning model response"""
        uri_kwargs = {
            'resource_name': self.resource_name
        }
        models_dict = model_to_dict(
            instance_or_query,
            self.model_response_uris,
            uri_kwargs,
            follow=follow
        )
        self.set_status(200)
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(models_dict, cls=TornadoJSONEncoder))
        self.finish()

    def get_current_user(self):
        if 'buid' in self.session and 'user_type' in self.session:
            return '%s:%s' % (self.session['user_type'], self.session['buid'])


class CloseHandler(RequestHandler):
    def get(self):
        self.flush()


class PopulateHandler(RequestHandler):
    def post(self):
        tasks.admin_add_all.apply_async()
        self.set_status(200)
        self.finish()
from tornado.web import authenticated

from admin.handlers.common import BaseHandler
from admin.service.job import *
from exc import handle_exceptions

__all__ = ['JobHandler', 'JobAcceptHandler', 'JobEndHandler',
           'JobStartHandler', 'JobRejectHandler']

class JobHandler(BaseHandler):
    resource_name = 'job'
    create_required = {'service_provider_id', 'service_id', 'location',
                       'request', 'appointment_time', 'address'}

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
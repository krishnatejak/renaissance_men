import json

from tornado.web import RequestHandler

from session import SessionMixin
from exc import handle_exceptions, AppException
import db
from search.service.search_service import *
from search.service.slots import *
from utils import TornadoJSONEncoder
__all__ = ['SearchHandler', 'SlotHandler']


class SearchHandler(RequestHandler, SessionMixin):
    def initialize(self):
        self.r = db.Redis()

    @handle_exceptions
    def get(self):
        service = self.get_argument("s", None)
        skill = self.get_argument("sk", None)
        if service and not self.r.hget(self.session.sessionid,'search_id:{0}'.format(service)):
            latitude = self.request.headers.get('latitude')
            longitude = self.request.headersget('longitude')
        else:
            latitude = None
            longitude = None
        data = handle_search(self.r, service, skill, latitude, longitude, self.session.sessionid)
        self.write(json.dumps(data))
        self.finish()

    def post(self):
        """expected json
            {
                "request": <request string>,
                "q1": <addtional question>,
                "a1": <additional answer>,
                "q2": ,
                "a2" ,
                "e"
                "location": [lat, long],
                "scheduled": date time
            }
        """
        """
        brief search process
        1. break down request, q*, a* into meaningful service, skills
        2. from service filter service providers who might be available at scheduled
        time
        3. filter service providers who will be willing to serve given location
        4. send service request to filtered service providers
        5. find out which service providers acknowledged service request
        6. update service request data structure with service provider responses

        """
        pass


class SlotHandler(RequestHandler, SessionMixin):
    def initialize(self):
        self.r = db.Redis()

    @handle_exceptions
    def get(self, service=None):
        available_slots = get_available_slots(self.r, service)
        self.set_status(200)
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({
            'available_slots': available_slots
        }, cls=TornadoJSONEncoder))
        self.flush()
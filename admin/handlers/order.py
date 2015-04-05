from tornado.web import authenticated

from admin.service.order import *
from admin.handlers.common import BaseHandler
from exc import handle_exceptions
from utils import su

__all__ = ['OrderHandler', 'OrderStatusHandler', 'MissedOrderHandler']

class OrderHandler(BaseHandler):
    resource_name = 'order'
    create_required = {'service', 'request', 'scheduled', 'address'}
    update_ignored = {'id', 'status', 'completed', 'created'}

    @su
    @handle_exceptions
    def post(self, id=None):
        data = self.check_input('create')
        order = create_order(
            self.dbsession, self.redisdb, data, self.session['uid']
        )
        self.send_model_response(order)

    @handle_exceptions
    def get(self, id=None):
        orders = get_order(
            self.dbsession,
            oid=id,
            user_type=self.session['user_type'],
            user_id=self.session['uid']
        )
        self.send_model_response(orders)

    @su
    @handle_exceptions
    def put(self, id=None):
        data = self.check_input('update')
        order = update_order(self.dbsession, id, data)
        self.send_model_response(order)


class OrderStatusHandler(BaseHandler):
    resource_name = 'order'

    @authenticated
    def get(self, status):
        orders = get_status_orders(
            self.dbsession,
            status,
            self.session['user_type'],
            self.session['uid']
        )
        self.send_model_response(orders)

class MissedOrderHandler(BaseHandler):
    resource_name = 'order'
    create_required = {'location'}

    @su
    @handle_exceptions
    def post(self):
        data = self.check_input('create')
        missed_order = save_missed_records(self.dbsession, data['location'])
        self.send_model_response(missed_order)


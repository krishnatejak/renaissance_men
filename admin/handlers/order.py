from tornado.web import authenticated
import json
from admin.service.order import *
from admin.handlers.common import BaseHandler
from exc import handle_exceptions
from utils import su, sp

__all__ = ['OrderHandler', 'OrderStatusHandler', 'MissedOrderHandler',
           'OrderRatingHandler']

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

    @handle_exceptions
    def post(self):
        data = self.check_input('create')
        missed_order = save_missed_records(self.dbsession, data['location'])
        self.send_model_response(missed_order)


class OrderRatingHandler(BaseHandler):

    @authenticated
    def post(self, order_id, rating):
        if self.session['user_type'] == 'service_provider':
            kwargs = {
                'sp_id': self.session['uid'],
                'sp_rating': rating
            }
            save_rating(self.dbsession, order_id, **kwargs)
        elif self.session['user_type'] == 'service_user':
            kwargs = {
                'su_id': self.session['uid'],
                'su_rating': rating
            }
            save_rating(self.dbsession, order_id, **kwargs)


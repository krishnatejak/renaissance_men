from admin.service.order import *
from admin.handlers.common import BaseHandler
from exc import handle_exceptions, AppException
from utils import allow, verify_rating_sanity

__all__ = ['OrderHandler', 'SuOrderStatusHandler', 'MissedOrderHandler',
           'OrderRatingHandler', 'UpdateOrderStatusHandler',
           'AssignOrderHandler', 'AdminOrderHandler', 'OrderBidHandler',
           'AdminOrderBidsHandler']


class OrderHandler(BaseHandler):
    resource_name = 'order'
    create_required = {'service', 'request', 'scheduled', 'address'}
    update_ignored = {'id', 'completed', 'created'}

    @handle_exceptions
    @allow('service_user')
    def post(self, *args, **kwargs):
        data = self.check_input('create')
        order = create_order(
            self.dbsession, self.redisdb, data, kwargs['uid']
        )
        self.send_model_response(order)

    @handle_exceptions
    @allow('service_user', allow_list=True)
    def get(self, *args, **kwargs):
        orders = get_order(
            self.dbsession,
            kwargs['uid'],
            oid=kwargs['pk']
        )
        self.send_model_response(orders)




class SuOrderStatusHandler(BaseHandler):
    resource_name = 'order'

    @allow('service_user')
    def get(self, *args, **kwargs):
        orders = get_su_orders_by_status(
            self.dbsession,
            kwargs['status'],
            self.session['uid']
        )
        self.send_model_response(orders)


class MissedOrderHandler(BaseHandler):
    resource_name = 'order'
    create_required = {'location'}
    @allow('admin', allow_list=True)
    def get(self, *args, **kwargs):
        missedorders = get_missed_orders(
            self.dbsession)
        self.send_model_response(missedorders)


    @handle_exceptions
    def post(self):
        data = self.check_input('create')
        missed_order = save_missed_records(self.dbsession, data)
        self.send_model_response(missed_order)


class OrderRatingHandler(BaseHandler):
    #@allow('service_user', 'service_provider')
    @handle_exceptions
    def post(self, *args, **kwargs):

        if 'order_info' in kwargs:
            order_string = verify_rating_sanity(kwargs)

        if order_string:
            save_rating(self.dbsession, order_string, kwargs['rating'])
        else:
            raise AppException('Please provide correct order info')


class UpdateOrderStatusHandler(BaseHandler):

    @handle_exceptions
    @allow('admin', post_pk=True)
    def post(self, *args, **kwargs):
        order = update_order_status(
            self.dbsession, kwargs['pk'], kwargs['status']
        )
        self.send_model_response(order, follow=True)


class AssignOrderHandler(BaseHandler):
    create_required = {'phone_number'}

    @handle_exceptions
    @allow('admin', post_pk=True)
    def post(self, *args, **kwargs):
        data = self.check_input('create')
        order = assign_order_to_phone_number(
            self.dbsession, kwargs['pk'], data['phone_number']
        )
        self.send_model_response(order, follow=True)


class AdminOrderHandler(OrderHandler):

    @handle_exceptions
    @allow('admin', allow_list=True)
    def get(self, *args, **kwargs):
        orders = get_admin_orders(self.dbsession, kwargs['pk'])
        self.send_model_response(orders, follow=True)

    @handle_exceptions
    @allow('admin')
    def post(self, *args, **kwargs):
        pass

    @handle_exceptions
    @allow('admin', 'service_provider')
    def put(self, *args, **kwargs):
        data = self.check_input('update')
        order = update_order(self.dbsession, kwargs['pk'], data)
        self.send_model_response(order, follow=True)

    @handle_exceptions
    @allow('admin')
    def delete(self, *args, **kwargs):
        pass


class OrderBidHandler(BaseHandler):

    @handle_exceptions
    @allow('service_provider')
    def post(self, *args, **kwargs):
        accepted = 'accept' in kwargs
        order_bid = bid_order(
            self.dbsession, kwargs['pk'], kwargs['uid'], accepted=accepted
        )
        self.send_model_response(order_bid)


class AdminOrderBidsHandler(BaseHandler):

    @handle_exceptions
    @allow('admin')
    def get(self, *args, **kwargs):
        order_bids = get_sp_order_bids(self.dbsession, kwargs['pk'])
import json

from admin.models import *
from admin import tasks
import config
from search.service.slots import assign_slot_to_sp
from admin.service.serviceprovider import get_sp_for_phone_number

from exc import AppException
from utils import transaction, update_model_from_dict, parse_datetime

__all__ = ['create_order', 'get_order', 'get_su_orders_by_status', 'update_order',
           'save_missed_records','get_missed_orders', 'save_rating', 'update_order_status',
           'assign_order_to_phone_number', 'get_admin_orders', 'bid_order',
           'get_sp_order_bids', 'get_admin_order_bids']


@transaction
def create_order(dbsession, redis, data, uid):
    order = Orders()
    service_provider_id = assign_slot_to_sp(
        redis, data['service'], data['scheduled']
    )
    data['service_provider_id'] = service_provider_id
    data['scheduled'] = parse_datetime(data['scheduled'])

    update_model_from_dict(order, data)
    order.service_user_id = uid
    order.status = 'assigned'
    dbsession.add(order)

    order_rating = OrderRating()
    order_rating.order_id = order.id
    dbsession.add(order_rating)

    dbsession.commit()
    tasks.post_order_creation.apply_async(
        (service_provider_id, data['scheduled'], order.id),
        queue=config.ORDER_QUEUE
    )
    return order


def get_order(dbsession, user_id, oid=None):
    if oid:
        orders = dbsession.query(Orders).filter(
            Orders.id == oid,
            Orders.service_user_id == user_id
        ).one()
    else:
        orders = dbsession.query(Orders).filter(
            Orders.service_user_id == user_id
        ).order_by(Orders.created.desc())
    return orders


@transaction
def update_order(dbsession, oid, data):
    order = dbsession.query(Orders).filter(
        Orders.id == oid
    ).one()
    update_model_from_dict(order, data)
    dbsession.add(order)
    dbsession.commit()

    tasks.post_order_update.apply_async(
        (data.get('status_changed'), oid),
        queue=config.ORDER_QUEUE
    )

    return order


def get_su_orders_by_status(dbsession, status, user_id):
    if status == 'all':
        orders = dbsession.query(Orders).filter(
            Orders.service_user_id == user_id,
        )
    else:
        orders = dbsession.query(Orders).filter(
            Orders.service_user_id == user_id,
            Orders.status == status
        )

    return orders.order_by(Orders.created.desc())


@transaction
def save_missed_records(dbsession, data):
    missed_order = MissedOrders()

    missed_order.location = data['location']
    if data['service_available']:
        missed_order.service_available = True
    dbsession.add(missed_order)
    dbsession.commit()
    return missed_order

def get_missed_orders(dbsession, oid=None):

    orders = dbsession.query(MissedOrders).filter(
            MissedOrders.service_available == False,
        )

    return orders.order_by(MissedOrders.created.desc())



@transaction
def save_rating(dbsession, order_string, rating):
    order_id, user, user_id = order_string.split('.')
    order = dbsession.query(Orders).filter(
        Orders.id == order_id
    ).one()
    order_rating = dbsession.query(OrderRating).filter(
        OrderRating.order_id == order_id
    ).one()

    if user == 'sp':
        sp_id = int(user_id)
        if order.service_provider_id != sp_id:
            raise AppException('Cannot rate order, sp not assigned to this order')
        sp_rating = int(rating)
        if not (0 <= sp_rating <= 5):
            raise AppException('rating value should be between 0 and 5')
        order_rating.sp_rating = sp_rating
        dbsession.add(order_rating)
    elif user == 'su':
        su_id = int(user_id)
        if order.service_user_id != su_id:
            raise AppException('Cannot rate order, su not assigned to this order')
        su_rating = int(rating)
        if not (0 <= su_rating <= 5):
            raise AppException('rating value should be between 0 and 5')
        order_rating.su_rating = su_rating
        dbsession.add(order_rating)
    else:
        raise AppException('Cannot rate order without sp/su')
    dbsession.commit()


def get_sp_orders_by_status(dbsession, spid, status):
    orders = dbsession.query(Orders).filter(
        Orders.service_provider_id == spid
    )
    if status:
        status = status.strip()
        status = status.split(',')
        orders = dbsession.query(Orders).filter(
            Orders.status.in_(status)
        )
    return orders


def update_order_status(dbsession, oid, status):
    if status not in Orders.status_types:
        raise AppException('invalid status')
    order = dbsession.query(Orders).filter(
        Orders.id == oid
    ).one()

    if order.status != status:
        order.status = status
        dbsession.add(order)
        dbsession.commit()

        tasks.post_order_update.apply_async(
            (oid,),
            queue=config.ORDER_QUEUE
        )
    return order


def assign_order_to_phone_number(dbsession, oid, phone_number):
    service_provider = get_sp_for_phone_number(dbsession, phone_number)
    order = dbsession.query(Orders).filter(
        Orders.id == oid
    ).one()
    order.service_provider_id = service_provider.id
    order.status = 'assigned'
    dbsession.add(order)
    dbsession.commit()
    return order


def get_order_rating_message(dbsession, oid, user_type='service_user'):
    pass


def get_admin_orders(dbsession, oid=None):

    if oid:
        order = dbsession.query(Orders).filter(
            Orders.id == oid
        ).one()
    else:
        order = dbsession.query(Orders).order_by(Orders.created.desc())
    return order


@transaction
def bid_order(dbsession, oid, spid, accepted=False):
    order = dbsession.query(Orders).filter(
        Orders.id == oid
    ).one()

    service_provider = dbsession.query(ServiceProvider).filter(
        ServiceProvider.id == spid
    ).one()

    if not order.service in service_provider.skills:
        raise AppException('order service not offered by service provider')

    order_bids = dbsession.query(OrderBid).filter(
        OrderBid.order_id == oid,
        OrderBid.service_provider_id == spid
    ).count()

    if order_bids > 0:
        raise AppException('service provider already bid for the order')

    order_bid = OrderBid()
    order_bid.order_id = oid
    order_bid.service_provider_id = spid
    order_bid.accepted = accepted

    # TODO verify if slot is free for service provider before assignment
    if not order.service_provider_id:
        order.service_provider_id = spid
        order.status = 'assigned'
        order_bid.selected = True

    dbsession.add(order)
    dbsession.add(order_bid)

    dbsession.commit()
    return order_bid


def get_sp_order_bids(dbsession, spid):
    order_bids = dbsession.query(OrderBid).filter(
        OrderBid.service_provider_id == spid
    ).order_by(OrderBid.created.desc())

    return order_bids


def get_admin_order_bids(dbsession, oid):
    order_bids = dbsession.query(OrderBid).filter(
        OrderBid.order_id == oid
    )

    return order_bids
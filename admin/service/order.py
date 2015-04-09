from admin.models import Orders, MissedOrders, OrderRating
from admin import tasks
import config
from search.service.slots import assign_slot_to_sp
from admin.service.serviceprovider import get_sp_for_phone_number

from exc import AppException
from utils import transaction, update_model_from_dict, parse_datetime

__all__ = ['create_order', 'get_order', 'get_su_orders_by_status', 'update_order',
           'save_missed_records', 'save_rating', 'update_order_status',
           'assign_order_to_phone_number', 'get_admin_orders']


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
    )
    update_model_from_dict(order, data)
    dbsession.add(order)
    dbsession.commit()
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


@transaction
def save_rating(dbsession, order_id, **kwargs):
    """expects kwargs in {
        "sp_id": service_provider id,
        "sp_rating": service provider rating
        "su_id": service_user id,
        "su_rating": service user rating
    }"""

    order = dbsession.query(Orders).filter(
        Orders.id == order_id
    ).one()

    order_rating = dbsession.query(OrderRating).filter(
        OrderRating.order_id == order_id
    ).one()

    if all([
        kwargs.get('sp_id'),
        kwargs.get('sp_rating')
    ]):
        sp_id = int(kwargs['sp_id'])
        if order.service_provider_id != sp_id:
            raise AppException('Cannot rate order, sp not assigned to this order')
        sp_rating = int(kwargs['sp_rating'])
        if not (0 <= sp_rating <= 5):
            raise AppException('rating value should be between 0 and 5')
        order_rating.sp_rating = sp_rating
        dbsession.add(order_rating)
    elif all([
        kwargs.get('su_id'),
        kwargs.get('su_rating')
    ]):
        su_id = kwargs['su_id']
        if order.service_user_id != su_id:
            raise AppException('Cannot rate order, su not assigned to this order')
        su_rating = int(kwargs['su_rating'])
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
        orders = dbsession.filter(
            Orders.status.in_(status)
        )
    return orders


def update_order_status(dbsession, oid, status):
    if status not in Orders.status_types:
        raise AppException('invalid status')
    order = dbsession.query(Orders).filter(
        Orders.id == oid
    ).one()

    order.status = status
    dbsession.add(order)
    dbsession.commit()
    return order


def assign_order_to_phone_number(dbsession, oid, phone_number):
    service_provider = get_sp_for_phone_number(dbsession, phone_number)
    order = dbsession.query(Orders).filter(
        Orders.id == oid
    ).one()
    order.service_provider_id = service_provider.id
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
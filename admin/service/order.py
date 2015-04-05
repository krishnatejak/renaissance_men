from admin.models import Orders, MissedOrders, OrderRating
from admin import tasks
import config
from search.service.slots import assign_slot_to_sp
from exc import AppException
from utils import transaction, update_model_from_dict, parse_datetime

__all__ = ['create_order', 'get_order', 'get_status_orders', 'update_order',
           'save_missed_records', 'save_rating']


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


def get_order(dbsession, oid=None, user_type='service_user', user_id=None):
    if oid:
        orders = dbsession.query(Orders).filter(
            Orders.id == oid
        ).one()
    elif user_type == 'service_user':
        orders = dbsession.query(Orders).filter(
            Orders.service_user_id == user_id
        )
    elif user_type == 'service_provider':
        orders = dbsession.query(Orders).filter(
            Orders.service_provider_id == user_id
        )
    elif user_type == 'admin':
        orders = dbsession.query(Orders).all()
    else:
        raise AppException('user_type/order id required')
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


def get_status_orders(dbsession, status, user_type='service_user', uid=None):
    orders = dbsession.query(Orders).filter(
        Orders.status == status
    )
    if user_type == 'service_user':
        orders = orders.filter(
            Orders.service_user_id == uid
        )
    elif user_type == 'service_provider':
        orders = orders.filter(
            Orders.service_provider_id == uid
        )

    return orders


@transaction
def save_missed_records(dbsession, location):
    missed_order = MissedOrders()
    missed_order.location = location
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





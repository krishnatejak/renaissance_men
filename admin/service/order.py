from admin.models import Orders
from admin import tasks
import config
from search.service.slots import assign_slot_to_sp
from exc import AppException
from utils import transaction, update_model_from_dict, parse_json_datetime

__all__ = ['create_order', 'get_order', 'get_status_orders', 'update_order']


@transaction
def create_order(dbsession, redis, data, uid):
    order = Orders()
    service_provider_id = assign_slot_to_sp(
        redis, data['service'], data['scheduled']
    )
    data['service_provider_id'] = service_provider_id
    data['scheduled'] = parse_json_datetime(data['scheduled'])

    update_model_from_dict(order, data)
    order.service_user_id = uid
    dbsession.add(order)
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



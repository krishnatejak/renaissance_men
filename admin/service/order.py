from admin.models import Order
from search.service.slots import assign_slot_to_sp
from exc import AppException
from utils import transaction, update_model_from_dict, parse_json_datetime

__all__ = ['create_order', 'get_order', 'get_status_orders', 'update_order']

@transaction
def create_order(dbsession, redis, data, uid):
    order = Order()
    service_provider_id = assign_slot_to_sp(
        redis, data['service'], data['scheduled']
    )
    data['service_provider_id'] = service_provider_id
    data['scheduled'] = parse_json_datetime(data['scheduled'])
    update_model_from_dict(order, data)
    order.service_user_id = uid
    dbsession.add(order)
    dbsession.commit()
    return order


def get_order(dbsession, oid=None, user_type='service_user', user_id=None):
    if oid:
        orders = dbsession.query(Order).filter(
            Order.id == oid
        ).one()
    elif user_type == 'service_user':
        orders = dbsession.query(Order).filter(
            Order.service_user_id == user_id
        )
    elif user_type == 'service_provider':
        orders = dbsession.query(Order).filter(
            Order.service_provider_id == user_id
        )
    elif user_type == 'admin':
        orders = dbsession.query(Order).all()
    else:
        raise AppException('user_type/order id required')
    return orders


@transaction
def update_order(dbsession, oid, data):
    order = dbsession.query(Order).filter(
        Order.id == oid
    )
    update_model_from_dict(order, data)
    dbsession.add(order)
    dbsession.commit()
    return order


def get_status_orders(dbsession, status, user_type='service_user', uid=None):
    orders = dbsession.query(Order).filter(
        Order.status == status
    )
    if user_type == 'service_user':
        orders = orders.filter(
            Order.service_user_id == uid
        )
    elif user_type == 'service_provider':
        orders = orders.filter(
            Order.service_provider_id == uid
        )

    return orders



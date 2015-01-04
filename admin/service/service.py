from sqlalchemy import func
from admin.models import Service
from utils import transaction, update_model_from_dict
from admin import tasks
from exc import AppException
import config

__all__ = ['get_services', 'create_service', 'get_service_name',
           'get_or_create_service']


def get_services(dbsession):
    return dbsession.query(Service)


@transaction
def create_service(dbsession, data):
    if service_exists(dbsession, data['name']):
        raise AppException('Service already exists')
    service = Service()
    update_model_from_dict(service, data)
    dbsession.add(service)
    dbsession.commit()
    tasks.add_service.apply_async(
        service.id,
        queue=config.SERVICE_QUEUE
    )
    return service


def service_exists(dbsession, service_name):
    service = dbsession.query(Service).filter(
        func.lower(Service.name) == func.lower(service_name),
        Service.trash == False
    ).first()

    return service if service else False


def get_or_create_service(dbsession, service_name):
    """returns service if exists otherwise creates and returns service"""
    service = service_exists(dbsession, service_name)
    if service:
        return service
    else:
        return create_service(dbsession, {'name': service_name})


def get_service_name(dbsession, sid):
    service = dbsession.query(Service.name).filter(
        Service.id == sid,
        Service.trash == False
    ).one()

    return service[0]

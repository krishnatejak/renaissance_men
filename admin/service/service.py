from admin.models import Service
from utils import transaction, update_model_from_dict
from admin import tasks
from exc import AppException
import config

__all__ = ['get_services', 'create_service']


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
    services = dbsession.query(Service).filter(
        Service.name == service_name,
        Service.trash == False
    ).count()

    return services > 0



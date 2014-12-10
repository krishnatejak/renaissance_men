from serviceprovider.models import *
from utils import transaction, update_model_from_dict


@transaction
def create_service_provider(dbsession, data):
    if 'service_name' in data:
        service_name = data.pop('service_name').lower()
        service = dbsession.query(Service).filter(
            Service.name == service_name
        ).one()
    else:
        raise Exception('Cannot create without service name')

    service_provider = ServiceProvider()
    update_model_from_dict(service_provider, data)
    service_provider.service = service
    dbsession.add(service_provider)
    dbsession.commit()
    return service_provider


@transaction
def update_service_provider(dbsession, provider_id, data):
    if provider_id:
        service_provider = dbsession.query(ServiceProvider).filter(
            ServiceProvider.id == provider_id
        ).one()
    else:
        raise Exception('Please provide a service provider id')

    update_model_from_dict(service_provider, data)
    dbsession.add(service_provider)
    dbsession.commit()
    return service_provider

def get_service_provider(dbsession, provider_id):
    if provider_id:
        service_provider = dbsession.query(ServiceProvider).filter(
            ServiceProvider.id == provider_id
        ).one()
    else:
        raise Exception('Please provide a service provider id')

    return service_provider

@transaction
def delete_service_provider(dbsession, provider_id):
    if provider_id:
        service_provider = dbsession.query(ServiceProvider).filter(
            ServiceProvider.id == provider_id
        ).one()
    else:
        raise Exception('Please provide a service provider id')

    service_provider.trash = True
    dbsession.add(service_provider)
    dbsession.commit()

    return True
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







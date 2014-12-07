import db
from serviceprovider.models import *

def get_service_provider(dbsession, provider_id):
    dbsession.query(ServiceProvider).filter_by(
        id=provider_id, trash=False
    ).one()

def get_service_providers(dbsession):
    dbsession.query(ServiceProvider)



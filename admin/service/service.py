from admin.models import Service

__all__ = ['get_services']


def get_services(dbsession):
    return dbsession.query(Service)
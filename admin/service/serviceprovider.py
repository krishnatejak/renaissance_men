import pyotp

from admin.models import *
from utils import transaction, update_model_from_dict
from exc import AppException
from config import OTP_SECRET


__all__ = ['create_service_provider', 'update_service_provider',
           'get_service_provider', 'delete_service_provider',
           'initiate_verification', 'verify_otp']

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
        raise AppException('Please provide a service provider id')

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
        raise AppException('Please provide a service provider id')

    return service_provider

@transaction
def delete_service_provider(dbsession, provider_id):
    if provider_id:
        service_provider = dbsession.query(ServiceProvider).filter(
            ServiceProvider.id == provider_id
        ).one()
    else:
        raise AppException('Please provide a service provider id')

    service_provider.trash = True
    dbsession.add(service_provider)
    dbsession.commit()

    return True


def initiate_verification(dbsession, redisdb, spid):
    service_provider = dbsession.query(ServiceProvider).filter(
        ServiceProvider.id == spid
    ).one()
    count = redisdb.incr('otp_count')
    redisdb.set('otp:' + spid, count)
    hotp = pyotp.HOTP(OTP_SECRET)
    otp = hotp.at(count)
    #TODO send OTP SMS to service provider phone number


def verify_otp(dbsession, redisdb, spid, token):
    service_provider = dbsession.query(ServiceProvider).filter(
        ServiceProvider.id == spid
    ).one()
    count = redisdb.get('otp:' + spid)
    if count:
        count = int(count)
    else:
        raise AppException('No active verification in progress')
    otp = pyotp.HOTP(OTP_SECRET)
    if otp.verify(token, count):
        service_provider.verified = True
        dbsession.add(service_provider)
        redisdb.expire('otp:' + spid)
    else:
        raise AppException('OTP verification failed')

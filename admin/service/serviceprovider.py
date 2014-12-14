import pyotp

from admin.models import Service, ServiceProvider, ServiceSkill
from utils import transaction, update_model_from_dict
from exc import AppException
from config import OTP_SECRET


__all__ = ['create_service_provider', 'update_service_provider',
           'get_service_provider', 'delete_service_provider',
           'initiate_verification', 'verify_otp']

@transaction
def create_service_provider(dbsession, data):
    service_id = data.pop('service')
    service = dbsession.query(Service).filter(Service.id == service_id).one()
    data['service'] = service
    skills = data.pop('skills', [])
    service_provider = ServiceProvider()
    update_model_from_dict(service_provider, data)
    dbsession.add(service_provider)
    dbsession.commit()
    if skills:
        update_service_provider_skills(
            dbsession, service_provider.id, service.id, skills
        )
    return service_provider


@transaction
def update_service_provider(dbsession, provider_id, data):
    if provider_id:
        service_provider = dbsession.query(ServiceProvider).filter(
            ServiceProvider.id == provider_id
        ).one()
    else:
        raise AppException('Please provide a service provider id')
    skills = data.pop('skills', [])
    update_model_from_dict(service_provider, data)
    dbsession.add(service_provider)
    dbsession.commit()
    if skills:
        update_service_provider_skills(
            dbsession, service_provider.id, service_provider.service_id, skills
        )
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


def update_service_provider_skills(dbsession, spid, sid, skills):

    current_skills = set([
        (skill['name'], skill['inspection'])
        for skill in skills
    ])

    existing_skills = dbsession.query(
        ServiceSkill.name, ServiceSkill.inspection
    ).filter(
        ServiceSkill.service_provider_id == spid,
        ServiceSkill.service_id == sid,
        ServiceSkill.trash == False
    ).all()

    existing_skills = set(existing_skills)

    created_skills = current_skills - existing_skills
    deleted_skills = existing_skills - current_skills

    for created_skill in created_skills:
        service_skill = ServiceSkill()
        service_skill.service_id = sid
        service_skill.service_provider_id = spid
        service_skill.name = created_skill[0]
        service_skill.inspection = created_skill[1]
        dbsession.add(service_skill)
    if deleted_skills:
        dbsession.query(ServiceSkill).filter(
            ServiceSkill.service_provider_id == spid,
            ServiceSkill.service_id == sid,
            ServiceSkill.name.in_([skill[0] for skill in deleted_skills])
        ).update({'trash': True}, synchronize_session=False)

    dbsession.commit()

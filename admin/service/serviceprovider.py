import pyotp

from admin.models import Service, ServiceProvider, ServiceSkill, Job
from admin import tasks
from admin.service.service import *
from utils import transaction, update_model_from_dict
from exc import AppException
import config


__all__ = ['create_service_provider', 'update_service_provider',
           'get_service_provider', 'delete_service_provider',
           'initiate_verification', 'verify_otp', 'update_gcm_reg_id',
           'get_service_provider_skills', 'fetch_jobs_by_status',
           'authenticate_service_provider']


@transaction
def create_service_provider(dbsession, data):
    skills = data.pop('skills', {})

    service_provider = ServiceProvider()
    update_model_from_dict(service_provider, data)
    dbsession.add(service_provider)
    dbsession.commit()

    if skills:
        for service_name, service_skills in skills.iteritems():
            service = get_or_create_service(dbsession, service_name)
            update_skills(dbsession, service_provider.id, service.id, service_skills)

    tasks.add_service_provider.apply_async(
        args=(service_provider.id,),
        queue=config.SERVICE_PROVIDER_QUEUE
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
        for service_name, service_skills in skills.iteritems():
            service = get_or_create_service(dbsession, service_name)
            update_skills(dbsession, service_provider.id, service.id, service_skills)

    tasks.update_service_provider.apply_async(
        args=(service_provider.id,),
        queue=config.SERVICE_PROVIDER_QUEUE
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
    tasks.delete_service_provider.apply_async(
        (service_provider.id,),
        queue=config.SERVICE_PROVIDER_QUEUE
    )
    return True

@transaction
def initiate_verification(dbsession, spid, phone_number):
    service_provider = dbsession.query(ServiceProvider).filter(
        ServiceProvider.id == spid,
        ServiceProvider.trash == False
    ).one()

    service_provider.phone_number = phone_number
    dbsession.add(service_provider)
    dbsession.commit()

    tasks.verify_service_provider.apply_async(
        (service_provider.id,),
        queue=config.SERVICE_PROVIDER_QUEUE
    )

def verify_otp(dbsession, redisdb, spid, token):
    service_provider = dbsession.query(ServiceProvider).filter(
        ServiceProvider.id == spid
    ).one()
    count = redisdb.get('otp:' + spid)
    if count:
        count = int(count)
    else:
        raise AppException('No active verification in progress')
    otp = pyotp.HOTP(config.OTP_SECRET)
    if otp.verify(token, count):
        service_provider.verified = True
        dbsession.add(service_provider)
        dbsesion.commit()
        redisdb.delete('otp:' + str(spid))
    else:
        raise AppException('OTP verification failed')

def update_skills(dbsession, spid, sid, skills):
    skill_names = [skill['name'] for skill in skills]
    skills = dbsession.query(ServiceSkill).filter(
        ServiceSkill.name.in_(skill_names),
        ServiceSkill.service_id == sid
    ).all()

    service_provider = dbsession.query(ServiceProvider).filter(ServiceProvider.id == spid).one()
    service_provider.skills = skills
    dbsession.add(service_provider)

    dbsession.commit()

def update_gcm_reg_id(dbsession, spid, gcm_reg_id):
    service_provider = dbsession.query(ServiceProvider).filter(
        ServiceProvider.id == spid,
        ServiceProvider.trash == False
    )
    service_provider.gcm_reg_id = gcm_reg_id
    dbsession.add(service_provider)
    dbsession.commit()


def get_service_provider_skills(dbsession, spid):
    service_provider = dbsession.query(ServiceProvider).filter(ServiceProvider.id == spid).one()

    service_skills = {}
    for skill in service_provider.skills:
        service_name = get_service_name(dbsession, skill.service_id)
        if service_name in service_skills:
            service_skills[service_name].append({
                'name': skill.name,
                'inspection': skill.inspection
            })
        else:
            service_skills[service_name] = [{
                'name': skill.name,
                'inspection': skill.inspection
            }]
    return service_skills

def fetch_jobs_by_status(dbsession, spid, status):
    return dbsession.query(Job).filter(
            Job.service_provider_id == spid,
            Job.status.in_(status))

def authenticate_service_provider(dbsession, user_dict):
    try:
        service_provider = dbsession.query(ServiceProvider).filter(
            ServiceProvider.email == user_dict['email']
        ).one()
    except:
        service_provider = create_service_provider(dbsession, {
            'name': user_dict['name'],
            'email': user_dict['email']
        })
    return service_provider

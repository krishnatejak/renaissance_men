
from admin.models import *
from admin import tasks
from admin.service.service import *
from admin.service.user import create_user
from utils import transaction, update_model_from_dict
from exc import AppException
import config
import constants

__all__ = ['update_service_provider', 'get_service_provider',
           'delete_service_provider', 'create_service_provider',
           'fetch_jobs_by_status', 'get_sp_for_phone_number']


def clean_service_provider_skills(details):
    """sanitizes service provider skills"""
    cleaned_skills = {}
    if isinstance(details, dict) and'skills' in details:
        for service, skills in details['skills'].iteritems():
            if service in constants.ALLOWED_SERVICES:
                skills = set([
                    (skill['inspection'], skill['name']) for skill in skills
                ])
                skills = [
                    dict(inspection=inspection, name=name)
                    for inspection, name in skills
                ]
                cleaned_skills[service] = skills
    return cleaned_skills

@transaction
def create_service_provider(dbsession, data):
    user_data = {
        'email': data['email'],
        'phone_number': data['phone_number']
    }
    user = create_user(dbsession, user_data)
    service_provider = ServiceProvider()
    service_provider.user_id = user.id
    details = data.pop('details', {})
    skills = clean_service_provider_skills(details)
    details['skills'] = skills
    data['details'] = details
    update_model_from_dict(service_provider, data)
    dbsession.add(service_provider)

    dbsession.commit()

    tasks.update_service_provider.apply_async(
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

    details = data.pop('details', {})
    skills = clean_service_provider_skills(details)
    details['skills'] = skills
    data['details'] = details

    update_model_from_dict(service_provider, data)
    dbsession.add(service_provider)
    dbsession.commit()

    tasks.update_service_provider.apply_async(
        args=(service_provider.id,),
        queue=config.SERVICE_PROVIDER_QUEUE
    )
    return service_provider


def get_service_provider(dbsession, spid=None):
    if spid:
        service_provider = dbsession.query(ServiceProvider).filter(
            ServiceProvider.id == spid,
            ServiceProvider.trash == False
        ).one()
    else:
        service_provider = dbsession.query(ServiceProvider).filter(
            ServiceProvider.trash == False
        )

    return service_provider


def delete_service_provider(dbsession, spid):
    # delete service provider, skills
    pass

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




def fetch_jobs_by_status(dbsession, spid, status):
    status = status.strip()
    jobs = dbsession.query(Job).filter(
        Job.service_provider_id == spid,
    )
    if status:
        status = status.split(',')
        jobs = jobs.filter(
            Job.status.in_(status)
        )
    return jobs


def get_sp_for_phone_number(dbsession, phone_number):
    service_provider = dbsession.query(ServiceProvider).filter(
        BaseUser.phone_number == phone_number,
        ServiceProvider.trash == False,
        ServiceProvider.user_id == BaseUser.id
    ).one()
    return service_provider
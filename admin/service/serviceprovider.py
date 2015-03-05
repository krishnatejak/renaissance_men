
from admin.models import ServiceProvider, ServiceSkill, Job, ServiceProviderService, ServiceProviderSkill
from admin import tasks
from admin.service.service import *
from utils import transaction, update_model_from_dict
from exc import AppException
import config


__all__ = ['update_service_provider', 'get_service_provider',
           'delete_service_provider', 'initiate_verification',
           'get_service_provider_skills',
           'fetch_jobs_by_status']


@transaction
def update_service_provider(dbsession, provider_id, data):
    if provider_id:
        service_provider = dbsession.query(ServiceProvider).filter(
            ServiceProvider.id == provider_id
        ).one()
    else:
        raise AppException('Please provide a service provider id')
    skills = data.pop('skills', [])
    user = data.pop('user', {})
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

    tasks.verify_user_phone.apply_async(
        (service_provider.id,),
        queue=config.SERVICE_PROVIDER_QUEUE
    )

'''
def update_skills(dbsession, spid, sid, update_skills):
    skill_names = [skill['name'] for skill in update_skills]
    skills = dbsession.query(ServiceSkill).filter(
        ServiceSkill.name.in_(skill_names),
        ServiceSkill.service_id == sid
    ).all()
    service_provider = dbsession.query(ServiceProvider).filter(ServiceProvider.id == spid).one()
    service_provider.skills = update_skills
    dbsession.add(service_provider)

    dbsession.commit()
'''


def update_skills(dbsession, spid, sid, skills):
    current_skills = set([
        (skill['name'], skill['inspection'])
        for skill in skills
    ])

    existing_skills = dbsession.query(
        ServiceSkill.name, ServiceSkill.inspection
    ).filter(
        ServiceProviderSkill.service_provider_id == spid,
        ServiceSkill.id == ServiceProviderSkill.service_skill_id,
        ServiceSkill.service_id == sid,
        ServiceSkill.trash == False
    ).all()

    existing_skills = set(existing_skills)

    created_skills = current_skills - existing_skills
    deleted_skills = existing_skills - current_skills
    for created_skill in created_skills:
        service_skill = dbsession.query(
            ServiceSkill
        ).filter(
            ServiceSkill.name == created_skill[0]
        ).all()
        if not service_skill:
            service_skill = ServiceSkill()
            service_skill.service_id = sid
            service_skill.name = created_skill[0]
            service_skill.inspection = created_skill[1]
            dbsession.add(service_skill)
            dbsession.commit()

        sp_skill = ServiceProviderSkill()
        sp_skill.service_skill_id = service_skill.id
        sp_skill.service_provider_id = spid
        dbsession.add(sp_skill)
    if deleted_skills:
        dbsession.query(ServiceProviderSkill).filter(
            #ServiceSkill.service_provider_id == spid,
            ServiceSkill.service_id == sid,
            ServiceSkill.name.in_([skill[0] for skill in deleted_skills]),
            ServiceSkill.id == ServiceProviderSkill.service_skill_id
        ).update({'trash': True}, synchronize_session=False)
        '''
        dbsession.query(ServiceProviderSkill).filter(
            ServiceProviderSkill.service_skill_id == sid
        ).update({'trash':True}, synchronize_session=False)
        '''
    dbsession.commit()


def get_service_provider_skills(dbsession, spid):
    service_provider = dbsession.query(ServiceProvider).filter(
                                    ServiceProvider.id == spid,
                                ).one()
    sp_skills = dbsession.query(ServiceProviderSkill).filter(
                                    ServiceProviderSkill.service_provider_id == spid,
                                    ServiceProviderSkill.trash == False
                                ).all()

    sp_skill_ids = [sp_skill.service_skill_id for sp_skill in sp_skills]
    service_skills = {}
    for skill in service_provider.skills:
        if skill.id in sp_skill_ids:
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
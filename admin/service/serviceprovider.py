
from admin.models import *
from admin import tasks
from admin.service.service import *
from admin.service.user import create_user, update_user
from utils import transaction, update_model_from_dict
from exc import AppException
import config


__all__ = ['update_service_provider', 'get_service_provider',
           'delete_service_provider', 'create_service_provider',
           'get_service_provider_skills', 'fetch_jobs_by_status',
           'get_sp_for_phone_number']

@transaction
def create_service_provider(dbsession, data):
    user_data = {
        'email': data['email'],
        'phone_number': data['phone_number']
    }
    skills = data.pop('skills', [])

    user = create_user(dbsession, user_data)
    service_provider = ServiceProvider()
    service_provider.user_id = user.id
    update_model_from_dict(service_provider, data)
    dbsession.add(service_provider)
    if skills:
        for service_name, service_skills in skills.iteritems():
            service = get_or_create_service(dbsession, service_name)
            sp_service = ServiceProviderService()
            sp_service.service_provider_id = service_provider.id
            sp_service.service_id = service.id
            dbsession.add(sp_service)
            update_skills(dbsession, service_provider.id, service.id, service_skills)


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
    skills = data.pop('skills', [])
    user = data.pop('user', {})
    update_model_from_dict(service_provider, data)
    dbsession.add(service_provider)

    update_user(dbsession, service_provider.user_id, user)

    if skills:
        update_skills(dbsession, service_provider.id, skills)

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


def update_skills(dbsession, spid, skills):
    '''
    current_skills = set([
        (skill['name'], skill['inspection'])
        for skill in skills
    ])
    '''
    existing_skills = dbsession.query(
        ServiceSkill.name, ServiceSkill.inspection, Service.id
    ).filter(
        ServiceProviderSkill.service_provider_id == spid,
        ServiceSkill.id == ServiceProviderSkill.service_skill_id,
        ServiceSkill.trash == False,
        ServiceSkill.service_id == Service.id,
        ServiceProviderSkill.trash == False
    ).all()

    skill_names = [esk.name for esk in existing_skills]

    for service_name, service_skills in skills.iteritems():
        service = get_or_create_service(dbsession, service_name)
        current_skills = set([
            (skill['name'], skill['inspection'])
            for skill in service_skills
        ])
        existing_skills_service = set([(existingskill.name, existingskill.inspection) for existingskill in existing_skills
             if existingskill.id == service.id])
        created_skills = current_skills - existing_skills_service
        deleted_skills = existing_skills_service - current_skills

        for ssk in service_skills:
            if ssk['name'] in skill_names:
                skill_names.remove(ssk['name'])

        for created_skill in created_skills:
            try:
                service_skill = dbsession.query(ServiceSkill).filter(
                    ServiceSkill.name == created_skill[0],
                    ServiceSkill.trash == False
                ).one()
            except Exception as ee:
                service_skill = ServiceSkill()
                service_skill.service_id = service.id
                service_skill.name = created_skill[0]
                service_skill.inspection = created_skill[1]
                dbsession.add(service_skill)

            sp_skill = ServiceProviderSkill()
            sp_skill.service_skill_id = service_skill.id
            sp_skill.service_provider_id = spid
            dbsession.add(sp_skill)


        if deleted_skills:
            dbsession.query(ServiceProviderSkill).filter(
                #ServiceSkill.service_provider_id == spid,
                ServiceSkill.service_id == service.id,
                ServiceSkill.name.in_([skill[0] for skill in deleted_skills]),
                ServiceSkill.id == ServiceProviderSkill.service_skill_id
            ).update({'trash': True}, synchronize_session=False)


    if skill_names:
        dbsession.query(ServiceProviderSkill).filter(
            ServiceProviderSkill.service_provider_id == spid,
            ServiceProviderSkill.service_skill_id == ServiceSkill.id,
            ServiceSkill.name.in_(skill_names)
        ).update({'trash': True}, synchronize_session=False)


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
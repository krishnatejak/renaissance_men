
from admin.models import *
from admin import tasks
from admin.service.user import create_user, update_user
from utils import transaction, update_model_from_dict
from exc import AppException
import config
import constants
import datetime


__all__ = ['update_service_provider', 'get_service_provider',
           'delete_service_provider', 'create_service_provider',
           'fetch_jobs_by_status', 'get_sp_for_phone_number']


def clean_service_provider_skills(skills):
    """sanitizes service provider skills"""
    cleaned_skills = {}
    for service, skills in skills.iteritems():
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
    if 'skills' in data:
        data['skills'] = clean_service_provider_skills(data['skills'])
    update_model_from_dict(service_provider, data)
    dbsession.add(service_provider)

    dbsession.commit()

    tasks.update_service_provider.apply_async(
        args=(service_provider.id,),
        kwargs={'created': True, 'old_start': 0, 'old_end': 0},
        queue=config.SERVICE_PROVIDER_QUEUE
    )
    return service_provider

@transaction
def update_service_provider(dbsession, provider_id, data):
    service_provider = dbsession.query(ServiceProvider).filter(
        ServiceProvider.id == provider_id
    ).one()

    old_start = service_provider.day_start
    old_end = service_provider.day_end

    if 'skills' in data:
        data['skills'] = clean_service_provider_skills(data['skills'])

    user = data.pop('user', {})
    update_model_from_dict(service_provider, data)
    dbsession.add(service_provider)

    update_user(dbsession, service_provider.user_id, user, admin=True)

    dbsession.commit()

    tasks.update_service_provider.apply_async(
        args=(service_provider.id,),
        kwargs={'created': False, 'old_start': old_start, 'old_end': old_end},
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
        ).order_by(ServiceProvider.id.asc())

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


def populate_service_provider_slots(dbsession, redis, spid,
                                    old_start=None, old_end=None, created=False):
    """populates service provider schedule slots in redis"""
    sp = dbsession.query(ServiceProvider).filter(
        ServiceProvider.id == spid,
        ServiceProvider.trash == False
    ).one()
    now = datetime.datetime.now()

    slot_day_start = 0
    if now.hour > constants.SLOT_DAY_END_HOUR:
        slot_day_start = 1
    slot_day_end = constants.SLOT_NO_OF_DAYS
    if now.hour > constants.SLOT_DAY_END_HOUR:
        slot_day_end = constants.SLOT_NO_OF_DAYS + 1

    if created:
        pipeline = redis.pipeline()

        for i in range(slot_day_start, slot_day_end):
            start = sp.day_start
            end = sp.day_end

            if i == 0:
                current_start = (now.hour * 60 + now.minute)/5
                if current_start > sp.day_start:
                    start = current_start

            slots_schedule = {
                str(slot): str(slot)
                for slot in range(start, end + 1)
            }
            date = (now + datetime.timedelta(days=i)).strftime('%m%d')
            key = 'schedule:{0}:{1}'.format(sp.id, date)
            # delete key
            pipeline.delete(key)
            # add created slots
            pipeline.zadd(key, **slots_schedule)
        pipeline.execute()
    else:
        if not old_start and not old_end:
            raise AppException('Cannot update slots without original slots')
        # slots that should be originally present for sp
        print 'old start %s old end %s' % (old_start, old_end)
        print 'new start %s new end %s' % (sp.day_start, sp.day_end)
        original_slots = set(range(old_start, old_end + 1))
        # slots that should be present for sp now
        new_slots = set(range(sp.day_start, sp.day_end + 1))
        # slots present now that are not present originally
        missing_slots = new_slots - original_slots
        print 'missing_slots %s' % missing_slots
        pipeline = redis.pipeline()
        for i in range(slot_day_start, slot_day_end):
            date = (now + datetime.timedelta(days=i)).strftime('%m%d')
            key = 'schedule:{0}:{1}'.format(sp.id, date)
            # slots for sp remaining in that day (missing slots
            # can be expired or booked)
            actual_slots = set(redis.zrangebyscore(key, 0, 289))
            # slots remaining for sp from original slots
            booked_slots = original_slots - actual_slots
            print 'booked_slots %s' % booked_slots
            # slots that needs to be added for sp
            added_slots = missing_slots - booked_slots
            print 'slots to be added %s' % added_slots
            if added_slots:
                print 'found added slots %s' % added_slots
                slots = {str(slot): str(slot) for slot in added_slots}
                pipeline.zadd(key, **slots)
            # remove all other slots
            pipeline.zremrangebyscore(key, 0, sp.day_start - 1)
            pipeline.zremrangebyscore(key, sp.day_end + 1, 289)
        pipeline.execute()
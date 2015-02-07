from datetime import datetime

from admin.models import Job
from utils import update_model_from_dict, transaction
from admin.service.user import create_user, get_user
from utils import generate_secret, parse_json_datetime
from exc import AppException
from admin import tasks
import config

__all__ = ['create_job', 'get_job', 'set_job_ended', 'set_job_started', 'set_job_accepted', 'set_job_rejected']

@transaction
def create_job(dbsession, data):
    job = Job()
    data['service_id'] = data.pop('service_id')
    data['service_provider_id'] = data.pop('service_provider_id')
    data['appointment_time'] = parse_json_datetime(data['appointment_time'])

    user_id = data.pop('user_id', 0)
    if user_id:
        user = get_user(dbsession, user_id)
    elif data.get('user'):
        user_data = data.pop('user')
        user = create_user(dbsession, user_data)
    else:
        raise AppException('User id or user data required to create job')
    data['user'] = user

    update_model_from_dict(job, data)
    dbsession.add(job)
    dbsession.commit()

    tasks.create_job.apply_async(
        (job.id,),
        queue=config.JOB_QUEUE
    )

    return job


def get_job(dbsession, jid):
    job = dbsession.query(Job).filter(Job.id == jid).one()
    return job


@transaction
def set_job_started(dbsession, jid):
    job = dbsession.query(Job).filter(Job.id == jid).one()
    if job.started:
        raise AppException('Cannot start started job')
    job.started = datetime.utcnow()
    job.status = 'started'
    dbsession.add(job)
    dbsession.commit()

    tasks.job_started.apply_async(
        job.id,
        queue=config.JOB_QUEUE
    )


@transaction
def set_job_ended(dbsession, jid):
    job = dbsession.query(Job).filter(Job.id == jid).one()
    if job.ended:
        raise AppException('Cannot end ended job')
    job.ended = datetime.utcnow()
    job.status = 'complete'
    dbsession.add(job)
    dbsession.commit()

    tasks.job_complete.apply_async(
        job.id,
        queue=config.JOB_QUEUE
    )

@transaction
def set_job_accepted(dbsession, jid):
    job = dbsession.query(Job).filter(Job.id == jid).one()
    if job.ended:
        raise AppException('Cannot end ended job')
    job.ended = datetime.utcnow()
    job.status = 'accepted'
    dbsession.add(job)
    dbsession.commit()

    tasks.job_complete.apply_async(
        job.id,
        queue=config.JOB_QUEUE
    )

@transaction
def set_job_rejected(dbsession, jid):
    job = dbsession.query(Job).filter(Job.id == jid).one()
    if job.ended:
        raise AppException('Cannot end ended job')
    job.ended = datetime.utcnow()
    job.status = 'rejected'
    dbsession.add(job)
    dbsession.commit()

    tasks.job_complete.apply_async(
        job.id,
        queue=config.JOB_QUEUE
    )

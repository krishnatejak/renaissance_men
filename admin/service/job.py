from datetime import datetime

from admin.models import Job
from utils import update_model_from_dict, transaction
from admin.service.user import create_user, get_user
from utils import generate_secret
from exc import AppException

__all__ = ['create_job', 'get_job', 'set_job_ended', 'set_job_started']

@transaction
def create_job(dbsession, data):
    job = Job()
    data['service_id'] = data.pop('service')
    data['service_provider_id'] = data.pop('service_provider')
    user_id = data.pop('user', -1)
    try:
        user = get_user(dbsession, user_id)
    except:
        user = create_user(dbsession, {
            'name': data.pop('name'),
            'address': data.pop('address'),
            'phone_number': data.pop('phone_number'),
            'email': data.pop('email'),
            'location': data['location'],
            'password': generate_secret()
        })
    data['user'] = user
    update_model_from_dict(job, data)
    dbsession.add(job)
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
    dbsession.add(job)
    #TODO send message to sp/user indicating job started

@transaction
def set_job_ended(dbsession, jid):
    job = dbsession.query(Job).filter(Job.id == jid).one()
    if job.ended:
        raise AppException('Cannot end ended job')
    job.ended = datetime.utcnow()
    dbsession.add(job)
    #TODO send message to sp/uer indicating job ended
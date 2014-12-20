from background import celery
from background import DBTask
from admin.models import ServiceProvider
import config
import pyotp


@celery.task(name='admin.serviceprovider.add', base=DBTask, bind=True)
def add_service_provider(self, spid):
    pass


@celery.task(name='admin.serviceprovider.update', base=DBTask, bind=True)
def update_service_provider(self, spid):
    pass


@celery.task(name='admin.serviceprovider.delete', base=DBTask, bind=True)
def delete_service_provider(self, spid):
    pass


@celery.task(name='admin.serviceprovider.verify', base=DBTask, bind=True)
def verify_service_provider(self, spid):
    service_provider = self.db.query(ServiceProvider).query(
        ServiceProvider.id == spid
    ).one()

    count = self.r.incr('otp:count')
    self.r.redisdb.set('otp:' + spid, count)
    hotp = pyotp.HOTP(config.OTP_SECRET)
    otp = hotp.at(count)

    #TODO send OTP sms to service provider phone number


@celery.task(name='admin.job.create', base=DBTask, bind=True)
def create_job(self, jid):
    pass


@celery.task(name='admin.job.started', base=DBTask, bind=True)
def job_started(self, jid):
    pass


@celery.task(name='admin.job.complete')
def job_complete(self, jid):
    pass


@celery.task(name='admin.user.create')
def user_create(name, user_name, email, password):
    pass


@celery.task(name='admin.service.add', base=DBTask, bind=True)
def add_service(self, sid):
    pass

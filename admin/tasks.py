import pyotp

from background import celery
from background import DBTask
from admin.models import *
import config
from admin.service.sms import OtpSms


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
    service_provider = self.db.query(ServiceProvider).filter(
        ServiceProvider.id == spid
    ).one()

    count = self.r.incr('otp:count')
    self.r.set('otp:' + spid, count)
    hotp = pyotp.HOTP(config.OTP_SECRET)
    otp = hotp.at(count)

    otp_sms = OtpSms(service_provider.phone_number, otp)
    otp_sms.send_sms()


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
    service = self.db.query(Service).filter(
        Service.id == sid
    )

    self.r.sadd('services', service.name)

@celery.task(name='admin.add.all', base=DBTask, bind=True)
def admin_add_all(self):
    services = self.db.query(Service.name).filter(
        Service.trash == False
    ).all()

    self.r.sadd('services', [service[0] for service in services])

    service_skills = self.db.query(
        ServiceSkill.name, Service.name, ServiceSkill.service_provider_id
    ).filter(
        ServiceSkill.trash == False, ServiceSkill.service_id == Service.id,
        Service.trash == False
    ).all()
    for service_skill, service_name, service_provider_id in service_skills:
        self.r.sadd("{0}:skills".format(service_name), service_skill)
        self.r.sadd("{0}:providers".format(service_name),service_provider_id)
        self.r.sadd("sp:{0}:skills".format(service_provider_id),service_skill)

    service_providers = self.db.query(
        ServiceProvider
    ).filter(
        ServiceProvider.trash == False
    ).all()
    for service_provider in service_providers:
        sp_dict = {
            "name":service_provider.name,
            "availability":service_provider.availability,
            "phone_number":service_provider.phone_number,
            "home_location":service_provider.home_location,
            "office_location":service_provider.office_location,
            "service_range":service_provider.service_range
            }
        self.r.hmset("sp:{0}".format(service_provider.id),sp_dict)


import pyotp
import gcmclient

from background import celery
from background import DBTask
from admin.models import *
import config
from admin.service.sms import Sms

@celery.task(name='admin.serviceprovider.add', base=DBTask, bind=True)
def add_service_provider(self, spid):
    service_provider = self.db.query(ServiceProvider).filter(
        ServiceProvider.id == spid, ServiceProvider.trash == False
    ).first()
    skills = service_provider.skills

    for skill in skills:
        self.r.sadd("{0}:providers".format(skill.service.name), spid)
        self.r.sadd("sp:{0}:{1}:skills".format(spid, skill.service.name), skill.name)

    sp_dict = {
        "name":service_provider.name,
        "availability":service_provider.availability,
        "phone_number":service_provider.phone_number,
        "home_location":service_provider.home_location,
        "office_location":service_provider.office_location,
        "service_range":service_provider.service_range
        }
    self.r.hmset("sp:{0}".format(service_provider.id),sp_dict)



@celery.task(name='admin.serviceprovider.update', base=DBTask, bind=True)
def update_service_provider(self, spid):
    service_provider = self.db.query(ServiceProvider).filter(
        ServiceProvider.trash == False, ServiceProvider.id == spid
    ).first()

    service_dict = {}

    skills = service_provider.skills

    for skill in skills:
        service_name = skill.service.name
        self.r.sadd("{0}:providers".format(service_name), spid)
        self.r.sadd("sp:{0}:{1}:skills".format(spid, service_name), skill.name)

        if service_dict.get(service_name):
            service_dict[service_name].append(skill.name)
        else:
            service_dict[service_name] = [skill.name]

    for key in service_dict:
        redis_skills = self.r.smembers("sp:{0}:{1}:skills".format(spid, key))
        db_skills = set(service_dict.get(key))
        deleted_skills = redis_skills - db_skills
        if deleted_skills:
            self.r.srem("sp:{0}:{1}:skills".format(spid, key),*deleted_skills)

    sp_dict = {
        "name":service_provider.name,
        "availability":service_provider.availability,
        "phone_number":service_provider.phone_number,
        "home_location":service_provider.home_location,
        "office_location":service_provider.office_location,
        "service_range":service_provider.service_range
        }
    self.r.hmset("sp:{0}".format(service_provider.id),sp_dict)

@celery.task(name='admin.serviceprovider.delete', base=DBTask, bind=True)
def delete_service_provider(self, spid):
    service_provider = self.db.query(ServiceProvider).filter(
        ServiceProvider.trash == False, ServiceProvider.id == spid
    ).first()

    for skill in service_provider.skills:
        service_name = skill.service.name

        self.r.srem("{0}:providers".format(service_name), spid)
        self.r.spop("sp:{0}:{1}:skills".format(spid, service_name))

    sp_dict = self.r.hgetall("sp:{0}".format(spid))
    self.r.hdel("sp:{0}".format(spid), *sp_dict)

@celery.task(name='admin.serviceprovider.verify', base=DBTask, bind=True)
def verify_service_provider(self, spid):
    service_provider = self.db.query(ServiceProvider).filter(
        ServiceProvider.id == spid
    ).one()

    count = self.r.incr('otp:count')
    self.r.set('otp:' + str(spid), count)
    hotp = pyotp.HOTP(config.OTP_SECRET)
    otp = hotp.at(count)

    otp_sms = Sms(service_provider.phone_number, "OTP for registration with Sevame is " + str(otp))
    otp_sms.send_sms()


@celery.task(name='admin.job.create', base=DBTask, bind=True)
def create_job(self, jid):
    pass


@celery.task(name='admin.job.started', base=DBTask, bind=True)
def job_started(self, jid):
    pass


@celery.task(name='admin.job.complete', base=DBTask, bind=True)
def job_complete(self, jid):
    pass

@celery.task(name='admin.job.rejected', base=DBTask, bind=True)
def job_rejected(self, jid):
    pass


@celery.task(name='admin.job.accepted', base=DBTask, bind=True)
def job_accepted(self, jid):
    pass


@celery.task(name='admin.user.create')
def user_create(uid):
    pass

@celery.task(name='admin.service.add', base=DBTask, bind=True)
def add_service(self, sid):
    service = self.db.query(Service).filter(Service.id == sid).first()

    self.r.sadd('services', service.name)

    for skill in service.skills:
        self.r.sadd("{0}:skills".format(service.name), skill.name)

@celery.task(name='admin.add.all', base=DBTask, bind=True)
def admin_add_all(self):
    services = self.db.query(Service).filter(Service.trash == False).all()

    self.r.delete("services")
    for service in services:
        self.r.delete("{0}.providers".format(service.name))
        self.r.delete("{0}.skills".format(service.name))

        self.r.sadd('services', service.name)

        for skill in service.skills:
            self.r.sadd("{0}:skills".format(service.name), skill.name)

    service_providers = self.db.query(ServiceProvider).filter(ServiceProvider.trash == False).all()

    for service_provider in service_providers:
        skills = service_provider.skills

        for skill in skills:
            service_name = skill.service.name
            self.r.sadd("{0}:providers".format(service_name), service_provider.id)
            self.r.sadd("sp:{0}:{1}:skills".format(service_provider.id, service_name), skill.name)

        sp_dict = {
            "name":service_provider.name,
            "availability":service_provider.availability,
            "phone_number":service_provider.phone_number,
            "home_location":service_provider.home_location,
            "office_location":service_provider.office_location,
            "service_range":service_provider.service_range
        }

        self.r.delete("sp:{0}".format(service_provider.id))
        self.r.hmset("sp:{0}".format(service_provider.id), sp_dict)

@celery.task(name='admin.notify.gcm')
def admin_notify_gcm(msg, *gcm_reg_ids):
    gcm = gcmclient.GCM(config.GOOGLE_GCM_API_KEY)
    multicast_msg = gcmclient.JSONMessage(gcm_reg_ids, msg)
    gcm.send(multicast_msg)

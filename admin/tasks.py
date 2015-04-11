import pyotp
import gcmclient
import datetime
import json

from background import celery
from background import DBTask
from admin.models import *
import config
import constants
from admin.service.sms import Sms
from admin.service import email as email

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
    self.r.hmset("sp:{0}".format(service_provider.id), sp_dict)


@celery.task(name='admin.serviceprovider.update', base=DBTask, bind=True)
def update_service_provider(self, spid, old_start=None, old_end=None, created=False):
    from admin.service.serviceprovider import populate_service_provider_slots

    sp = self.db.query(ServiceProvider).filter(
        ServiceProvider.id == spid,
        ServiceProvider.trash == False
    ).one()

    service_skills = sp.skills
    # populate redis entries
    for service, skills in service_skills.iteritems():
        # add service provider to <service>:providers set
        self.r.sadd("service:{0}:sp".format(service), spid)

        # update service provider service skills sp:<id>:<service>:skills
        current_skills = set([skill['name'] for skill in skills])
        existing_skills = self.r.smembers(
            "sp:{0}:{1}:skills".format(spid, service)
        )
        deleted_skills = list(existing_skills - current_skills)
        if deleted_skills:
            print 'deleted skills %s' % deleted_skills
            self.r.srem(
                "sp:{0}:{1}:skills".format(spid, service),
                *deleted_skills
            )
        added_skills = list(current_skills - existing_skills)
        if added_skills:
            print 'added skills %s' % added_skills
            self.r.sadd(
                "sp:{0}:{1}:skills".format(spid, service),
                *added_skills
            )
        # update availability in <service>:availability:sps
        availability = 1 if sp.availability else 0
        kwargs = {str(spid): availability}
        self.r.zadd(
            "{0}:availability:sps".format(service),
            **kwargs
        )

    # update service provider data in sp:<id>
    sp_dict = {
        "name": sp.user.name,
        "availability": sp.availability,
        "phone_number": sp.user.phone_number,
        "home_location": sp.home_location,
        "office_location": sp.office_location,
        "service_range": sp.service_range
        }
    self.r.hmset("sp:{0}".format(sp.id), sp_dict)

    # update schedule slots in schedule:<id>:<mmdd>
    populate_service_provider_slots(
        self.db, self.r, spid,
        created=created, old_start=old_start, old_end=old_end
    )

@celery.task(name='admin.serviceprovider.delete', base=DBTask, bind=True)
def delete_service_provider(self, spid):
    service_provider = self.db.query(ServiceProvider).filter(
        ServiceProvider.trash == False, ServiceProvider.id == spid
    ).first()

    for skill in service_provider.skills:
        service_name = skill.service.name

        self.r.srem("{0}:providers".format(service_name), spid)
        self.r.srem("services:{0}:sps", spid)
        self.r.spop("sp:{0}:{1}:skills".format(spid, service_name))

    sp_dict = self.r.hgetall("sp:{0}".format(spid))
    self.r.hdel("sp:{0}".format(spid), *sp_dict)

@celery.task(name='admin.user.phone.verify', base=DBTask, bind=True)
def verify_user_phone(self, uid):
    user = self.db.query(BaseUser).filter(
        BaseUser.id == uid
    ).one()

    count = self.r.incr('otp:count')
    self.r.set('otp:' + str(uid), count)
    hotp = pyotp.HOTP(config.OTP_SECRET)
    otp = hotp.at(count)

    kwargs = {
        "to_number": str(user.phone_number),
        "body": "OTP for registration with Sevame is " + str(otp)
    }

    otp_sms = Sms(**kwargs)
    otp_sms.send_sms()

@celery.task(name='admin.order.created', base=DBTask, bind=True)
def post_order_creation(self, spid, slot_start, order_id):
    phone_number = self.db.query(BaseUser.phone_number).filter(
        ServiceProvider.id == spid,
        ServiceProvider.user_id == BaseUser.id,

    ).one()
    order = self.db.query(Orders).filter(
        Orders.id == order_id
    ).one()
    customer = self.db.query(BaseUser.phone_number, BaseUser.name, BaseUser.email).filter(
        ServiceUser.id == order.service_user_id,
        BaseUser.id == ServiceUser.user_id
    ).one()
    slot_start = slot_start.strftime('%B %d %I:%M %p')
    message = '{service} pickup at {time} at {address}. Order {order_id}.Phone number:{phone_number}, Name:{name}'.\
                                    format(
                                        service=order.service,
                                        time=slot_start,
                                        order_id=order_id,
                                        address=order.address,
                                        phone_number=customer.phone_number,
                                        name=customer.name
                                    )
    kwargs = {
        "to_number": str(phone_number.phone_number),
        "body": message
    }
    sp_sms = Sms(**kwargs)
    sp_sms.send_sms()

    #Email sending
    if order.service == 'laundry':
        scheduled_date = order.scheduled
        date = '{0}-{1} on {2}'.format(
            scheduled_date.strftime('%H:%M'),
            (scheduled_date + datetime.timedelta(minutes=30)).strftime('%H:%M'),
            scheduled_date.strftime('%d-%m-%Y')
        )
        kwargs = {
            'service' : order.service,
            'request' : order.request,
            'order_id': order.id,
            'address' : order.address,
            'phone'   : customer.phone_number,
            'date'    : date,
            'template': 'order_accepted_laundry'
        }
    order_email = email.OrderEmail(customer.email, customer.name, **kwargs)
    order_email.send_email()

@celery.task(name='admin.order.updated', base=DBTask, bind=True)
def post_order_update(self, order_id):
    order = self.db.query(Orders).filter(
        Orders.id == order_id
    ).one()
    customer = self.db.query(BaseUser.name, BaseUser.email).filter(
        ServiceUser.id == order.service_user_id,
        BaseUser.id == ServiceUser.user_id
    ).one()
    #Sending email for order updated
    #TODO integrate PAYU
    send_email = False
    if order.status == 'processing':
        if order.service == 'laundry':
            kwargs = {
                'details' : json.dumps(order.details),
                'template': 'laundry_picked',
                'service' : order.service,
                'link'    : 'link'
            }
            send_email = True
        elif order.service in ['plumber', 'electrician']:
            sp = self.db.query(ServiceProvider).filter(
                ServiceProvider.id == order.service_provider_id,
                ServiceProvider.trash == False
            )
            kwargs = {
                'service' : order.service,
                'order_id': order_id,
                'sp_name' : sp.name,
                'details' : json.dumps(order.details),
                'link'    : 'link',
                'template': 'order_quote_others'
            }
            send_email = True
    elif order.status == 'completed':
        kwargs = {
            'template': 'feedback',
            'service' : order.service,
            'order_id': order_id,
            'user_id' : order.service_user_id
         }
        send_email = True
    elif order.status == 'confirmed':
        sp = self.db.query(ServiceProvider).filter(
                ServiceProvider.id == order.service_provider_id,
                ServiceProvider.trash == False
            )
        kwargs = {
            'service' : order.service,
            'order_id': order_id,
            'sp_name' : sp.name,
            'sp_image': sp.details['photo_link'] if sp.details and sp.detals.get('photo_link') else
                        constants.DEFAULT_SP_IMAGE,
            'template': 'order_assigned_others',
            'sp_ph_no': sp.user.phone_number,
            'experience': sp.experience
        }
        send_email = True
    if send_email:
        order_email = email.OrderEmail(customer.email, customer.name, **kwargs)
        order_email.send_email()

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


@celery.task(name='admin.add.all', base=DBTask, bind=True)
def admin_add_all(self):
    pass


@celery.task(name='admin.notify.gcm')
def admin_notify_gcm(msg, *gcm_reg_ids):
    gcm = gcmclient.GCM(config.GOOGLE_GCM_API_KEY)
    multicast_msg = gcmclient.JSONMessage(gcm_reg_ids, msg)
    gcm.send(multicast_msg)


@celery.task(name='admin.scheduler.populate', base=DBTask, bind=True)
def populate_schedules(self):
    service_providers = self.db.query(ServiceProvider).filter(
        ServiceProvider.trash == False
    ).all()
    now = datetime.datetime.now()
    date = (now + datetime.timedelta(days=3)).strftime('%m%d')

    # only next day slot should be created
    for sp in service_providers:
        pipeline = self.r.pipeline()
        key = 'schedule:{0}:{1}'.format(sp.id, date)
        slots = {
            str(slot): str(slot)
            for slot in range(sp.day_start, sp.day_end + 1)
        }
        pipeline.zadd(key, **slots)
    pipeline.execute()


@celery.task(name='admin.scheduler.clean', base=DBTask, bind=True)
def clean_schedules(self):
    """runs every five minutes and removes the expired 5min slot"""
    now = datetime.datetime.now()
    interval = (now.hour * 60 + now.minute)/5 - 1
    now = now.strftime('%m%d')
    spids = self.db.query(ServiceProvider.id).filter(
        ServiceProvider.trash == False
    )

    spids = zip(*spids)[0]
    pipe = self.r.pipeline()
    for spid in spids:
        pipe.zremrangebyscore("schedule:{0}:{1}".format(spid, now), 0, interval)
    pipe.execute()

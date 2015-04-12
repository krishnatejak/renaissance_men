from admin.models import BaseUser, ServiceProvider, ServiceUser
from utils import update_model_from_dict
from utils import transaction
from exc import AppException
from admin import tasks
import config
import pyotp

from sqlalchemy.orm.exc import NoResultFound

__all__ = ['create_user', 'get_user', 'handle_user_authentication',
           'verify_otp', 'update_user', 'get_admin_users']

BASE_USER_UPDATE_IGNORE = ('verified',)

@transaction
def create_user(dbsession, data):
    user = BaseUser()
    if user_exists(dbsession, data['email']):
        raise AppException('User already exists')
    if 'phone_number' in data:
        if phone_number_exists(dbsession, data['phone_number']):
            raise AppException('Phone number exists')
    update_model_from_dict(user, data)
    dbsession.add(user)
    dbsession.commit()

    tasks.user_create.apply_async(
        (user.id,),
        queue=config.USER_QUEUE
    )

    return user

@transaction
def update_user(dbsession, uid, data, admin=False):
    user = dbsession.query(BaseUser).filter(
        BaseUser.id == uid
    ).one()
    phone_number_changed = False
    if 'phone_number' in data and data['phone_number'] != user.phone_number:
        if phone_number_exists(dbsession, data['phone_number']):
            raise AppException('Phone number exists')
        phone_number_changed = True

    # remove all data that should be ignored
    if not admin:
        for field in BASE_USER_UPDATE_IGNORE:
            data.pop(field, None)

    update_model_from_dict(user, data)

    dbsession.add(user)
    dbsession.commit()
    # if phone number is changed initiated verification
    if phone_number_changed and user.phone_number:
        user.verified = False
        tasks.verify_user_phone.apply_async(
            (user.id,),
            queue=config.USER_QUEUE
    )
    return user

def get_user(dbsession, user_id):
    return dbsession.query(BaseUser).filter(BaseUser.id == user_id).one()


def user_exists(dbsession, email):
    user_count = dbsession.query(BaseUser.id).filter(BaseUser.email == email).count()
    return user_count > 0


def handle_user_authentication(dbsession, user_dict, user_type):
    try:
        user = dbsession.query(BaseUser).filter(
            BaseUser.email == user_dict['email'],
        ).one()
    except NoResultFound:
        user = create_user(dbsession, {
            'email': user_dict['email']
        })

    if user_type == 'service_provider':
        try:
            service_provider = dbsession.query(ServiceProvider).filter(
                ServiceProvider.user_id == user.id
            ).one()
        except NoResultFound:
            service_provider = ServiceProvider()
            service_provider.user = user
            dbsession.add(service_provider)
            dbsession.commit()
            tasks.update_service_provider.apply_async(
                args=(service_provider.id,),
                kwargs={'created': True, 'old_start': 0, 'old_end': 0},
                queue=config.SERVICE_PROVIDER_QUEUE
            )
        return service_provider
    elif user_type == 'service_user':
        try:
            service_user = dbsession.query(ServiceUser).filter(
                ServiceUser.user_id == user.id
            ).one()
        except NoResultFound:
            service_user = ServiceUser()
            service_user.user = user
            dbsession.add(service_user)
            dbsession.commit()
        return service_user
    elif user_type == 'admin':
        if not user.admin:
            raise AppException('User is not admin')
        return user


def verify_otp(dbsession, redisdb, uid, token):
    user = dbsession.query(BaseUser).filter(
        ServiceProvider.id == uid
    ).one()
    count = redisdb.get('otp:' + uid)
    if count:
        count = int(count)
    else:
        raise AppException('No active verification in progress')
    otp = pyotp.HOTP(config.OTP_SECRET)
    if otp.verify(token, count):
        user.verified = True
        dbsession.add(user)
        dbsession.commit()
        redisdb.delete('otp:' + str(uid))
    else:
        raise AppException('OTP verification failed')


def make_admin(dbsession, email):
    user = dbsession.query(BaseUser).filter(
        BaseUser.email == email
    ).one()

    user.admin = True
    dbsession.add(user)
    dbsession.commit()


def phone_number_exists(dbsession, phone_number):
    """returns true if phone number exists, false otherwise"""
    count = dbsession.query(BaseUser.phone_number).filter(
        BaseUser.phone_number == phone_number
    ).count()

    return count > 0


def get_admin_users(dbsession, uid=None):
    if uid:
        user = dbsession.query(BaseUser).filter(
            BaseUser.id == uid
        ).one()
    else:
        user = dbsession.query(BaseUser).all()
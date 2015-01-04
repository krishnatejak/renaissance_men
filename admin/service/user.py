from admin.models import User
from utils import update_model_from_dict
from utils import transaction
from exc import AppException
from admin import tasks
import config


@transaction
def create_user(dbsession, data):
    user = User()
    if user_exists(dbsession, data['email']):
        raise AppException('User already exists')
    update_model_from_dict(user, data)
    dbsession.add(user)
    dbsession.commit()

    tasks.user_create.apply_async(
        user.id,
        queue=config.USER_QUEUE
    )

    return user


def get_user(dbsession, user_id):
    return dbsession.query(User).filter(User.id == user_id).one()


def user_exists(dbsession, email):
    user_count = dbsession.query(User.id).filter(User.email == email).count()
    return user_count > 0


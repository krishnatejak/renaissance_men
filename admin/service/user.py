from admin.models import User
from utils import update_model_from_dict
from utils import transaction


@transaction
def create_user(dbsession, data):
    user = User()
    update_model_from_dict(user, data)
    dbsession.add(user)
    #TODO send user creation email in background
    return user


def get_user(dbsession, user_id):
    return dbsession.query(User).filter(User.id == user_id).one()
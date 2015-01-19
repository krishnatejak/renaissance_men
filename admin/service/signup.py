from utils import update_model_from_dict, transaction
from admin.models import Signupemail
from sqlalchemy import func

@transaction
def save_signup_email(dbsession, email_address):
    try:
        signupemail = dbsession.query(Signupemail).filter(Signupemail.email == func.lower(email_address)).one()
    except:
        signupemail = Signupemail()
        signupemail.email = func.lower(email_address)
        dbsession.add(signupemail)
        dbsession.commit()

    return signupemail
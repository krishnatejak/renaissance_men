from utils import update_model_from_dict, transaction
from admin.models import Signupemail
from sqlalchemy import func

@transaction
def save_signup_email(dbsession, email_address, feedback=None):
    try:
        signupemail = dbsession.query(Signupemail).filter(Signupemail.email == func.lower(email_address)).one()
        signupemail.feedback = feedback
    except:
        signupemail = Signupemail()
        signupemail.email = func.lower(email_address)
        signupemail.feedback = feedback
    dbsession.add(signupemail)
    dbsession.commit()

    return signupemail
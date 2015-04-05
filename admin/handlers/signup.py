import json

from admin.handlers.common import BaseHandler
from admin.service.signup import *
from exc import handle_exceptions

__all__ = ['SignupHandler']


class SignupHandler(BaseHandler):
    resource_name = 'signup'
    create_required = {'email'}

    @handle_exceptions
    def post(self):
        data = self.check_input('create')
        signupemail = save_signup_email(self.dbsession, data['email'],
                                        feedback=data.get('feedback'))
        email_dict = {
            "email": signupemail.email,
            "feedback": signupemail.feedback
        }
        self.set_status(200)
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(email_dict))
        self.finish()
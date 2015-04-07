import sendgrid
import config as config
import constants as constants

from admin.templates.order_accepted_laundry import order_accepted_laundry
from admin.templates.base_template import base_template

class EmailService(object):
    def __init__(self, *args, **kwargs):
        self.host_user = config.EmailUserName
        self.host_pass = config.EmailUserPasswd
        self.from_email = constants.SUPPORT_EMAIL_ADDRESS if not kwargs.get(
            'from_email') else kwargs.get('from_email')
        self.to_email = kwargs.get('email')
        self.subject = kwargs.get('subject')
        self.first_name = kwargs.get('first_name')
        self.cc_email = kwargs.get('cc_email')
        self.bcc_email = kwargs.get('bcc_email')
        self.html = None
        self.text = None

    def generate_email_body(self):
        """
        this function should be implemented in subclasses and
        set self.html and self.text
        """
        raise NotImplementedError

    def send_email(self):
        try:
            self.generate_email_body()
            s = sendgrid.SendGridClient(self.host_user, self.host_pass)
            message = sendgrid.Mail()
            message.set_from(self.from_email)
            message.set_subject(self.subject)
            message.set_html(self.html)
            message.set_text(self.text)
            if len(self.to_email.split(',')) > 1:
                to_list = self.to_email.split(',')
                message.add_to(self.to_email)
            else:
                print 'self.to_email() %s' %self.to_email
                message.add_to(self.to_email)
            if self.bcc_email:
                bcc_list = self.bcc_email.split(',')
                message.add_bcc(self.bcc_email)
            if self.cc_email:
                cc_list = self.cc_email.split(',')
                message.add_cc(self.cc_email)
            s.send(message)
        except Exception as e:
            raise e

class OrderEmail(EmailService):
    def __init__(self, email, first_name, **kwargs):
        self.signup_email = kwargs.get('signup_email')
        self.service = kwargs['service']
        if self.service == 'laundry':
            self.request = kwargs['request']
            self.order_id = kwargs['order_id']
            self.address = kwargs['address']
            self.phone = kwargs['phone']
            self.date = kwargs['date']

        super(OrderEmail, self).__init__(
                                            email=email,
                                            first_name=first_name,
                                            subject=constants.ORDER_ACCEPTED_SUBJECT
                                        )

    def generate_email_body(self):
            if self.service == 'laundry':
                template_content = order_accepted_laundry.format(
                    customer_name=self.first_name,
                    service=self.service,
                    request=self.request,
                    order_number=self.order_id,
                    pickup_time=self.date,
                    order_address=self.address,
                    phone_number=self.phone
                )

            self.html = base_template.format(template_content=template_content)
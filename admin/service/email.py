import json
import sendgrid
import config as config
import constants as constants

from admin.templates.order_accepted_laundry import order_accepted_laundry
from admin.templates.laundry_picked import table_data, laundry_picked
from admin.templates.base_template import base_template
from admin.templates.feedback_template import feedback_template
from admin.templates.order_quote_others import order_quote_others
from admin.templates.order_assigned_other import order_assigned_others
from admin.templates.order_successfull_others import order_successful_others_template

from utils import calculate_hmac

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
            message.set_from_name('Sevame')
            message.set_subject(self.subject)
            message.set_html(self.html)
            message.set_text(self.text)
            if len(self.to_email.split(',')) > 1:
                to_list = self.to_email.split(',')
                message.add_to(self.to_email)
            else:
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
        self.service = kwargs['service']
        self.template = kwargs['template']
        self.bcc_email = constants.SUPPORT_EMAIL_ADDRESS
        if self.template == 'order_accepted_laundry':
            self.request = kwargs['request']
            self.order_id = kwargs['order_id']
            self.address = kwargs['address']
            self.phone = kwargs['phone']
            self.date = kwargs['date']
            subject = constants.ORDER_ACCEPTED_SUBJECT
        elif self.template == 'laundry_picked':
            self.details = kwargs['details']
            self.link = kwargs['link']
            subject = constants.LAUNDRY_BILL_EMAIL_SUBJECT
        elif self.template == 'feedback':
            self.order_id = kwargs['order_id'],
            if type(self.order_id) == tuple:
                self.order_id = self.order_id[0]
            self.user_id = kwargs['user_id']
            subject = constants.FEEDBACK_SUBJECT
        elif self.template == 'order_quote_others':
            self.order_id = kwargs['order_id']
            if type(self.order_id) == tuple:
                self.order_id = self.order_id[0]
            self.sp_name = kwargs['sp_name']
            self.details = kwargs['details']
            self.link = kwargs['link']
            subject = constants.QUOTE_OTHERS.format(self.service, self.order_id)
        elif self.template == 'order_assigned_others':
            self.order_id = kwargs['order_id']
            self.sp_name = kwargs['sp_name'],
            self.sp_name = self.sp_name[0]
            self.sp_image = kwargs['sp_image'],
            self.sp_image = self.sp_image[0]
            self.sp_ph_no = kwargs['sp_ph_no'],
            self.sp_ph_no = self.sp_ph_no[0]
            self.experience = kwargs['experience']
            subject = constants.SP_ASSIGNED.format(self.sp_name, self.service)
        elif self.template == 'order_successful_others_template':
            self.request = kwargs['request']
            self.order_id = kwargs['order_id']
            self.address = kwargs['address']
            self.phone = kwargs['phone']
            self.date = kwargs['date']
            subject = constants.ORDER_ACCEPTED_SUBJECT

        super(OrderEmail, self).__init__(
                                            email=email,
                                            first_name=first_name,
                                            subject=subject
                                        )

    def generate_email_body(self):
        if self.template == 'order_accepted_laundry':
            template_content = order_accepted_laundry.format(
                customer_name=self.first_name,
                service=self.service,
                request=self.request,
                order_number=self.order_id,
                pickup_time=self.date,
                order_address=self.address,
                phone_number=self.phone
            )
        elif self.template == 'laundry_picked':
            items = json.loads(self.details)['items']
            html_table_data = ""
            bill_amount = 0
            for item in items:
                html_table_data = html_table_data + table_data.format(
                                                                item = item['name'],
                                                                quantity = item['quantity'],
                                                                amount = item['cost']
                                                    )
                bill_amount += int(item['cost'])
            template_content = laundry_picked.format(
                                        customer_name=self.first_name,
                                        table_data = html_table_data,
                                        link = self.link,
                                        bill_amount = bill_amount
                                )
        elif self.template == 'feedback':
            feedback_identifier = "{0}.su.{1}".format(self.order_id, self.user_id)
            feedback_identifier = "{0}.{1}".format(feedback_identifier,calculate_hmac(feedback_identifier))
            template_content = feedback_template.format(
                customer_name=self.first_name,
                service=self.service,
                order_id=self.order_id,
                rating_link=constants.FEEDBACK_LINK,
                order_identity=feedback_identifier
            )
        elif self.template == 'order_quote_others':
            items = json.loads(self.details)['items']
            html_table_data = ""
            bill_amount = 0
            for item in items:
                html_table_data = html_table_data + table_data.format(
                                                                item = item['name'],
                                                                quantity = item['quantity'],
                                                                amount = item['cost']
                                                    )
                bill_amount += int(item['cost'])
            template_content = order_quote_others.format(
                customer_name=self.first_name,
                service=self.service,
                order_id=self.order_id,
                sp_name=self.sp_name,
                table_data=html_table_data,
                link=self.link
            )
        elif self.template == 'order_assigned_others':
            template_content = order_assigned_others.format(
                customer_name=self.first_name,
                service=self.service,
                order_id=self.order_id,
                sp_name=self.sp_name,
                sp_ph_no=self.sp_ph_no,
                sp_experience=self.experience,
                sp_image=self.sp_image
            )
        elif self.template == 'order_successful_others_template':
            template_content = order_successful_others_template.format(
                customer_name=self.first_name,
                service=self.service,
                request=self.request,
                order_id=self.order_id,
                pickup_time=self.date,
                order_address=self.address,
                phone_number=self.phone
            )
        self.html = base_template.format(template_content=template_content)
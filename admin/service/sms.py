from twilio.rest import TwilioRestClient
import config


class Sms(object):
    def __init__(self,*args, **kwargs):
        self.account_sid = config.TWILIO_ACCOUNT_SID
        self.auth_token = config.TWILIO_AUTH_TOKEN
        self.from_number = config.TWILIO_FROM_NUMBER
        self.body = kwargs.get('body')
        to_number = kwargs.get('to_number')
        if len(kwargs.get('to_number')) == 10:
            to_number = "+91" + kwargs.get('to_number')

        self.to_number = to_number

    def send_sms(self):
        try:
            client = TwilioRestClient(self.account_sid, self.auth_token)

            response = client.messages.create(body=self.body, to=self.to_number, from_=self.from_number)
        except Exception as e:
            print 'e is %s' %e


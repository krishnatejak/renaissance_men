from twilio.rest import TwilioRestClient
import config


class Sms(object):
    def __init__(self,*args, **kwargs):
        self.account_sid = config.TWILIO_ACCOUNT_SID
        self.auth_token = config.TWILIO_AUTH_TOKEN
        self.from_number = config.TWILIO_FROM_NUMBER
        self.body = args[1]
        to_number = args[0]

        if len(self.from_number) == 10:
            to_number = "+91" + kwargs.get('to_number')

        self.to_number = to_number

    def send_sms(self):
        try:
            client = TwilioRestClient(self.account_sid, self.auth_token)

            response = client.messages.create(body=self.body, to=self.to_number, from_=self.from_number)
        except Exception as e:
            print 'e is %s' %e


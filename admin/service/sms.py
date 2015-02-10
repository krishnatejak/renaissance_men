from twilio.rest import TwilioRestClient
import config


class Sms(object):
    def __init__(self, to_number, body):
        self.account_sid = config.TWILIO_ACCOUNT_SID
        self.auth_token = config.TWILIO_AUTH_TOKEN
        self.from_number = config.TWILIO_FROM_NUMBER
        self.body = body

        if len(to_number) == 10:
            to_number = "+91" + to_number

        self.to_number = to_number

    def send_sms(self):
        client = TwilioRestClient(self.account_sid, self.auth_token)

        response = client.messages.create(body=self.body, to=self.to_number, from_=self.from_number)
        print(response)

